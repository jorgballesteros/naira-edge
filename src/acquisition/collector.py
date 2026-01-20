"""
Colector de datos del puerto serie.

Lee datos del Arduino MKR, los parsea, normaliza y guarda en SQLite.
Soporta modo real (hardware) y modo simulado.
"""

import serial
import logging
from datetime import datetime, UTC
from typing import Dict, Optional

from .db import get_database

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
        self.port = port
        self.baudrate = baudrate
        self.node_id = node_id
        self.db = get_database()
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
            return "bad"
        
        return "ok"

    def read_and_store_one(self) -> bool:
        """Lee una línea del puerto y la guarda en BD.
        
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
        
        try:
            self.db.insert_sample(normalized)
            self.last_values[parsed["metric"]] = parsed["value"]
            logger.info(f"Guardado: {parsed['metric']}={parsed['value']} {parsed['unit']}")
            return True
        except Exception as e:
            logger.error(f"Error guardando en BD: {e}")
            return False

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
            while count is None or i < count:
                if self.read_and_store_one():
                    saved += 1
                i += 1
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

    def get_db_stats(self) -> Dict:
        """Obtiene estadísticas de la BD.
        
        Returns:
            Dict con estadísticas
        """
        return self.db.get_stats()


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
        print(f"Stats: {collector.get_db_stats()}")
        collector.disconnect()
    else:
        print("✗ No se pudo conectar al puerto serie")


if __name__ == "__main__":
    collect_cli()


__all__ = ["SerialCollector", "collect_cli"]
