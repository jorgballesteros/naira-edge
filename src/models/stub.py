"""Placeholder para modelos ligeros de inferencia.

Aquí se colocarían adaptadores a tflite, onnxruntime o modelos propios.
"""

from __future__ import annotations

from typing import Dict


def predict(sample: Dict[str, float]) -> Dict[str, float]:
    """Función de ejemplo que 'predice' un riesgo simple.

    Retorna una dict con la probabilidad estimada de algún riesgo.
    """
    soil_pct = sample.get("soil_moisture_pct", 50)
    # ejemplo: riesgo si la humedad de suelo es baja
    risk_score = max(0.0, (50.0 - float(soil_pct)) / 50.0)
    return {"risk_score": round(risk_score, 3)}


__all__ = ["predict"]
