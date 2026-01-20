"""
Simulador de sensores - Modo stub para testing sin hardware.

Genera datos realistas para desarrollo y testing.
"""

import random
import logging
from datetime import datetime, UTC
from typing import Dict

logger = logging.getLogger(__name__)


def read_sensor(sim: bool = True) -> Dict[str, float]:
    """
    Lee datos de sensores (real o simulado).
    
    Args:
        sim: Si True, devuelve datos simulados (default)
        
    Returns:
        Dict con valores de sensores normalizados
    """
    if sim:
        return {
            "air_temp_c": round(random.uniform(15, 35), 2),
            "air_humidity_pct": round(random.uniform(30, 80), 1),
            "soil_moisture": round(random.uniform(0.2, 0.8), 2),
        }
    else:
        # Placeholder para hardware real
        logger.warning("Hardware real no implementado, usando simulador")
        return read_sensor(sim=True)


def generate_sample() -> Dict:
    """
    Genera una muestra simulada normalizada al formato NAIRA.
    
    Returns:
        Dict con estructura NAIRA completa
    """
    metrics = [
        {
            "metric": "temp_aire",
            "value": round(random.uniform(15, 35), 2),
            "unit": "°C",
            "source": "meteo"
        },
        {
            "metric": "humedad_suelo",
            "value": round(random.uniform(300, 950), 0),
            "unit": "%",
            "source": "suelo"
        },
        {
            "metric": "luminosidad",
            "value": round(random.uniform(0, 5000), 2),
            "unit": "lux",
            "source": "meteo"
        }
    ]
    
    m = random.choice(metrics)
    
    return {
        "ts": datetime.now(UTC).isoformat().replace("+00:00", "") + "Z",
        "node_id": "naira-node-001",
        "source": m["source"],
        "metric": m["metric"],
        "value": m["value"],
        "unit": m["unit"],
        "quality": "ok"
    }
