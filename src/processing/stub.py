"""Stubs de procesamiento: filtros e indicadores simples."""

from __future__ import annotations

from typing import Dict


def process_sample(sample: Dict[str, float]) -> Dict[str, float]:
    """Procesa una muestra y añade indicadores básicos.

    Devuelve la muestra original enriquecida con indicadores calculados
    como "dry_alert" o humedad relativa procesada.
    """
    if not sample:
        return {}

    # Normalizar y añadir un indicador simple de sequía (ejemplo pedagógico)
    soil = sample.get("soil_moisture", 0.0)
    processed = dict(sample)
    processed["soil_moisture_pct"] = round(min(max(soil * 100.0, 0), 100), 1)
    processed["dry_alert"] = processed["soil_moisture_pct"] < 30.0
    return processed


__all__ = ["process_sample"]
