#!/usr/bin/env python3
"""
Ejemplo sencillo:
- Consume una API pública (WorldTimeAPI).
- Parsea la respuesta JSON.
- Extrae campos relevantes.
- Guarda el resultado en un fichero JSON.
"""

import json
from datetime import datetime, UTC
import requests  # pip install requests

# Configuración
TIMEZONE = "Atlantic/Canary"
API_URL = f"https://worldtimeapi.org/api/timezone/{TIMEZONE}"
OUTPUT_FILE = "/home/naira/NAIRA/naira-edge/data//worldtime_last.json"  # ajusta ruta si quieres


def fetch_time_data() -> dict:
    """Llama a la API y devuelve el JSON original (dict)."""
    resp = requests.get(API_URL, timeout=10)
    resp.raise_for_status()  # lanza error si el status code no es 2xx
    return resp.json()


def build_clean_payload(raw: dict) -> dict:
    """
    Construye un JSON "limpio" con sólo los campos relevantes
    de la respuesta de WorldTimeAPI.
    """
    return {
        "timestamp_local": raw.get("datetime"),
        "timezone": raw.get("timezone"),
        "abbreviation": raw.get("abbreviation"),
        "unixtime": raw.get("unixtime"),
        "day_of_week": raw.get("day_of_week"),
        "day_of_year": raw.get("day_of_year"),
        "week_number": raw.get("week_number"),
        "dst": raw.get("dst"),
        "raw_offset": raw.get("raw_offset"),
        "dst_offset": raw.get("dst_offset"),
        # Metadata de la captura
        "meta": {
            "source": "worldtimeapi.org",
            "api_url": API_URL,
            "collected_at_utc": datetime.utcnow().isoformat() + "Z",
        },
    }


def main():
    try:
        raw = fetch_time_data()
        clean_payload = build_clean_payload(raw)

        # Guardar en fichero JSON
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(clean_payload, f, indent=2, ensure_ascii=False)

        # También lo mostramos por stdout (útil para Node-RED o logs)
        print(json.dumps(clean_payload, indent=2, ensure_ascii=False))

    except Exception as e:
        # En un sistema real, aquí podrías:
        # - Escribir en syslog
        # - Enviar alerta a MQTT/HTTP
        error_payload = {
            "status": "error",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "api_url": API_URL,
            "collected_at_utc": datetime.utcnow().isoformat() + "Z",
        }
        print(json.dumps(error_payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

