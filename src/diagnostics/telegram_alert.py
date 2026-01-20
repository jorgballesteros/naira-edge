"""Módulo de alertas por Telegram para eventos críticos del nodo edge.

Captura eventos de temperatura, CPU, RAM, disco y envía notificaciones
a un chat de Telegram de forma asincrónica con rate-limiting.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict

import requests

logger = logging.getLogger(__name__)


@dataclass
class AlertThresholds:
    """Umbrales de alerta configurables."""

    temp_c: float = 60.0  # Temperatura crítica en °C
    cpu_pct: float = 85.0  # CPU crítica en %
    ram_pct: float = 90.0  # RAM crítica en %
    disk_pct: float = 95.0  # Disco crítico en %


@dataclass
class TelegramAlertManager:
    """Gestor de alertas por Telegram con rate-limiting."""

    bot_token: str
    chat_id: str
    thresholds: AlertThresholds = field(default_factory=AlertThresholds)
    alert_cooldown_s: int = 300  # No enviar mismo alerta en < 5 min
    last_alerts: Dict[str, datetime] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Valida credenciales."""
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram: credenciales incompletas (bot_token o chat_id vacíos)")
            self.bot_token = ""

    def _can_send_alert(self, alert_key: str) -> bool:
        """Verifica si es tiempo de enviar una alerta (rate-limiting)."""
        last_time = self.last_alerts.get(alert_key)
        if last_time is None:
            return True
        elapsed = (datetime.now() - last_time).total_seconds()
        return elapsed >= self.alert_cooldown_s

    def _send_telegram_message(self, text: str) -> bool:
        """Envía mensaje a Telegram. Retorna True si éxito."""
        if not self.bot_token or not self.chat_id:
            logger.debug("Telegram: modo simulado (sin credenciales)")
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown",
        }

        try:
            resp = requests.post(url, json=payload, timeout=5)
            if resp.status_code == 200:
                logger.info("Telegram alert sent successfully")
                return True
            else:
                logger.warning(
                    f"Telegram error {resp.status_code}: {resp.text[:200]}"
                )
                return False
        except requests.RequestException as e:
            logger.warning(f"Telegram send failed: {e}")
            return False

    def check_temperature(self, temp_c: float | None) -> None:
        """Verifica temperatura y envía alerta si supera umbral."""
        if temp_c is None or temp_c < self.thresholds.temp_c:
            return

        alert_key = "temp_high"
        if not self._can_send_alert(alert_key):
            return

        msg = (
            f"🌡️ **ALERTA TEMPERATURA**\n"
            f"Nodo: {os.getenv('NAIRA_NODE_ID', 'naira-node-001')}\n"
            f"Temperatura: {temp_c:.1f}°C (umbral: {self.thresholds.temp_c}°C)\n"
            f"Hora: {datetime.now().strftime('%H:%M:%S')}\n"
            f"⚠️ RPi puede ralentizarse a >75°C"
        )

        if self._send_telegram_message(msg):
            self.last_alerts[alert_key] = datetime.now()

    def check_cpu(self, cpu_pct: float) -> None:
        """Verifica uso de CPU y envía alerta si supera umbral."""
        if cpu_pct < self.thresholds.cpu_pct:
            return

        alert_key = "cpu_high"
        if not self._can_send_alert(alert_key):
            return

        msg = (
            f"🔴 **ALERTA CPU**\n"
            f"Nodo: {os.getenv('NAIRA_NODE_ID', 'naira-node-001')}\n"
            f"CPU: {cpu_pct:.1f}% (umbral: {self.thresholds.cpu_pct}%)\n"
            f"Hora: {datetime.now().strftime('%H:%M:%S')}"
        )

        if self._send_telegram_message(msg):
            self.last_alerts[alert_key] = datetime.now()

    def check_ram(self, ram_pct: float) -> None:
        """Verifica uso de RAM y envía alerta si supera umbral."""
        if ram_pct < self.thresholds.ram_pct:
            return

        alert_key = "ram_high"
        if not self._can_send_alert(alert_key):
            return

        msg = (
            f"💾 **ALERTA MEMORIA**\n"
            f"Nodo: {os.getenv('NAIRA_NODE_ID', 'naira-node-001')}\n"
            f"RAM: {ram_pct:.1f}% (umbral: {self.thresholds.ram_pct}%)\n"
            f"Hora: {datetime.now().strftime('%H:%M:%S')}"
        )

        if self._send_telegram_message(msg):
            self.last_alerts[alert_key] = datetime.now()

    def check_disk(self, disk_pct: float) -> None:
        """Verifica uso de disco y envía alerta si supera umbral."""
        if disk_pct < self.thresholds.disk_pct:
            return

        alert_key = "disk_high"
        if not self._can_send_alert(alert_key):
            return

        msg = (
            f"💿 **ALERTA DISCO**\n"
            f"Nodo: {os.getenv('NAIRA_NODE_ID', 'naira-node-001')}\n"
            f"Disco: {disk_pct:.1f}% (umbral: {self.thresholds.disk_pct}%)\n"
            f"Hora: {datetime.now().strftime('%H:%M:%S')}"
        )

        if self._send_telegram_message(msg):
            self.last_alerts[alert_key] = datetime.now()

    def check_all(
        self,
        temp_c: float | None = None,
        cpu_pct: float | None = None,
        ram_pct: float | None = None,
        disk_pct: float | None = None,
    ) -> None:
        """Ejecuta todas las comprobaciones en un solo llamado."""
        if temp_c is not None:
            self.check_temperature(temp_c)
        if cpu_pct is not None:
            self.check_cpu(cpu_pct)
        if ram_pct is not None:
            self.check_ram(ram_pct)
        if disk_pct is not None:
            self.check_disk(disk_pct)


def create_alert_manager() -> TelegramAlertManager:
    """Factory para crear gestor de alertas desde variables de entorno."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

    thresholds = AlertThresholds(
        temp_c=float(os.getenv("ALERT_TEMP_C", "60")),
        cpu_pct=float(os.getenv("ALERT_CPU_PCT", "85")),
        ram_pct=float(os.getenv("ALERT_RAM_PCT", "90")),
        disk_pct=float(os.getenv("ALERT_DISK_PCT", "95")),
    )

    return TelegramAlertManager(
        bot_token=bot_token,
        chat_id=chat_id,
        thresholds=thresholds,
    )


__all__ = ["TelegramAlertManager", "AlertThresholds", "create_alert_manager"]
