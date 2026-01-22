"""Helper para replicar muestras en InfluxDB.

Centraliza la conexión y escritura contra Influx usando la configuración
expuesta en ``src.config``. Si la librería o los parámetros no están
presentes, el helper queda deshabilitado de forma silenciosa.
"""

from __future__ import annotations

import logging
from datetime import datetime, UTC
from pathlib import Path
from typing import Dict, Iterable, Optional

try:
    from src.config import load_settings
except ModuleNotFoundError:  # Permite ejecutar "python collector.py"
    import sys

    src_root = Path(__file__).resolve().parents[2]
    if str(src_root) not in sys.path:
        sys.path.append(str(src_root))
    from config import load_settings

try:  # Import perezoso para no romper cuando no esté instalada la librería
    from influxdb_client import InfluxDBClient, Point, WritePrecision
    from influxdb_client.client.write_api import SYNCHRONOUS
except ImportError:  # pragma: no cover - dependencias opcionales
    InfluxDBClient = None  # type: ignore
    Point = None  # type: ignore
    WritePrecision = None  # type: ignore
    SYNCHRONOUS = None  # type: ignore

logger = logging.getLogger(__name__)


class InfluxSink:
    """Gestor de escritura hacia InfluxDB."""

    def __init__(
        self,
        *,
        url: str,
        token: str,
        org: str,
        bucket: str,
        enabled: bool,
        measurement: str = "naira_samples",
    ) -> None:
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket
        self.measurement = measurement
        self.enabled = bool(enabled)
        self.client: Optional[InfluxDBClient] = None
        self.write_api = None

        if not self.enabled:
            logger.debug("InfluxDB deshabilitado por configuración.")
            return

        if not all([self.url, self.token, self.org, self.bucket]):
            logger.warning(
                "InfluxDB activo pero sin parámetros completos. Se deshabilita la replicación."
            )
            self.enabled = False
            return

        if InfluxDBClient is None:
            logger.warning(
                "Librería influxdb-client no disponible. Instalar dependencias para habilitar replicación."
            )
            self.enabled = False
            return

        try:
            self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            logger.info("Replicación a InfluxDB habilitada: %s bucket=%s", self.url, self.bucket)
        except Exception as exc:  # pragma: no cover - depende del entorno
            logger.error("No se pudo inicializar InfluxDB: %s", exc)
            self.enabled = False
            self.client = None
            self.write_api = None

    def close(self) -> None:
        """Cierra la conexión si existe."""
        if self.client:
            try:
                self.client.close()
            except Exception:  # pragma: no cover - limpieza best effort
                pass
            self.client = None
            self.write_api = None

    def write_sample(self, sample: Dict) -> None:
        """Envía una muestra normalizada a InfluxDB."""
        if not self._ready():
            logger.debug("Sink Influx no listo; se omite muestra %s", sample.get("metric"))
            return

        try:
            point = self._build_sample_point(sample)
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
        except Exception as exc:  # pragma: no cover - acceso remoto
            logger.warning("No se pudo replicar métrica %s en Influx: %s", sample.get("metric"), exc)

    def write_samples(self, samples: Iterable[Dict]) -> None:
        """Envía múltiples muestras en un lote."""
        buffered = list(samples)
        if not buffered:
            return

        if not self._ready():
            logger.debug("Sink Influx no listo; lote omitido (%d muestras)", len(buffered))
            return

        points = []
        for sample in buffered:
            try:
                points.append(self._build_sample_point(sample))
            except Exception as exc:
                logger.debug("Muestra descartada para Influx (%s): %s", sample.get("metric"), exc)
        if points:
            try:
                self.write_api.write(bucket=self.bucket, org=self.org, record=points)
            except Exception as exc:  # pragma: no cover - acceso remoto
                logger.warning("Error replicando lote en Influx: %s", exc)

    def write_device_status(self, node_id: str, status_data: Dict) -> None:
        """Replica estado del dispositivo en Influx."""
        if not self._ready() or Point is None:
            logger.debug("Sink Influx no listo; estado omitido")
            return

        ts = self._get_timestamp(status_data.get("ts"))
        point = Point("naira_device_status").tag("node_id", node_id)
        point.tag("status", status_data.get("status", "unknown"))
        point.time(ts, WritePrecision.NS if WritePrecision else None)

        self._assign_numeric_field(point, "cpu_pct", status_data.get("cpu_pct"))
        self._assign_numeric_field(point, "ram_pct", status_data.get("ram_pct"))
        self._assign_numeric_field(point, "disk_pct", status_data.get("disk_pct"))
        self._assign_numeric_field(point, "temp_c", status_data.get("temp_c"))
        self._assign_numeric_field(point, "uptime_s", status_data.get("uptime_s"))

        try:
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
        except Exception as exc:  # pragma: no cover - acceso remoto
            logger.warning("No se pudo replicar estado del nodo %s: %s", node_id, exc)

    def _ready(self) -> bool:
        ready = bool(self.enabled and self.write_api and Point and WritePrecision)
        if not ready:
            logger.debug(
                "Sink Influx no inicializado (enabled=%s, client=%s, write_api=%s)",
                self.enabled,
                bool(self.client),
                bool(self.write_api),
            )
        return ready

    def _build_sample_point(self, sample: Dict):
        if Point is None:
            raise RuntimeError("Point no disponible; verificar instalación de influxdb-client")

        ts = self._get_timestamp(sample.get("ts"))
        value = sample.get("value")
        try:
            numeric_value = float(value) if value is not None else 0.0
        except (TypeError, ValueError):
            numeric_value = 0.0
        point = (
            Point(self.measurement)
            .tag("node_id", sample.get("node_id", "unknown"))
            .tag("source", sample.get("source", "unknown"))
            .tag("metric", sample.get("metric", "unknown"))
            .tag("unit", sample.get("unit", ""))
            .tag("quality", sample.get("quality", "ok"))
            .field("value", numeric_value)
        )
        point.time(ts, WritePrecision.NS if WritePrecision else None)
        return point

    def _get_timestamp(self, ts: Optional[str]) -> datetime:
        if not ts:
            return datetime.now(UTC)

        try:
            if ts.endswith("Z"):
                return datetime.fromisoformat(ts.replace("Z", "+00:00"))
            return datetime.fromisoformat(ts)
        except ValueError:
            logger.debug("Timestamp inválido para Influx (%s); se usa ahora UTC", ts)
            return datetime.now(UTC)

    @staticmethod
    def _assign_numeric_field(point: "Point", field: str, value: Optional[float]) -> None:
        if value is None:
            return
        try:
            point.field(field, float(value))
        except (TypeError, ValueError):
            logger.debug("Valor %s no numérico para campo %s en Influx", value, field)


_influx_instance: Optional[InfluxSink] = None


def get_influx_sink() -> Optional[InfluxSink]:
    """Devuelve una instancia singleton del sink de Influx."""
    global _influx_instance
    if _influx_instance is None:
        settings = load_settings()
        _influx_instance = InfluxSink(
            url=settings.influx_url,
            token=settings.influx_token,
            org=settings.influx_org,
            bucket=settings.influx_bucket,
            enabled=settings.influx_enabled,
        )
    return _influx_instance if _influx_instance.enabled else None


__all__ = ["InfluxSink", "get_influx_sink"]
