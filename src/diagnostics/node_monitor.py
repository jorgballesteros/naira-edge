#!/usr/bin/env python3
"""
Monitorización y diagnóstico de una Raspberry Pi.
- Devuelve salida en JSON con métricas del sistema.
- Genera alertas en función de umbrales configurables.
"""

import json
import os
import platform
import socket
import subprocess
import time
from datetime import datetime

import psutil  # pip install psutil


# ---------------------- CONFIGURACIÓN DE UMBRALES ---------------------- #

THRESHOLDS = {
    "cpu_percent": {
        "warning": 70.0,
        "critical": 90.0,
    },
    "load_ratio": {  # load_avg_1min / num_cpus
        "warning": 1.0,
        "critical": 2.0,
    },
    "memory_percent": {
        "warning": 75.0,
        "critical": 90.0,
    },
    "swap_percent": {
        "warning": 40.0,
        "critical": 70.0,
    },
    "disk_root_percent": {
        "warning": 75.0,
        "critical": 90.0,
    },
    "cpu_temperature": {
        "warning": 65.0,   # ºC
        "critical": 75.0,
    },
}

# Servicios que queremos comprobar (opcional)
# Se buscará por nombre de proceso que contenga alguno de estos strings
WATCHED_SERVICES = [
    "mariadbd", "mysqld",          # MariaDB/MySQL
    "node-red", "node-red-pi",     # Node-RED
    "mosquitto",                   # MQTT (por si acaso)
]


# ---------------------- FUNCIONES DE OBTENCIÓN DE MÉTRICAS ---------------------- #

def get_uptime_seconds() -> float:
    boot_time = psutil.boot_time()
    return time.time() - boot_time


def get_cpu_temperature() -> float | None:
    """
    Intenta leer la temperatura de la CPU de la RPi.
    Devuelve temperatura en ºC o None si no se puede obtener.
    """
    # 1) Intentar con vcgencmd
    try:
        out = subprocess.check_output(
            ["vcgencmd", "measure_temp"],
            stderr=subprocess.DEVNULL
        ).decode()
        # formato típico: temp=48.5'C
        if "temp=" in out:
            value = out.strip().split("=", 1)[1].split("'")[0]
            return float(value)
    except Exception:
        pass

    # 2) Intentar con /sys/class/thermal
    try:
        paths = [
            "/sys/class/thermal/thermal_zone0/temp",
            "/sys/class/hwmon/hwmon0/temp1_input",
        ]
        for p in paths:
            if os.path.exists(p):
                with open(p, "r") as f:
                    raw = f.read().strip()
                    # Suele venir en miligrados (ej: 48567 -> 48.567ºC)
                    val = float(raw)
                    if val > 1000:
                        return val / 1000.0
                    return val
    except Exception:
        pass

    return None


def get_service_statuses() -> dict:
    """
    Recorre los procesos y marca si los servicios deseados parecen estar activos.
    No usa systemctl, sólo inspección de procesos.
    """
    running_processes = []
    try:
        for p in psutil.process_iter(attrs=["name", "cmdline"]):
            name = p.info.get("name") or ""
            cmd = " ".join(p.info.get("cmdline") or [])
            running_processes.append((name.lower(), cmd.lower()))
    except Exception:
        pass

    statuses = {}
    for svc in WATCHED_SERVICES:
        svc_lower = svc.lower()
        found = any(
            (svc_lower in name) or (svc_lower in cmd)
            for name, cmd in running_processes
        )
        statuses[svc] = "running" if found else "stopped"

    return statuses


def get_network_stats() -> dict:
    net = psutil.net_io_counters()
    return {
        "bytes_sent": net.bytes_sent,
        "bytes_recv": net.bytes_recv,
        "packets_sent": net.packets_sent,
        "packets_recv": net.packets_recv,
    }


def collect_metrics() -> dict:
    """
    Recopila todas las métricas de interés de la RPi.
    """
    # CPU
    cpu_percent = psutil.cpu_percent(interval=1.0)
    cpu_count = psutil.cpu_count(logical=True)
    load1, load5, load15 = os.getloadavg()

    # Memoria
    vm = psutil.virtual_memory()
    sm = psutil.swap_memory()

    # Disco (partición raíz)
    disk_root = psutil.disk_usage("/")

    # Temperatura CPU
    cpu_temp = get_cpu_temperature()

    # Uptime
    uptime_seconds = get_uptime_seconds()

    # Red
    net_stats = get_network_stats()

    # Servicios
    services = get_service_statuses()

    # Relación carga / núcleos (load ratio)
    load_ratio = load1 / cpu_count if cpu_count else 0.0

    metrics = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "cpu": {
            "percent": cpu_percent,
            "count": cpu_count,
            "load_1min": load1,
            "load_5min": load5,
            "load_15min": load15,
            "load_ratio": load_ratio,
            "temperature_c": cpu_temp,
        },
        "memory": {
            "total_bytes": vm.total,
            "used_bytes": vm.used,
            "available_bytes": vm.available,
            "percent": vm.percent,
        },
        "swap": {
            "total_bytes": sm.total,
            "used_bytes": sm.used,
            "free_bytes": sm.free,
            "percent": sm.percent,
        },
        "disk_root": {
            "total_bytes": disk_root.total,
            "used_bytes": disk_root.used,
            "free_bytes": disk_root.free,
            "percent": disk_root.percent,
            "mountpoint": "/",
        },
        "network": net_stats,
        "uptime_seconds": uptime_seconds,
        "services": services,
    }

    return metrics


# ---------------------- EVALUACIÓN DE ALERTAS ---------------------- #

def evaluate_metric(name: str, value, thresholds: dict) -> list[dict]:
    """
    Genera alertas (warning/critical) para una métrica concreta
    según los umbrales definidos.
    """
    alerts = []
    cfg = thresholds.get(name)
    if cfg is None or value is None:
        return alerts

    warning = cfg.get("warning")
    critical = cfg.get("critical")

    # Asumimos que umbrales son "mayor que"
    level = None
    if critical is not None and value >= critical:
        level = "CRITICAL"
    elif warning is not None and value >= warning:
        level = "WARNING"

    if level:
        alerts.append({
            "metric": name,
            "level": level,
            "value": value,
            "warning_threshold": warning,
            "critical_threshold": critical,
            "message": f"Métrica {name} = {value} supera umbral de {level.lower()}",
        })

    return alerts


def evaluate_alerts(metrics: dict) -> list[dict]:
    alerts: list[dict] = []

    # CPU %
    alerts += evaluate_metric("cpu_percent", metrics["cpu"]["percent"], THRESHOLDS)

    # Load ratio (load 1min / núcleos)
    alerts += evaluate_metric("load_ratio", metrics["cpu"]["load_ratio"], THRESHOLDS)

    # Memoria
    alerts += evaluate_metric("memory_percent", metrics["memory"]["percent"], THRESHOLDS)

    # Swap
    alerts += evaluate_metric("swap_percent", metrics["swap"]["percent"], THRESHOLDS)

    # Disco raíz
    alerts += evaluate_metric("disk_root_percent", metrics["disk_root"]["percent"], THRESHOLDS)

    # Temperatura CPU (si disponible)
    alerts += evaluate_metric("cpu_temperature", metrics["cpu"]["temperature_c"], THRESHOLDS)

    # Servicios: generar alertas si están "stopped"
    for svc_name, status in metrics["services"].items():
        if status != "running":
            alerts.append({
                "metric": "service_status",
                "level": "WARNING",
                "service": svc_name,
                "value": status,
                "message": f"Servicio {svc_name} no está en ejecución (estado: {status})",
            })

    return alerts


def overall_status(alerts: list[dict]) -> str:
    """
    Calcula un estado global del sistema según las alertas generadas.
    """
    levels = {a["level"] for a in alerts}
    if "CRITICAL" in levels:
        return "CRITICAL"
    if "WARNING" in levels:
        return "WARNING"
    return "OK"


# ---------------------- PUNTO DE ENTRADA ---------------------- #

def main():
    metrics = collect_metrics()
    alerts = evaluate_alerts(metrics)
    status = overall_status(alerts)

    output = {
        "status": status,
        "metrics": metrics,
        "alerts": alerts,
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()

