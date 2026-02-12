"""Persistencia local para estado del nodo, inventario y cola offline."""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

try:  # Uso normal dentro del paquete
    from src.config import load_settings
except ModuleNotFoundError:  # Permite ejecutar "python state_store.py"
    import sys

    src_root = Path(__file__).resolve().parents[2]
    if str(src_root) not in sys.path:
        sys.path.append(str(src_root))
    from config import load_settings  # type: ignore

logger = logging.getLogger(__name__)
DEFAULT_STATE_DB = "/home/naira/NAIRA/naira-edge/data/naira_state.db"


def _iso_now(offset_s: int = 0) -> str:
    base = datetime.now(UTC) + timedelta(seconds=offset_s)
    return base.isoformat().replace("+00:00", "") + "Z"


class StateStore:
    """SQLite para estado operativo y cola offline."""

    def __init__(self, db_path: Optional[str] = None, max_queue: int = 500) -> None:
        settings = load_settings()
        resolved_path = db_path or getattr(settings, "sqlite_state_path", "") or DEFAULT_STATE_DB
        self.db_path = Path(resolved_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        inferred_max = getattr(settings, "offline_queue_max_items", max_queue)
        self.max_queue = max(inferred_max or max_queue, 0)
        self.node_id = getattr(settings, "node_id", "naira-node-001")
        self._initialize_db()

    def _initialize_db(self) -> None:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS node_snapshot (
                        node_id TEXT PRIMARY KEY,
                        ts TEXT NOT NULL,
                        mode TEXT,
                        firmware_sha TEXT,
                        uptime_s REAL,
                        health TEXT,
                        summary TEXT,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS event_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ts TEXT NOT NULL,
                        node_id TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        context TEXT,
                        ack_ts TEXT
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_event_log_node_ts
                        ON event_log(node_id, ts DESC)
                    """
                )
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_event_log_severity
                        ON event_log(severity)
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS inventory_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        device_uid TEXT NOT NULL UNIQUE,
                        kind TEXT NOT NULL,
                        model TEXT,
                        port TEXT,
                        status TEXT,
                        last_seen_ts TEXT,
                        meta TEXT
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_inventory_status
                        ON inventory_items(status)
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS config_versions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        applied_ts TEXT NOT NULL,
                        node_id TEXT NOT NULL,
                        version_tag TEXT,
                        sha256 TEXT,
                        payload TEXT,
                        author TEXT,
                        notes TEXT
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_config_node_ts
                        ON config_versions(node_id, applied_ts DESC)
                    """
                )
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_config_sha
                        ON config_versions(sha256)
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS pending_payloads (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        created_ts TEXT NOT NULL,
                        kind TEXT NOT NULL,
                        payload TEXT NOT NULL,
                        retry_count INTEGER NOT NULL DEFAULT 0,
                        next_retry_ts TEXT,
                        last_error TEXT
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_pending_retry
                        ON pending_payloads(next_retry_ts)
                    """
                )
                conn.commit()
        except sqlite3.Error as exc:  # pragma: no cover - inicialización crítica
            logger.error("No se pudo inicializar state store: %s", exc)
            raise

    def update_node_snapshot(self, snapshot: Dict[str, Any]) -> None:
        record = {
            "node_id": snapshot.get("node_id", self.node_id),
            "ts": snapshot.get("ts", _iso_now()),
            "mode": snapshot.get("mode"),
            "firmware_sha": snapshot.get("firmware_sha"),
            "uptime_s": snapshot.get("uptime_s"),
            "health": snapshot.get("health"),
            "summary": self._serialize_json(snapshot.get("summary")),
        }
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO node_snapshot (node_id, ts, mode, firmware_sha, uptime_s, health, summary, updated_at)
                    VALUES (:node_id, :ts, :mode, :firmware_sha, :uptime_s, :health, :summary, CURRENT_TIMESTAMP)
                    ON CONFLICT(node_id) DO UPDATE SET
                        ts=excluded.ts,
                        mode=excluded.mode,
                        firmware_sha=excluded.firmware_sha,
                        uptime_s=excluded.uptime_s,
                        health=excluded.health,
                        summary=excluded.summary,
                        updated_at=CURRENT_TIMESTAMP
                    """,
                    record,
                )
                conn.commit()
        except sqlite3.Error as exc:
            logger.error("No se pudo actualizar snapshot: %s", exc)
            raise

    def log_event(self, event: Dict[str, Any]) -> int:
        payload = {
            "ts": event.get("ts", _iso_now()),
            "node_id": event.get("node_id", self.node_id),
            "severity": event.get("severity", "info"),
            "event_type": event.get("event_type", "generic"),
            "context": self._serialize_json(event.get("context")),
            "ack_ts": event.get("ack_ts"),
        }
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO event_log (ts, node_id, severity, event_type, context, ack_ts)
                    VALUES (:ts, :node_id, :severity, :event_type, :context, :ack_ts)
                    """,
                    payload,
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as exc:
            logger.error("No se pudo registrar evento: %s", exc)
            raise

    def ack_event(self, event_id: int) -> None:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE event_log SET ack_ts = ? WHERE id = ?",
                    (_iso_now(), event_id),
                )
                conn.commit()
        except sqlite3.Error as exc:
            logger.warning("No se pudo reconocer evento %s: %s", event_id, exc)

    def upsert_inventory_item(self, item: Dict[str, Any]) -> None:
        payload = {
            "device_uid": item.get("device_uid"),
            "kind": item.get("kind", "sensor"),
            "model": item.get("model"),
            "port": item.get("port"),
            "status": item.get("status", "unknown"),
            "last_seen_ts": item.get("last_seen_ts", _iso_now()),
            "meta": self._serialize_json(item.get("meta")),
        }
        if not payload["device_uid"]:
            raise ValueError("device_uid es obligatorio para inventory_items")
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO inventory_items (device_uid, kind, model, port, status, last_seen_ts, meta)
                    VALUES (:device_uid, :kind, :model, :port, :status, :last_seen_ts, :meta)
                    ON CONFLICT(device_uid) DO UPDATE SET
                        kind=excluded.kind,
                        model=excluded.model,
                        port=excluded.port,
                        status=excluded.status,
                        last_seen_ts=excluded.last_seen_ts,
                        meta=excluded.meta
                    """,
                    payload,
                )
                conn.commit()
        except sqlite3.Error as exc:
            logger.error("No se pudo registrar inventario: %s", exc)
            raise

    def save_config_version(self, config_payload: Dict[str, Any]) -> int:
        record = {
            "applied_ts": config_payload.get("applied_ts", _iso_now()),
            "node_id": config_payload.get("node_id", self.node_id),
            "version_tag": config_payload.get("version_tag"),
            "sha256": config_payload.get("sha256"),
            "payload": self._serialize_json(config_payload.get("payload")),
            "author": config_payload.get("author"),
            "notes": config_payload.get("notes"),
        }
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO config_versions (applied_ts, node_id, version_tag, sha256, payload, author, notes)
                    VALUES (:applied_ts, :node_id, :version_tag, :sha256, :payload, :author, :notes)
                    """,
                    record,
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as exc:
            logger.error("No se pudo guardar config: %s", exc)
            raise

    def enqueue_payload(
        self,
        payload: Dict[str, Any],
        *,
        kind: str = "telemetry",
        next_retry_ts: Optional[str] = None,
        last_error: Optional[str] = None,
    ) -> int:
        record = {
            "created_ts": _iso_now(),
            "kind": kind,
            "payload": self._serialize_json(payload) or "{}",
            "next_retry_ts": next_retry_ts,
            "last_error": last_error,
        }
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO pending_payloads (created_ts, kind, payload, retry_count, next_retry_ts, last_error)
                    VALUES (:created_ts, :kind, :payload, 0, :next_retry_ts, :last_error)
                    """,
                    record,
                )
                row_id = cursor.lastrowid
                self._trim_queue(cursor)
                conn.commit()
                return row_id
        except sqlite3.Error as exc:
            logger.error("No se pudo encolar payload offline: %s", exc)
            raise

    def get_pending_payloads(self, limit: int = 20) -> List[Dict[str, Any]]:
        limit = max(limit, 1)
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, created_ts, kind, payload, retry_count, next_retry_ts, last_error
                    FROM pending_payloads
                    WHERE next_retry_ts IS NULL OR next_retry_ts <= ?
                    ORDER BY created_ts
                    LIMIT ?
                    """,
                    (_iso_now(), limit),
                )
                rows = cursor.fetchall()
        except sqlite3.Error as exc:
            logger.error("No se pudo leer cola offline: %s", exc)
            return []

        pending: List[Dict[str, Any]] = []
        for row in rows:
            pending.append(
                {
                    "id": row["id"],
                    "created_ts": row["created_ts"],
                    "kind": row["kind"],
                    "payload": self._deserialize_json(row["payload"]),
                    "retry_count": row["retry_count"],
                    "next_retry_ts": row["next_retry_ts"],
                    "last_error": row["last_error"],
                }
            )
        return pending

    def mark_payload_sent(self, payload_id: int) -> None:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM pending_payloads WHERE id = ?", (payload_id,))
                conn.commit()
        except sqlite3.Error as exc:
            logger.warning("No se pudo eliminar payload %s: %s", payload_id, exc)

    def mark_payload_error(self, payload_id: int, error_msg: str, retry_delay_s: int) -> None:
        next_retry = _iso_now(retry_delay_s)
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE pending_payloads
                    SET retry_count = retry_count + 1,
                        next_retry_ts = ?,
                        last_error = ?
                    WHERE id = ?
                    """,
                    (next_retry, error_msg[:512], payload_id),
                )
                conn.commit()
        except sqlite3.Error as exc:
            logger.warning("No se pudo actualizar payload %s: %s", payload_id, exc)

    def get_queue_stats(self) -> Dict[str, Any]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM pending_payloads")
                pending = cursor.fetchone()[0]
                cursor.execute("SELECT MAX(ts) FROM event_log")
                last_event = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM inventory_items")
                inventory_count = cursor.fetchone()[0]
        except sqlite3.Error as exc:
            logger.error("No se pudo leer métricas del store: %s", exc)
            return {"state_db": str(self.db_path), "error": str(exc)}
        return {
            "state_db": str(self.db_path),
            "pending_payloads": pending,
            "inventory_items": inventory_count,
            "last_event_ts": last_event,
        }

    def _trim_queue(self, cursor: sqlite3.Cursor) -> None:
        if self.max_queue <= 0:
            return
        cursor.execute("SELECT COUNT(*) FROM pending_payloads")
        count = cursor.fetchone()[0]
        if count <= self.max_queue:
            return
        surplus = count - self.max_queue
        cursor.execute(
            """
            DELETE FROM pending_payloads
            WHERE id IN (
                SELECT id FROM pending_payloads
                ORDER BY created_ts
                LIMIT ?
            )
            """,
            (surplus,),
        )

    @staticmethod
    def _serialize_json(value: Any) -> Optional[str]:
        if value is None:
            return None
        try:
            return json.dumps(value, ensure_ascii=True, separators=(",", ":"))
        except (TypeError, ValueError):
            logger.debug("Valor no serializable; se descarta")
            return None

    @staticmethod
    def _deserialize_json(raw: Optional[str]) -> Any:
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.debug("JSON inválido en state store")
            return None


_state_store_instance: Optional[StateStore] = None


def get_state_store(db_path: Optional[str] = None) -> Optional[StateStore]:
    settings = load_settings()
    if not getattr(settings, "state_store_enabled", True):
        logger.debug("State store deshabilitado por configuración")
        return None

    global _state_store_instance
    if _state_store_instance is None:
        max_queue = getattr(settings, "offline_queue_max_items", 500)
        _state_store_instance = StateStore(db_path or settings.sqlite_state_path, max_queue=max_queue)
    return _state_store_instance


__all__ = ["StateStore", "get_state_store"]
