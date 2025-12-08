"""Módulo de comunicaciones — funciones stub para publicar datos."""

from __future__ import annotations

from typing import Dict


def publish_sample(sample: Dict[str, float]) -> bool:
    """Publica una muestra en un broker o endpoint.

    En modo real publicaría por MQTT o HTTP. Aquí solo hace logging.
    """
    # placeholder: en desarrollo, solo imprimimos
    print("[comms] publish:", sample)
    return True


__all__ = ["publish_sample"]
