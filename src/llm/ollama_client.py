"""Cliente TinyLlama basado en la API HTTP de Ollama."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import requests
from requests import RequestException, Response

from src.config import Settings, load_settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OllamaConfig:
    """Parámetros necesarios para hablar con un servidor Ollama."""

    host: str
    port: int
    model: str
    timeout_s: float = 30.0
    pull_retries: int = 2
    retry_backoff_s: float = 2.0

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"


def load_role(path: str | Path | None = None) -> str:
    """Carga el rol del modelo desde un archivo de texto.

    Devuelve el contenido del archivo o cadena vacía si no existe o no se especifica.
    """
    if not path:
        return ""
    try:
        return Path(path).read_text(encoding="utf-8").strip()
    except OSError as exc:
        logger.warning("No se pudo cargar el rol desde '%s': %s", path, exc)
        return ""


def config_from_settings(settings: Optional[Settings] = None) -> OllamaConfig:
    """Construye la configuración a partir de src.config.Settings."""

    cfg = settings or load_settings()
    return OllamaConfig(
        host=cfg.ollama_host,
        port=cfg.ollama_port,
        model=cfg.ollama_model,
        timeout_s=cfg.ollama_timeout_s,
        pull_retries=cfg.ollama_pull_retries,
        retry_backoff_s=cfg.ollama_retry_backoff_s,
    )


class TinyLlamaClient:
    """Wrapper robusto para descargar e invocar TinyLlama vía Ollama."""

    def __init__(
        self,
        config: Optional[OllamaConfig] = None,
        settings: Optional[Settings] = None,
    ) -> None:
        if config is None:
            config = config_from_settings(settings)
        self._config = config

    @property
    def config(self) -> OllamaConfig:
        return self._config

    def is_model_ready(self) -> bool:
        """Devuelve True si TinyLlama ya está disponible localmente."""

        url = f"{self._config.base_url}/api/tags"
        try:
            response = requests.get(url, timeout=self._config.timeout_s)
            response.raise_for_status()
        except RequestException as exc:
            logger.warning("No se pudo consultar Ollama tags: %s", exc)
            return False

        try:
            payload = response.json()
        except ValueError as exc:
            logger.error("Respuesta inválida al listar modelos Ollama: %s", exc)
            return False
        finally:
            response.close()

        models = payload.get("models") or []
        for entry in models:
            if self._model_matches(entry.get("name", "")):
                return True
        return False

    def ensure_model_available(self) -> bool:
        """Verifica o intenta descargar TinyLlama retornando True en éxito."""

        if self.is_model_ready():
            return True

        for attempt in range(1, self._config.pull_retries + 1):
            logger.info("Descargando modelo %s (intento %s/%s)", self._config.model, attempt, self._config.pull_retries)
            if self.pull_model() and self.is_model_ready():
                return True
            time.sleep(self._config.retry_backoff_s)
        return False

    def pull_model(self) -> bool:
        """Solicita a Ollama la descarga del modelo configurado."""

        url = f"{self._config.base_url}/api/pull"
        try:
            response = requests.post(
                url,
                json={"name": self._config.model},
                timeout=self._config.timeout_s,
                stream=True,
            )
            response.raise_for_status()
        except RequestException as exc:
            logger.error("Error al iniciar pull de TinyLlama: %s", exc)
            return False

        success = False
        for chunk in self._iter_stream(response):
            status = chunk.get("status")
            if status:
                logger.info("[ollama pull] %s", status)
            if status == "success":
                success = True
        response.close()

        if not success:
            logger.warning("Ollama no reportó éxito al descargar %s", self._config.model)
        return success

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        stream: bool = False,
    ) -> str:
        """Invoca TinyLlama y devuelve el texto generado."""

        if not prompt.strip():
            raise ValueError("prompt no puede estar vacío")

        url = f"{self._config.base_url}/api/generate"
        payload: Dict[str, Any] = {
            "model": self._config.model,
            "prompt": prompt,
            "stream": stream,
        }
        if system:
            payload["system"] = system
        if options:
            payload["options"] = options

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self._config.timeout_s,
                stream=stream,
            )
            response.raise_for_status()
        except RequestException as exc:
            logger.error("TinyLlama generate falló: %s", exc)
            raise RuntimeError("No se pudo generar respuesta con TinyLlama") from exc

        if stream:
            try:
                chunks = [chunk.get("response", "") for chunk in self._iter_stream(response)]
            finally:
                response.close()
            return "".join(chunks).strip()

        try:
            data = response.json()
        except ValueError as exc:
            response.close()
            logger.error("Respuesta inválida de TinyLlama: %s", exc)
            raise RuntimeError("TinyLlama devolvió JSON inválido") from exc
        response.close()
        return str(data.get("response", "")).strip()

    def _iter_stream(self, response: Response) -> Iterable[Dict[str, Any]]:
        """Itera respuestas chunked de Ollama gestionando JSON parciales."""

        for raw_line in response.iter_lines(decode_unicode=True):
            if not raw_line:
                continue
            try:
                yield json.loads(raw_line)
            except json.JSONDecodeError:
                logger.debug("Chunk no parseable de Ollama: %s", raw_line)
                continue

    def _model_matches(self, installed_name: str) -> bool:
        """True si installed_name satisface el modelo configurado.

        - Sin tag en config (p. ej. "tinyllama"): acepta cualquier variante
          ("tinyllama:latest", "tinyllama:1.1b", …).
        - Con tag explícito (p. ej. "tinyllama:1.1b"): exige coincidencia exacta;
          no acepta "tinyllama:latest" en su lugar.
        """
        desired = (self._config.model or "").strip().lower()
        installed = (installed_name or "").strip().lower()
        if ":" in desired:
            return installed == desired
        return installed.split(":", 1)[0] == desired


__all__ = ["OllamaConfig", "TinyLlamaClient", "config_from_settings", "load_role"]
