"""Carga de configuración para el nodo edge NAIRA.

Este archivo expone una carga mínima basada en variables de entorno y
defaults para facilitar el desarrollo y las pruebas en modo simulado.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Settings:
    node_id: str = os.getenv("NAIRA_NODE_ID", "naira-node-001")
    mqtt_broker: str = os.getenv("NAIRA_MQTT_BROKER", "localhost:1883")
    report_interval_s: int = int(os.getenv("NAIRA_REPORT_INTERVAL", "60"))
    sim_mode: bool = os.getenv("NAIRA_SIM", "1") in ("1", "true", "True")


def load_settings() -> Settings:
    """Devuelve la configuración activa para el nodo."""
    return Settings()


__all__ = ["Settings", "load_settings"]