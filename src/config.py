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
    # Almacenamiento de estado (SQLite)
    state_store_enabled: bool = os.getenv("NAIRA_STATE_STORE_ENABLED", "1") in ("1", "true", "True")
    sqlite_state_path: str = os.getenv(
        "NAIRA_STATE_DB", "/home/naira/NAIRA/naira-edge/data/naira_state.db"
    )
    simulated_inventory_path: str = os.getenv("NAIRA_SIM_INVENTORY_PATH", "")
    offline_queue_max_items: int = int(os.getenv("NAIRA_OFFLINE_QUEUE_MAX", "500"))
    collector_interval_s: int = int(os.getenv("NAIRA_COLLECTOR_INTERVAL", "10"))
    # Telegram alertas
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")
    # InfluxDB
    influx_enabled: bool = os.getenv("NAIRA_INFLUX_ENABLED", "0") in ("1", "true", "True")
    influx_url: str = os.getenv("NAIRA_INFLUX_URL", "")
    influx_token: str = os.getenv("NAIRA_INFLUX_TOKEN", "")
    influx_org: str = os.getenv("NAIRA_INFLUX_ORG", "")
    influx_bucket: str = os.getenv("NAIRA_INFLUX_BUCKET", "")
    influx_bucket_telemetry: str = os.getenv(
        "NAIRA_INFLUX_BUCKET_TELEMETRY",
        os.getenv("NAIRA_INFLUX_BUCKET", ""),
    )
    influx_bucket_resources: str = os.getenv(
        "NAIRA_INFLUX_BUCKET_RESOURCES",
        os.getenv("NAIRA_INFLUX_BUCKET", ""),
    )
    influx_bucket_events: str = os.getenv(
        "NAIRA_INFLUX_BUCKET_EVENTS",
        os.getenv("NAIRA_INFLUX_BUCKET", ""),
    )
    influx_retry_interval_s: int = int(os.getenv("NAIRA_INFLUX_RETRY_INTERVAL", "10"))
    # LLM / Ollama
    ollama_host: str = os.getenv("NAIRA_OLLAMA_HOST", "127.0.0.1")
    ollama_port: int = int(os.getenv("NAIRA_OLLAMA_PORT", "11434"))
    ollama_model: str = os.getenv("NAIRA_OLLAMA_MODEL", "qwen2.5:1.5b")
    ollama_timeout_s: float = float(os.getenv("NAIRA_OLLAMA_TIMEOUT", "120"))
    ollama_pull_retries: int = int(os.getenv("NAIRA_OLLAMA_PULL_RETRIES", "2"))
    ollama_retry_backoff_s: float = float(os.getenv("NAIRA_OLLAMA_RETRY_BACKOFF", "2"))
    ollama_num_ctx: int = int(os.getenv("NAIRA_OLLAMA_NUM_CTX", "4096"))
    ollama_role_path: str = os.getenv(
        "NAIRA_OLLAMA_ROLE_PATH",
        str(os.path.join(os.path.dirname(__file__), "llm", "role.md")),
    )


def load_settings() -> Settings:
    """Devuelve la configuración activa para el nodo."""
    return Settings()


__all__ = ["Settings", "load_settings"]