#!/usr/bin/env python3
"""Script de prueba para alertas por Telegram.

Verifica la configuración y envía un mensaje de prueba.

Uso desde raíz del proyecto:
    python src/diagnostics/test_telegram_alerts.py
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# Detecta dónde está el directorio src y lo añade al path
if __name__ == "__main__":
    # Si se ejecuta directamente, añade src al path
    current_file = Path(__file__).resolve()
    src_dir = current_file.parent.parent
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

from diagnostics.telegram_alert import create_alert_manager, AlertThresholds

def main() -> None:
    """Prueba la configuración de Telegram y envía un mensaje."""
    logger.info("=== Test de Alertas Telegram ===")

    # Crear gestor
    manager = create_alert_manager()

    logger.info(f"Bot Token: {'✓ Configurado' if manager.bot_token else '✗ NO CONFIGURADO'}")
    logger.info(f"Chat ID: {'✓ Configurado' if manager.chat_id else '✗ NO CONFIGURADO'}")
    logger.info(f"Umbrales:")
    logger.info(f"  - Temperatura: {manager.thresholds.temp_c}°C")
    logger.info(f"  - CPU: {manager.thresholds.cpu_pct}%")
    logger.info(f"  - RAM: {manager.thresholds.ram_pct}%")
    logger.info(f"  - Disco: {manager.thresholds.disk_pct}%")

    if not manager.bot_token or not manager.chat_id:
        logger.warning("\n⚠️  Telegram no configurado. Para habilitar alertas:")
        logger.warning("   export TELEGRAM_BOT_TOKEN='tu_token'")
        logger.warning("   export TELEGRAM_CHAT_ID='tu_chat_id'")
        logger.info("\nVer: docs/TELEGRAM_ALERTS_SETUP.md")
        return

    # Test de temperatura (por encima del umbral)
    logger.info("\n📤 Enviando alerta de prueba (temperatura alta)...")
    manager.check_temperature(65.0)

    # Test de CPU
    logger.info("📤 Enviando alerta de prueba (CPU alto)...")
    manager.check_cpu(90.0)

    logger.info("\n✅ Test completado. Revisa tu chat de Telegram.")


if __name__ == "__main__":
    main()
