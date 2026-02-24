# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**NAIRA Edge** is a Raspberry Pi-based IoT node for agricultural edge computing. It acquires sensor data (temperature, humidity, soil moisture, irrigation), processes it locally, runs anomaly detection, controls actuators, and publishes results via MQTT/HTTP. The codebase supports both real hardware and full simulation mode.

## Commands

All commands assume the virtual environment is active:
```bash
source venv/bin/activate
```

**Run the node:**
```bash
python -m src.main --sim --log INFO    # simulation (no hardware)
python -m src.main --log DEBUG          # real hardware
```

**Run tests:**
```bash
python -m pytest tests/unit/ -v
python -m pytest tests/unit/acquisition/test_serial_reader.py -v   # single file
python -m pytest tests/unit/ --cov=src --cov-report=term-missing    # with coverage
```

**Acquisition test helper (finer-grained):**
```bash
bash src/acquisition/run_tests.sh verbose
bash src/acquisition/run_tests.sh coverage
```

**Diagnostics dashboard:**
```bash
streamlit run src/diagnostics/diagnostics_app.py
```

**CLI tools:**
```bash
python -m src.acquisition.collector --count 50 --log-level INFO
python -m src.tools.influx_anomaly --help
```

## Architecture

### Unidirectional Pipeline

```
acquisition/ → processing/ → {comms/, control/} → diagnostics/
```

- **`src/acquisition/`** — sensor drivers (RS485/serial) and simulators; normalizes data to the standard contract
- **`src/processing/`** — pure functions (no I/O): filters, aggregations, indicators (dry_alert, balance_hydrique)
- **`src/comms/`** — MQTT/HTTP publishing, offline queue with retry; never reads sensors
- **`src/control/`** — actuator rule engine; all rules require interlocks, cooldowns, fail-safe defaults, and log every decision
- **`src/diagnostics/`** — node health (CPU temp, memory, battery); Streamlit dashboard + Telegram alerts
- **`src/models/`** — anomaly detection (MAD, Z-score); statistical models on time series
- **`src/llm/`** — local LLM inference via Ollama (TinyLlama)
- **`src/config.py`** — all settings loaded from env vars → dataclass; never hardcode secrets/URLs/ports
- **`src/main.py`** — orchestration, mode switching, main loop

### Simulation-First Design

Every subsystem has a `stub.py` simulator. The file naming convention:
- `sensor.py` → hardware implementation
- `stub.py` → simulator (default; always works without hardware)

`main.py` imports stubs by default, switching to hardware drivers only when needed. The data shape is identical in both modes — processing and comms are mode-agnostic.

### Data Contract

All data leaving `acquisition/` must conform to:
```python
{
  "ts": "ISO8601-UTC",
  "node_id": "naira-node-001",       # from config
  "source": "meteo|suelo|riego|diagnostics",
  "metric": "temp_aire|humedad_suelo|caudal",
  "value": 23.45,
  "unit": "°C|%|l/min",
  "quality": "ok|suspect|bad",       # heuristic: range checks, NaN, outliers
  "meta": {}                          # optional
}
```

## Key Conventions

**Error handling:** Never `except: pass`. Always log with context (`node_id`, module, operation) and implement a fallback (cached sample, queue for retry, or quality flag downgrade).

**Logging:** One `logger = logging.getLogger(__name__)` per module. Use `logger.info/warning/error` — not `print()`. Avoid log spam in fast loops; batch or rate-limit.

**Configuration:** All settings in `src/config.py` as a dataclass from env vars:
```bash
NAIRA_NODE_ID, NAIRA_MQTT_BROKER, NAIRA_SERIAL_PORT, NAIRA_SIM
NAIRA_INFLUX_URL, NAIRA_INFLUX_TOKEN, NAIRA_INFLUX_ORG, NAIRA_INFLUX_BUCKET
NAIRA_OLLAMA_URL, NAIRA_OLLAMA_MODEL
TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
```

**Modularity:** If a change touches more than 2 module folders, an abstraction is likely missing. No circular imports.

**Documentation:** One `README.md` per module folder, max 100–150 lines. Long reference docs go in `docs/`, not in module folders.

## Pre-Merge Checklist

- [ ] `python -m src.main --sim` runs without error
- [ ] No hardcoded credentials, IPs, or ports
- [ ] All sensor outputs match the normalized data contract
- [ ] Network failure doesn't crash; payloads queue for retry
- [ ] Logs are readable at INFO level; no loop spam
- [ ] New env vars are documented
