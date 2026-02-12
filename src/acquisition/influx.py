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
        telemetry_bucket: Optional[str] = None,
        resources_bucket: Optional[str] = None,
        events_bucket: Optional[str] = None,
        measurement_resources: str = "naira_resource",
    ) -> None:
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket  # compatibilidad hacia atrás
        self.bucket_telemetry = telemetry_bucket or bucket
        self.bucket_resources = resources_bucket or self.bucket_telemetry
        self.bucket_events = events_bucket or self.bucket_telemetry
        self.measurement = measurement
        self.measurement_resources = measurement_resources
        self.enabled = bool(enabled)
        self.client: Optional[InfluxDBClient] = None
        self.write_api = None

        if not self.enabled:
            logger.debug("InfluxDB deshabilitado por configuración.")
            return

        if not all([self.url, self.token, self.org]):
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

    def write_sensor_sample(self, sample: Dict) -> None:
        """Envía una muestra de telemetría a InfluxDB."""
        bucket_name = self._bucket_or_fallback(self.bucket_telemetry)
        if not self._ready(bucket_name):
            logger.debug("Sink Influx no listo; se omite muestra %s", sample.get("metric"))
            return

        try:
            point = self._build_sample_point(sample, self.measurement)
            self._write_records(bucket_name, point)
        except Exception as exc:  # pragma: no cover - acceso remoto
            logger.warning(
                "No se pudo replicar métrica %s en Influx: %s", sample.get("metric"), exc
            )

    def write_sample(self, sample: Dict) -> None:
        """Alias legacy para write_sensor_sample."""
        self.write_sensor_sample(sample)

    def write_resource_sample(self, sample: Dict) -> None:
        """Envía métricas de recursos del nodo."""
        bucket_name = self._bucket_or_fallback(self.bucket_resources)
        if not self._ready(bucket_name):
            logger.debug("Sink Influx no listo; recurso omitido %s", sample.get("resource"))
            return

        try:
            point = self._build_resource_point(sample, self.measurement_resources)
            self._write_records(bucket_name, point)
        except Exception as exc:  # pragma: no cover - acceso remoto
            logger.warning(
                "No se pudo replicar recurso %s en Influx: %s", sample.get("resource"), exc
            )

    def write_samples(self, samples: Iterable[Dict]) -> None:
        """Envía múltiples muestras en un lote."""
        buffered = list(samples)
        if not buffered:
            return

        bucket_name = self._bucket_or_fallback(self.bucket_telemetry)
        if not self._ready(bucket_name):
            logger.debug("Sink Influx no listo; lote omitido (%d muestras)", len(buffered))
            return

        points = []
        for sample in buffered:
            try:
                points.append(self._build_sample_point(sample, self.measurement))
            except Exception as exc:
                logger.debug("Muestra descartada para Influx (%s): %s", sample.get("metric"), exc)
        if points:
            try:
                self._write_records(bucket_name, points)
            except Exception as exc:  # pragma: no cover - acceso remoto
                logger.warning("Error replicando lote en Influx: %s", exc)

    def write_device_status(self, node_id: str, status_data: Dict) -> None:
        """Replica estado del dispositivo en Influx."""
        bucket_name = self._bucket_or_fallback(self.bucket_resources)
        if not self._ready(bucket_name) or Point is None:
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
            self._write_records(bucket_name, point)
        except Exception as exc:  # pragma: no cover - acceso remoto
            logger.warning("No se pudo replicar estado del nodo %s: %s", node_id, exc)

    def _write_records(self, bucket_name: Optional[str], record) -> None:
        if not bucket_name:
            raise ValueError("No hay bucket configurado para Influx")
        self.write_api.write(bucket=bucket_name, org=self.org, record=record)

    def _bucket_or_fallback(self, preferred: Optional[str]) -> Optional[str]:
        return preferred or self.bucket or self.bucket_telemetry

    def is_ready(self, channel: str = "telemetry") -> bool:
        if channel == "resources":
            bucket = self.bucket_resources
        elif channel == "events":
            bucket = self.bucket_events
        else:
            bucket = self.bucket_telemetry
        return self._ready(bucket)

    def _ready(self, bucket_name: Optional[str] = None) -> bool:
        bucket_ok = bucket_name or self.bucket_telemetry or self.bucket
        ready = bool(self.enabled and self.write_api and Point and WritePrecision and bucket_ok)
        if not ready:
            logger.debug(
                "Sink Influx no inicializado (enabled=%s, client=%s, write_api=%s, bucket=%s)",
                self.enabled,
                bool(self.client),
                bool(self.write_api),
                bucket_ok,
            )
        return ready

    def _build_sample_point(self, sample: Dict, measurement: str):
        if Point is None:
            raise RuntimeError("Point no disponible; verificar instalación de influxdb-client")

        ts = self._get_timestamp(sample.get("ts"))
        value = sample.get("value")
        try:
            numeric_value = float(value) if value is not None else 0.0
        except (TypeError, ValueError):
            numeric_value = 0.0
        point = (
            Point(measurement)
            .tag("node_id", sample.get("node_id", "unknown"))
            .tag("source", sample.get("source", "unknown"))
            .tag("metric", sample.get("metric", "unknown"))
            .tag("unit", sample.get("unit", ""))
            .tag("quality", sample.get("quality", "ok"))
            .field("value", numeric_value)
        )
        point.time(ts, WritePrecision.NS if WritePrecision else None)
        return point

    def _build_resource_point(self, sample: Dict, measurement: str):
        if Point is None:
            raise RuntimeError("Point no disponible; verificar instalación de influxdb-client")

        ts = self._get_timestamp(sample.get("ts"))
        value = sample.get("value")
        try:
            numeric_value = float(value) if value is not None else 0.0
        except (TypeError, ValueError):
            numeric_value = 0.0

        point = (
            Point(measurement)
            .tag("node_id", sample.get("node_id", "unknown"))
            .tag("resource", sample.get("resource", sample.get("metric", "unknown")))
            .tag("unit", sample.get("unit", ""))
            .tag("quality", sample.get("quality", "ok"))
            .field("value", numeric_value)
        )
        if "meta" in sample:
            point.tag("meta", str(sample.get("meta")))
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
            telemetry_bucket=settings.influx_bucket_telemetry,
            resources_bucket=settings.influx_bucket_resources,
            events_bucket=settings.influx_bucket_events,
        )
    return _influx_instance if _influx_instance.enabled else None


__all__ = ["InfluxSink", "get_influx_sink"]
