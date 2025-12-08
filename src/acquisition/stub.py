"""Stubs de adquisición para pruebas/simulación.

Funciones mínimas que devuelven valores simulados para sensores.
"""

from __future__ import annotations

import random
from typing import Dict


def read_sensor(sim: bool = True) -> Dict[str, float]:
    """Lee un "sensor" y devuelve una muestra simulada.

    En modo real (sim=False) este módulo debería leer hardware.
    """
    if sim:
        return {
            "air_temp_c": round(15 + 10 * random.random(), 2),
            "air_humidity_pct": round(30 + 50 * random.random(), 1),
            "soil_moisture": round(0.2 + 0.6 * random.random(), 3),
        }
    # placeholder for hardware read
    return {"air_temp_c": 0.0, "air_humidity_pct": 0.0, "soil_moisture": 0.0}


__all__ = ["read_sensor"]
