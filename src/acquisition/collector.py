"""Colector serie para el nodo NAIRA."""

import logging
import time
from datetime import datetime, UTC
from pathlib import Path
from typing import Dict, Optional

import serial
from dotenv import load_dotenv

try:
    from .influx import get_influx_sink
    from .state_store import get_state_store
except ImportError:  # Permite ejecutar "python collector.py" desde src/acquisition
    import sys

    src_root = Path(__file__).resolve().parents[1]
    if str(src_root) not in sys.path:
        sys.path.append(str(src_root))
    from acquisition.influx import get_influx_sink  # type: ignore
    from acquisition.state_store import get_state_store  # type: ignore

try:
    from src.config import load_settings
except ModuleNotFoundError:  # Permite ejecutar "python collector.py"
    import sys

    src_root = Path(__file__).resolve().parents[1]
    if str(src_root) not in sys.path:
        sys.path.append(str(src_root))
    from config import load_settings  # type: ignore

load_dotenv(Path(__file__).resolve().parent / ".env")

logger = logging.getLogger(__name__)

# Configuración por defecto
DEFAULT_PORT = "/dev/ttyACM0"
DEFAULT_BAUDRATE = 9600
DEFAULT_TIMEOUT = 2


class SerialCollector:
    """Recolecta datos del puerto serie en la base de datos."""

    def __init__(self, port: str = DEFAULT_PORT, baudrate: int = DEFAULT_BAUDRATE,
                 node_id: str = "naira-node-001"):
        """Inicializa el colector.
        
        Args:
            port: Puerto serie (ej: /dev/ttyACM0)
            baudrate: Velocidad en baudios
            node_id: ID del nodo
        """
        self.settings = load_settings()
        self.port = port
        self.baudrate = baudrate
        self.node_id = node_id or getattr(self.settings, "node_id", "naira-node-001")
        self.influx = get_influx_sink()
        self.state_store = get_state_store()
        self.retry_interval_s = getattr(self.settings, "influx_retry_interval_s", 10)
        self.sample_interval_s = max(0, getattr(self.settings, "collector_interval_s", 30))
        self.ser = None
        self.last_values = {}  # Caché de últimos valores

    def connect(self) -> bool:
        """Abre conexión al puerto serie.
        
        Returns:
            True si conecta, False si falla
        """
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=DEFAULT_TIMEOUT)
            logger.info(f"Conectado a {self.port} @ {self.baudrate} baud")
            return True
        except serial.SerialException as e:
            logger.error(f"Error conectando a {self.port}: {e}")
            self.ser = None
            return False

    def disconnect(self) -> None:
        """Cierra conexión al puerto serie."""
        if self.ser and self.ser.is_open:
            self.ser.close()
            logger.info("Desconectado del puerto serie")

    def read_line(self) -> Optional[str]:
        """Lee una línea del puerto serie.
        
        Returns:
            Línea como string o None si timeout/error
        """
        if not self.ser or not self.ser.is_open:
            return None
        
        try:
            line = self.ser.readline().decode("utf-8", errors="ignore").strip()
            return line if line else None
        except Exception as e:
            logger.warning(f"Error leyendo puerto: {e}")
            return None

    def parse_line(self, line: str) -> Optional[Dict]:
        """Parsea línea del Arduino.
        
        Esperado: "sensor_type value"
        Ej: "moisture 800", "light 5.00", "temperature 18.96"
        
        Args:
            line: Línea recibida
            
        Returns:
            Dict con {metric, value, unit} o None si error
        """
        if not line or " " not in line:
            return None
        
        try:
            parts = line.split(" ", 1)
            sensor_type = parts[0].lower()
            value_str = parts[1]
            value = float(value_str)
            
            # Mapeo de tipos de sensores a métrica y unidad
            sensor_map = {
                "moisture": {"metric": "humedad_suelo", "unit": "%", "source": "suelo"},
                "light": {"metric": "luminosidad", "unit": "lux", "source": "meteo"},
                "temperature": {"metric": "temp_aire", "unit": "°C", "source": "meteo"},
            }
            
            if sensor_type not in sensor_map:
                logger.warning(f"Tipo de sensor desconocido: {sensor_type}")
                self._record_event(
                    event_type="unknown_sensor_type",
                    severity="warn",
                    context={"line": line, "sensor_type": sensor_type},
                )
                return None
            
            mapping = sensor_map[sensor_type]
            return {
                "metric": mapping["metric"],
                "value": value,
                "unit": mapping["unit"],
                "source": mapping["source"]
            }
        except ValueError as e:
            logger.warning(f"Error parseando línea '{line}': {e}")
            return None

    def normalize_sample(self, parsed: Dict) -> Dict:
        """Normaliza muestra a estructura estándar.
        
        Args:
            parsed: Dict con {metric, value, unit, source}
            
        Returns:
            Dict normalizado con estructura NAIRA
        """
        return {
            "ts": datetime.now(UTC).isoformat().replace("+00:00", "") + "Z",
            "node_id": self.node_id,
            "source": parsed.get("source", "meteo"),
            "metric": parsed.get("metric"),
            "value": parsed.get("value"),
            "unit": parsed.get("unit"),
            "quality": self._assess_quality(parsed.get("metric"), parsed.get("value"))
        }

    def _assess_quality(self, metric: str, value: float) -> str:
        """Evalúa calidad de la muestra (checks básicos).
        
        Args:
            metric: Tipo de métrica
            value: Valor leído
            
        Returns:
            "ok", "suspect", o "bad"
        """
        # Ranges típicos de validez
        ranges = {
            "temp_aire": (-10, 60),        # °C
            "humedad_suelo": (0, 1023),    # Valor analógico del sensor
            "luminosidad": (0, 1023),      # Valor analógico
        }
        
        if metric not in ranges:
            return "ok"
        
        min_val, max_val = ranges[metric]
        if value < min_val or value > max_val:
            logger.warning(f"Valor fuera de rango para {metric}: {value}")
            self._record_event(
                event_type="sensor_value_out_of_range",
                severity="warn",
                context={"metric": metric, "value": value},
            )
            return "bad"
        
        return "ok"

    def _publish_sample(self, sample: Dict) -> bool:
        if not self.influx or not self.influx.is_ready("telemetry"):
            self._record_event(
                event_type="telemetry_sink_unavailable",
                severity="warn",
                context={"metric": sample.get("metric")},
            )
            self._enqueue_payload(sample, "sink_not_ready")
            return False

        try:
            self.influx.write_sensor_sample(sample)
            return True
        except Exception as exc:  # pragma: no cover - depende de red
            logger.error("Error publicando en Influx: %s", exc)
            self._record_event(
                event_type="telemetry_publish_failed",
                severity="error",
                context={"metric": sample.get("metric"), "error": str(exc)},
            )
            self._enqueue_payload(sample, str(exc))
            return False

    def _enqueue_payload(self, sample: Dict, error_msg: str) -> None:
        if not self.state_store:
            logger.error("State store deshabilitado; muestra perdida (%s)", error_msg)
            return
        payload = {"type": "sensor_sample", "data": sample}
        try:
            row_id = self.state_store.enqueue_payload(payload, kind="telemetry", last_error=error_msg)
            logger.debug("Payload offline registrado id=%s", row_id)
        except Exception as exc:
            logger.error("No se pudo encolar payload offline: %s", exc)

    def _flush_pending_payloads(self, limit: int = 20) -> int:
        if not self.state_store or not self.influx or not self.influx.is_ready("telemetry"):
            return 0
        pending = self.state_store.get_pending_payloads(limit)
        flushed = 0
        for item in pending:
            payload = item.get("payload") or {}
            if payload.get("type") != "sensor_sample":
                self.state_store.mark_payload_error(item["id"], "payload_no_soportado", self.retry_interval_s)
                continue
            sample = payload.get("data")
            if not isinstance(sample, dict):
                self.state_store.mark_payload_error(item["id"], "payload_invalido", self.retry_interval_s)
                continue
            try:
                self.influx.write_sensor_sample(sample)
                self.state_store.mark_payload_sent(item["id"])
                flushed += 1
            except Exception as exc:  # pragma: no cover - depende de red
                logger.warning("Error reenviando payload %s: %s", item["id"], exc)
                self.state_store.mark_payload_error(item["id"], str(exc), self.retry_interval_s)
        if flushed:
            logger.info(f"Reenviadas {flushed} muestras pendientes")
        return flushed

    def _record_event(self, event_type: str, severity: str, context: Optional[Dict] = None) -> None:
        if not self.state_store:
            return
        try:
            self.state_store.log_event(
                {
                    "event_type": event_type,
                    "severity": severity,
                    "context": context or {},
                    "node_id": self.node_id,
                }
            )
        except Exception as exc:
            logger.debug("No se pudo registrar evento %s: %s", event_type, exc)

    def read_and_store_one(self) -> bool:
        """Lee una línea del puerto y la publica (online/offline).
        
        Returns:
            True si se guardó algo, False si no
        """
        line = self.read_line()
        if not line:
            return False
        
        parsed = self.parse_line(line)
        if not parsed:
            return False
        
        normalized = self.normalize_sample(parsed)
        if normalized.get("quality") == "bad":
            self._record_event(
                event_type="sensor_sample_bad_quality",
                severity="warn",
                context={"metric": normalized.get("metric"), "value": normalized.get("value")},
            )

        published = self._publish_sample(normalized)
        metric = normalized.get("metric", "unknown")
        unit = normalized.get("unit", "")
        if published:
            self.last_values[metric] = normalized.get("value")
            logger.info(f"Publicado: {metric}={normalized.get('value')} {unit}")
        else:
            logger.warning(f"Muestra encolada offline: {metric}")
        return published

    def read_and_store_loop(self, count: Optional[int] = None) -> int:
        """Lee N líneas del puerto y las guarda en BD.
        
        Args:
            count: Número de líneas a leer (None = infinito)
            
        Returns:
            Número de muestras guardadas
        """
        if not self.ser or not self.ser.is_open:
            if not self.connect():
                return 0
        
        saved = 0
        i = 0
        
        try:
            self._flush_pending_payloads()
            while count is None or i < count:
                self._flush_pending_payloads()
                if self.read_and_store_one():
                    saved += 1
                i += 1
                if self.sample_interval_s > 0 and (count is None or i < count):
                    time.sleep(self.sample_interval_s)
        except KeyboardInterrupt:
            logger.info("Lectura interrumpida por usuario")
        except Exception as e:
            logger.error(f"Error en bucle de lectura: {e}")
        
        return saved

    def get_last_values(self) -> Dict:
        """Obtiene últimos valores leídos (caché).
        
        Returns:
            Dict con {metric: value, ...}
        """
        return self.last_values.copy()

    def get_state_stats(self) -> Dict:
        """Resumen del almacén de estado/offline."""
        if not self.state_store:
            return {"state_store": "disabled"}
        return self.state_store.get_queue_stats()

    def get_db_stats(self) -> Dict:
        """Compatibilidad hacia atrás con API previa."""
        return self.get_state_stats()


def collect_cli():
    """Función CLI para ejecutar colector en línea de comandos."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Recolecta datos del puerto serie en SQLite"
    )
    parser.add_argument("--port", default=DEFAULT_PORT, help="Puerto serie")
    parser.add_argument("--baudrate", type=int, default=DEFAULT_BAUDRATE, help="Baudrate")
    parser.add_argument("--node-id", default="naira-node-001", help="ID del nodo")
    parser.add_argument("--count", type=int, help="Número de líneas a leer")
    parser.add_argument("--log-level", default="INFO", help="Nivel de log")
    
    args = parser.parse_args()
    
    # Configurar logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    
    # Crear colector
    collector = SerialCollector(
        port=args.port,
        baudrate=args.baudrate,
        node_id=args.node_id
    )
    
    # Conectar y leer
    if collector.connect():
        saved = collector.read_and_store_loop(count=args.count)
        print(f"\n✓ {saved} muestras guardadas")
        print(f"State stats: {collector.get_state_stats()}")
        collector.disconnect()
    else:
        print("✗ No se pudo conectar al puerto serie")


if __name__ == "__main__":
    collect_cli()


__all__ = ["SerialCollector", "collect_cli"]
