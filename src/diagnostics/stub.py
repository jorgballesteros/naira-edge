"""Funciones de diagnóstico del nodo (stubs para simulación)."""

from __future__ import annotations

from typing import Dict


def health_check() -> Dict[str, float]:
    """Devuelve un diccionario con métricas de salud del nodo.

    Valores simulados por ahora.
    """
    return {"internal_temp_c": 42.0, "battery_v": 3.7}


__all__ = ["health_check"]
