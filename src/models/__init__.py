"""Modelos tradicionales y compatibilidad hacia atrás con LLMs."""

from . import stub

try:
	from src.llm.ollama_client import (
		OllamaConfig,
		TinyLlamaClient,
		config_from_settings,
	)
except ModuleNotFoundError:  # pragma: no cover - módulo opcional
	OllamaConfig = TinyLlamaClient = config_from_settings = None  # type: ignore

__all__ = ["stub", "OllamaConfig", "TinyLlamaClient", "config_from_settings"]
