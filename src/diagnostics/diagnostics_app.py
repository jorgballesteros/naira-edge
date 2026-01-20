import logging
import os
import time
from collections import deque
from datetime import datetime

import psutil
import streamlit as st

from .telegram_alert import create_alert_manager

logger = logging.getLogger(__name__)


# ---------- Helpers ----------
def read_cpu_temp_c() -> float | None:
    """
    Raspberry Pi: lee /sys/class/thermal/thermal_zone0/temp si existe.
    Devuelve ºC o None si no está disponible.
    """
    path = "/sys/class/thermal/thermal_zone0/temp"
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read().strip()
        return float(raw) / 1000.0
    except Exception:
        return None


def read_uptime_s() -> float | None:
    """Lee uptime de /proc/uptime (segundos)."""
    try:
        with open("/proc/uptime", "r", encoding="utf-8") as f:
            return float(f.read().split()[0])
    except Exception:
        return None


def has_default_route() -> bool:
    """
    Heurística simple: si existe una interfaz 'up' con IP y hay gateway probable.
    Sin dependencias externas (ip route).
    """
    try:
        stats = psutil.net_if_stats()
        addrs = psutil.net_if_addrs()
        for ifname, s in stats.items():
            if not s.isup:
                continue
            # IPv4 address present?
            for a in addrs.get(ifname, []):
                if getattr(a, "family", None) == 2 and a.address and a.address != "127.0.0.1":
                    return True
        return False
    except Exception:
        return False


def bytes_to_human(n: float) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while n >= 1024 and i < len(units) - 1:
        n /= 1024
        i += 1
    return f"{n:.2f} {units[i]}"


def check_alerts(cpu_pct: float, ram_pct: float, disk_pct: float, temp_c: float | None,
                 cpu_threshold: float, ram_threshold: float, disk_threshold: float, temp_threshold: float) -> dict:
    """Verifica si las métricas exceden los umbrales y devuelve un dict de alertas."""
    alerts = {}
    if cpu_pct >= cpu_threshold:
        alerts["cpu"] = f"CPU alto: {cpu_pct:.1f}%"
    if ram_pct >= ram_threshold:
        alerts["ram"] = f"RAM alta: {ram_pct:.1f}%"
    if disk_pct >= disk_threshold:
        alerts["disk"] = f"Disco casi lleno: {disk_pct:.1f}%"
    if temp_c is not None and temp_c >= temp_threshold:
        alerts["temp"] = f"Temperatura alta: {temp_c:.1f}°C"
    return alerts


# ---------- Streamlit UI ----------
st.set_page_config(page_title="NAIRA - Diagnóstico Nodo RPi", layout="wide")

st.title("NAIRA · Diagnóstico del nodo (Raspberry Pi)")

# Controles
with st.sidebar:
    st.header("Controles")
    refresh_s = st.slider("Intervalo de refresco (s)", 1, 10, 2)
    history_len = st.slider("Longitud histórico (puntos)", 30, 300, 120, step=30)
    st.caption("Tip: Para un prototipo estable, 2–3 s es suficiente.")
    
    st.divider()
    st.header("⚠️ Umbrales de Alerta")
    cpu_alert_pct = st.slider("CPU alerta (%)", 50, 100, 80)
    ram_alert_pct = st.slider("RAM alerta (%)", 50, 100, 85)
    disk_alert_pct = st.slider("Disco alerta (%)", 70, 100, 90)
    temp_alert_c = st.slider("Temperatura alerta (°C)", 40, 85, 70)

# Estado en sesión: histórico
if "ts_hist" not in st.session_state:
    st.session_state.ts_hist = deque(maxlen=history_len)
    st.session_state.cpu_hist = deque(maxlen=history_len)
    st.session_state.temp_hist = deque(maxlen=history_len)
    st.session_state.ram_hist = deque(maxlen=history_len)
    st.session_state.rx_hist = deque(maxlen=history_len)
    st.session_state.tx_hist = deque(maxlen=history_len)

# Si cambia history_len, actualiza maxlen manteniendo valores
def resize_deque(dq: deque, new_len: int) -> deque:
    new = deque(dq, maxlen=new_len)
    return new

for key in ["ts_hist", "cpu_hist", "temp_hist", "ram_hist", "rx_hist", "tx_hist"]:
    st.session_state[key] = resize_deque(st.session_state[key], history_len)

# Lectura de métricas (snapshot)
cpu_pct = psutil.cpu_percent(interval=0.2)
cpu_freq = psutil.cpu_freq()
temp_c = read_cpu_temp_c()

vm = psutil.virtual_memory()
sm = psutil.swap_memory()
disk = psutil.disk_usage("/")

net0 = psutil.net_io_counters()
uptime_s = read_uptime_s()
online = has_default_route()

# Guardar en histórico
now = datetime.now()
st.session_state.ts_hist.append(now)
st.session_state.cpu_hist.append(cpu_pct)
st.session_state.temp_hist.append(temp_c if temp_c is not None else float("nan"))
st.session_state.ram_hist.append(vm.percent)
st.session_state.rx_hist.append(net0.bytes_recv)
st.session_state.tx_hist.append(net0.bytes_sent)

# Verificar alertas activas
alerts = check_alerts(cpu_pct, vm.percent, disk.percent, temp_c,
                      cpu_alert_pct, ram_alert_pct, disk_alert_pct, temp_alert_c)

# Enviar alertas por Telegram si están configuradas
try:
    alert_manager = create_alert_manager()
    if alert_manager.bot_token and alert_manager.chat_id:
        alert_manager.check_all(
            temp_c=temp_c,
            cpu_pct=cpu_pct,
            ram_pct=vm.percent,
            disk_pct=disk.percent,
        )
except Exception as e:
    logger.warning(f"Error enviando alertas Telegram: {e}")

# Layout: KPIs
c1, c2, c3, c4, c5, c6 = st.columns(6)

# Función helper para colorear métricas
def get_metric_color(value: float, threshold: float) -> str:
    return "🔴" if value >= threshold else "🟢"

c1.metric("CPU (%)", f"{cpu_pct:.1f}", delta=f"{get_metric_color(cpu_pct, cpu_alert_pct)}")
c2.metric("RAM (%)", f"{vm.percent:.1f}", delta=f"{get_metric_color(vm.percent, ram_alert_pct)}")
c3.metric("Disco (%)", f"{disk.percent:.1f}", delta=f"{get_metric_color(disk.percent, disk_alert_pct)}")
c4.metric("Temp (°C)", "N/A" if temp_c is None else f"{temp_c:.1f}", 
          delta=("N/A" if temp_c is None else get_metric_color(temp_c, temp_alert_c)))
c5.metric("Red", "Online" if online else "Sin salida")
if uptime_s is None:
    c6.metric("Uptime", "N/A")
else:
    hours = int(uptime_s // 3600)
    mins = int((uptime_s % 3600) // 60)
    c6.metric("Uptime", f"{hours}h {mins}m")

# Detalle
st.divider()

# Panel de alertas activas
if alerts:
    st.warning("⚠️ **Alertas Activas:**")
    for key, msg in alerts.items():
        st.error(f"  • {msg}")
else:
    st.success("✅ Sistema operativo — sin alertas")

st.divider()
left, right = st.columns([1, 1])

with left:
    st.subheader("Estado del sistema")
    st.write(
        {
            "CPU_freq_MHz": None if not cpu_freq else round(cpu_freq.current, 1),
            "RAM_used": bytes_to_human(vm.used),
            "RAM_total": bytes_to_human(vm.total),
            "Swap_used": bytes_to_human(sm.used),
            "Disk_used": bytes_to_human(disk.used),
            "Disk_total": bytes_to_human(disk.total),
        }
    )

with right:
    st.subheader("Red (contadores acumulados)")
    st.write(
        {
            "RX_total": bytes_to_human(net0.bytes_recv),
            "TX_total": bytes_to_human(net0.bytes_sent),
            "Packets_RX": net0.packets_recv,
            "Packets_TX": net0.packets_sent,
        }
    )

# Gráficas simples (Streamlit line_chart)
st.divider()
g1, g2, g3 = st.columns(3)

with g1:
    st.subheader("CPU (%)")
    st.line_chart(list(st.session_state.cpu_hist))

with g2:
    st.subheader("RAM (%)")
    st.line_chart(list(st.session_state.ram_hist))

with g3:
    st.subheader("Temperatura (°C)")
    # si temp es nan se verá “hueco”; ok para prototipo
    st.line_chart(list(st.session_state.temp_hist))

# Autorefresco simple
time.sleep(refresh_s)
st.rerun()
