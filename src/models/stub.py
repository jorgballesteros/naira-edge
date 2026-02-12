"""Modelos ligeros y detectores basados en series temporales."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Dict

from .mad_anomaly import RollingMadAnomalyDetector
from .zscore_anomaly import RollingAnomalyDetector

_soil_detector = RollingAnomalyDetector(
    metric="soil_moisture_pct",
    window=timedelta(days=3),
    min_samples=72,
    z_threshold=2.5,
    max_samples=4096,
)

_temp_detector = RollingMadAnomalyDetector(
    metric="air_temp_c",
    window=timedelta(hours=12),
    min_samples=60,
    mad_threshold=3.0,
    max_samples=2048,
)


def _iso_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "") + "Z"


def predict(sample: Dict[str, float]) -> Dict[str, float]:
    """Enriquece la muestra con inferencias ligeras."""

    ts = sample.get("ts") or _iso_now()
    soil_pct = sample.get("soil_moisture_pct")
    soil_anomaly = _soil_detector.evaluate(ts, soil_pct)

    temp_val = sample.get("air_temp_c")
    temp_anomaly = _temp_detector.evaluate(ts, temp_val)

    soil_value = float(soil_pct) if soil_pct is not None else 50.0
    risk_score = max(0.0, (50.0 - soil_value) / 50.0)

    result = dict(soil_anomaly)
    result.update(temp_anomaly)
    result["risk_score"] = round(risk_score, 3)
    result["ts_model"] = ts
    result["temp_alert"] = bool(temp_anomaly.get("air_temp_c_mad_anomaly"))
    return result


__all__ = ["predict"]
