"""Stubs de procesamiento: filtros e indicadores simples."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Dict

from src.models import stub as model_stub


def _iso_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "") + "Z"


def process_sample(sample: Dict[str, float]) -> Dict[str, float]:
    """Procesa una muestra y añade indicadores básicos + IA ligera."""

    if not sample:
        return {}

    processed = dict(sample)
    processed.setdefault("ts", _iso_now())

    soil_raw = sample.get("soil_moisture", 0.0)
    try:
        soil_pct = float(soil_raw) * 100.0
    except (TypeError, ValueError):
        soil_pct = 0.0
    processed["soil_moisture_pct"] = round(min(max(soil_pct, 0.0), 100.0), 1)
    processed["dry_alert"] = processed["soil_moisture_pct"] < 30.0

    # Enriquecemos la muestra con el detector temporal
    model_outputs = model_stub.predict(processed)
    processed.update(model_outputs)
    processed["anomaly_detected"] = bool(processed.get("soil_moisture_pct_anomaly", False))
    return processed


__all__ = ["process_sample"]
