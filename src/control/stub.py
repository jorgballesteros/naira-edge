"""Lógicas simples de control / actuadores (simulación)."""

from __future__ import annotations

from typing import Dict


def apply_rules(sample: Dict[str, float]) -> Dict[str, bool]:
    """Aplica reglas de control simples (ej. activar riego) y devuelve acciones.

    En instalación real, se enviaría comandos a relés/BLE/MODBUS/etc.
    """
    actions = {"start_irrigation": False}
    if sample.get("dry_alert", False):
        actions["start_irrigation"] = True
        print("[control] Regla accionada: start_irrigation")
    else:
        print("[control] No se accionan actuadores")
    return actions


__all__ = ["apply_rules"]
