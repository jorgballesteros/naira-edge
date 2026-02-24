from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from requests import RequestException

from src.llm.ollama_client import OllamaConfig, TinyLlamaClient


def _dummy_config() -> OllamaConfig:
    return OllamaConfig(host="localhost", port=11434, model="tinyllama", timeout_s=5.0)


def _make_tags_response(names: list[str]) -> MagicMock:
    response = MagicMock()
    response.json.return_value = {"models": [{"name": n} for n in names]}
    response.raise_for_status.return_value = None
    return response


def test_is_model_ready_no_tag_matches_any_variant() -> None:
    """Sin tag en config: acepta cualquier variante del modelo."""
    client = TinyLlamaClient(config=_dummy_config())  # model="tinyllama"
    response = _make_tags_response(["tinyllama:latest"])

    with patch("src.llm.ollama_client.requests.get", return_value=response):
        assert client.is_model_ready() is True
        response.close.assert_called_once()


def test_is_model_ready_explicit_tag_requires_exact_match() -> None:
    """Con tag explícito: solo coincide la variante exacta."""
    config = OllamaConfig(host="localhost", port=11434, model="tinyllama:1.1b", timeout_s=5.0)
    client = TinyLlamaClient(config=config)
    response = _make_tags_response(["tinyllama:latest"])

    with patch("src.llm.ollama_client.requests.get", return_value=response):
        assert client.is_model_ready() is False


def test_is_model_ready_explicit_tag_matches_exact() -> None:
    config = OllamaConfig(host="localhost", port=11434, model="tinyllama:1.1b", timeout_s=5.0)
    client = TinyLlamaClient(config=config)
    response = _make_tags_response(["tinyllama:1.1b"])

    with patch("src.llm.ollama_client.requests.get", return_value=response):
        assert client.is_model_ready() is True


def test_generate_returns_text() -> None:
    client = TinyLlamaClient(config=_dummy_config())

    response = MagicMock()
    response.json.return_value = {"response": "hola"}
    response.raise_for_status.return_value = None

    with patch("src.llm.ollama_client.requests.post", return_value=response) as mock_post:
        result = client.generate("Hola TinyLlama")
        assert result == "hola"
        mock_post.assert_called_once()
        response.close.assert_called_once()


def test_generate_raises_on_http_error() -> None:
    client = TinyLlamaClient(config=_dummy_config())

    with patch(
        "src.llm.ollama_client.requests.post",
        side_effect=RequestException("boom"),
    ):
        with pytest.raises(RuntimeError):
            client.generate("hola")


def test_pull_model_success_stream() -> None:
    client = TinyLlamaClient(config=_dummy_config())

    response = MagicMock()
    response.iter_lines.return_value = [
        '{"status": "downloading"}',
        '{"status": "success"}',
    ]
    response.raise_for_status.return_value = None

    with patch("src.llm.ollama_client.requests.post", return_value=response):
        assert client.pull_model() is True
        response.close.assert_called_once()


def test_ensure_model_available_triggers_pull_when_missing() -> None:
    client = TinyLlamaClient(config=_dummy_config())

    with patch.object(client, "is_model_ready", side_effect=[False, True]) as ready_mock:
        with patch.object(client, "pull_model", return_value=True) as pull_mock:
            assert client.ensure_model_available() is True
            pull_mock.assert_called_once()
            assert ready_mock.call_count == 2
