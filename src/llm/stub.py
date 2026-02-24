"""Simulador del cliente LLM para modo sin hardware/red (NAIRA_SIM=1)."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_STUB_RESPONSES: dict[str, str] = {
    "anomaly": "Se detectó una anomalía en el sensor. Verificar calibración y rango esperado.",
    "irrigation": "Las condiciones de suelo indican que el riego puede iniciarse de forma segura.",
    "default": "Diagnóstico simulado: sistema operando dentro de parámetros normales.",
}


class StubLlamaClient:
    """Reemplaza TinyLlamaClient en modo simulado; no requiere Ollama."""

    def is_model_ready(self) -> bool:
        logger.debug("[stub-llm] is_model_ready → True")
        return True

    def ensure_model_available(self) -> bool:
        logger.debug("[stub-llm] ensure_model_available → True")
        return True

    def pull_model(self) -> bool:
        logger.debug("[stub-llm] pull_model → True (no-op)")
        return True

    def generate(self, prompt: str, system: str | None = None, **_kwargs: object) -> str:
        if not prompt.strip():
            raise ValueError("prompt no puede estar vacío")
        for key, response in _STUB_RESPONSES.items():
            if key in prompt.lower():
                logger.info("[stub-llm] generate (keyword=%s)", key)
                return response
        logger.info("[stub-llm] generate (default)")
        return _STUB_RESPONSES["default"]


def get_client(sim: bool = True) -> "StubLlamaClient | object":
    """Devuelve el cliente adecuado según el modo de ejecución."""
    if sim:
        return StubLlamaClient()
    from src.llm.ollama_client import TinyLlamaClient
    return TinyLlamaClient()
