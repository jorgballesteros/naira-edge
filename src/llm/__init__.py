"""Clientes y utilidades para modelos LLM (Ollama, etc.)."""

from .ollama_client import OllamaConfig, TinyLlamaClient, config_from_settings, load_role

__all__ = ["OllamaConfig", "TinyLlamaClient", "config_from_settings", "load_role"]
