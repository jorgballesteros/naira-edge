#!/usr/bin/env python3
"""Ejemplos de uso del StateStore (SQLite operativo)."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Dict

try:
    from src.acquisition.state_store import StateStore, get_state_store
except ModuleNotFoundError:
    import sys
    from pathlib import Path

    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.append(str(project_root))
    from src.acquisition.state_store import StateStore, get_state_store  # type: ignore


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def example_snapshot(store: StateStore) -> None:
    logger.info("=" * 60)
    logger.info("EJEMPLO 1: Node Snapshot")
    logger.info("=" * 60)
    store.update_node_snapshot(
        {
            "node_id": "naira-node-001",
            "ts": datetime.now(UTC).isoformat().replace("+00:00", "") + "Z",
            "mode": "sim",
            "firmware_sha": "deadbeef",
            "uptime_s": 123.4,
            "health": "ok",
            "summary": {"last_metric": "temp_aire", "value": 23.1},
        }
    )
    logger.info("✓ Snapshot actualizado")


def example_event_log(store: StateStore) -> None:
    logger.info("=" * 60)
    logger.info("EJEMPLO 2: Event Log")
    logger.info("=" * 60)
    event_id = store.log_event(
        {
            "event_type": "sensor_value_out_of_range",
            "severity": "warn",
            "context": {"metric": "temp_aire", "value": 99.0},
        }
    )
    logger.info("Evento registrado id=%s", event_id)
    store.ack_event(event_id)
    logger.info("Evento reconocido")


def example_inventory(store: StateStore) -> None:
    logger.info("=" * 60)
    logger.info("EJEMPLO 3: Inventory")
    logger.info("=" * 60)
    store.upsert_inventory_item(
        {
            "device_uid": "sensor-temp-001",
            "kind": "sensor",
            "model": "MKR-temp",
            "port": "/dev/ttyACM0",
            "status": "online",
            "meta": {"range": "-20/60", "unit": "°C"},
        }
    )
    logger.info("✓ Inventario actualizado")


def example_offline_queue(store: StateStore) -> None:
    logger.info("=" * 60)
    logger.info("EJEMPLO 4: Offline Queue")
    logger.info("=" * 60)
    payload = {"type": "sensor_sample", "data": {"metric": "temp_aire", "value": 25.1}}
    payload_id = store.enqueue_payload(payload, kind="telemetry", last_error="influx_down")
    logger.info("Payload encolado id=%s", payload_id)
    pending = store.get_pending_payloads(limit=5)
    logger.info("Pendientes=%s", len(pending))
    if pending:
        store.mark_payload_error(pending[0]["id"], "still_down", 5)
        store.mark_payload_sent(pending[0]["id"])
        logger.info("Payload marcado como reenviado")


def example_stats(store: StateStore) -> None:
    logger.info("=" * 60)
    logger.info("EJEMPLO 5: State Stats")
    logger.info("=" * 60)
    stats: Dict[str, str] = store.get_queue_stats()
    logger.info(json.dumps(stats, indent=2))


def main() -> None:
    store = get_state_store()
    if not store:
        logger.error("StateStore deshabilitado, revisa configuración")
        return
    example_snapshot(store)
    example_event_log(store)
    example_inventory(store)
    example_offline_queue(store)
    example_stats(store)
    logger.info("=" * 60)
    logger.info("✓ Ejemplos completados")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
