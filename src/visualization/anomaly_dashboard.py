"""Streamlit dashboard to visualize anomaly detections from InfluxDB."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import pandas as pd
import streamlit as st

try:
    from src.config import Settings, load_settings
    from src.tools import influx_anomaly
except ModuleNotFoundError:  # pragma: no cover - Streamlit runner safeguard
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.append(str(PROJECT_ROOT))
    from src.config import Settings, load_settings
    from src.tools import influx_anomaly

logger = logging.getLogger(__name__)

def _fetch_and_detect(
    *,
    settings: Settings,
    metric: str,
    measurement: str,
    bucket: str,
    node_id: str | None,
    hours: float,
    limit: int,
    method: str,
    window_hours: float,
    window_samples: int,
    min_samples: int,
    z_threshold: float,
    mad_threshold: float,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    client_cls = influx_anomaly.InfluxDBClient
    if client_cls is None:  # pragma: no cover - safeguarded in UI
        raise RuntimeError("La dependencia influxdb-client no está disponible.")

    with client_cls(url=settings.influx_url, token=settings.influx_token, org=settings.influx_org) as client:
        samples = influx_anomaly.fetch_metric_samples(
            client=client,
            org=settings.influx_org,
            bucket=bucket,
            measurement=measurement,
            metric=metric,
            hours=hours,
            limit=limit,
            node_id=node_id,
        )

    anomalies, last_state = influx_anomaly.detect_anomalies(
        samples,
        metric=metric,
        window_hours=window_hours,
        window_samples=max(window_samples, min_samples),
        min_samples=min_samples,
        z_threshold=z_threshold,
        mad_threshold=mad_threshold,
        method=method,
    )
    return samples, anomalies, last_state


def _build_series_df(samples: Sequence[Dict[str, Any]], anomalies: Sequence[Dict[str, Any]]) -> pd.DataFrame:
    if not samples:
        return pd.DataFrame()
    df = pd.DataFrame(samples).copy()
    df["ts_raw"] = df["ts"]
    df["ts"] = pd.to_datetime(df["ts"], utc=True, errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    anomaly_ts = {item["ts"] for item in anomalies}
    df["is_anomaly"] = df["ts_raw"].isin(anomaly_ts)
    df.sort_values("ts", inplace=True)
    df.set_index("ts", inplace=True)
    df.drop(columns=["ts_raw"], inplace=True)
    return df


def _build_anomaly_df(anomalies: Sequence[Dict[str, Any]], score_key: str) -> pd.DataFrame:
    if not anomalies:
        return pd.DataFrame()
    df = pd.DataFrame(anomalies).copy()
    df = df[[col for col in ("ts", "value", score_key, "node_id", "quality", "source") if col in df.columns]]
    df.sort_values("ts", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


st.set_page_config(page_title="NAIRA · Anomalías", layout="wide")
st.title("NAIRA · Panel de anomalías")

settings = load_settings()

if influx_anomaly.InfluxDBClient is None:  # pragma: no cover - UI guard
    st.error("Falta la dependencia 'influxdb-client'. Instala requisitos antes de continuar.")
    st.stop()

if not settings.influx_url or not settings.influx_token or not settings.influx_org:
    st.error("Configura NAIRA_INFLUX_URL / TOKEN / ORG en el entorno antes de usar el panel.")
    st.stop()

DEFAULT_BUCKET = settings.influx_bucket_telemetry or settings.influx_bucket
if not DEFAULT_BUCKET:
    st.error("Configura NAIRA_INFLUX_BUCKET o NAIRA_INFLUX_BUCKET_TELEMETRY.")
    st.stop()

with st.sidebar:
    st.header("Consulta InfluxDB")
    metric = st.text_input("Métrica", value="soil_moisture_pct")
    node_id = st.text_input("Node ID (opcional)", value=settings.node_id)
    measurement = st.text_input("Measurement", value="naira_samples")
    bucket = st.text_input("Bucket", value=DEFAULT_BUCKET)
    hours = st.slider("Ventana de lectura (h)", min_value=1, max_value=168, value=24)
    limit = st.number_input("Límite de filas", min_value=100, max_value=20000, value=5000, step=100)
    st.header("Detector")
    method = st.selectbox("Método", options=("zscore", "mad"), index=0)
    window_hours = st.slider("Ventana rolling (h)", min_value=6, max_value=240, value=72, step=6)
    min_samples = st.number_input("Mínimo muestras en ventana", min_value=10, max_value=2000, value=72, step=2)
    window_samples = st.number_input("Máximo muestras almacenadas", min_value=100, max_value=10000, value=720, step=20)
    if method == "zscore":
        z_threshold = st.slider("Umbral z-score", min_value=1.0, max_value=6.0, value=2.5, step=0.1)
        mad_threshold = 3.5
    else:
        mad_threshold = st.slider("Umbral MAD", min_value=1.0, max_value=10.0, value=3.5, step=0.5)
        z_threshold = 2.5

if not metric.strip():
    st.info("Define una métrica para consultar InfluxDB.")
    st.stop()

if not bucket.strip():
    st.info("Especifica el bucket que contiene las muestras normalizadas.")
    st.stop()

try:
    with st.spinner("Consultando InfluxDB y evaluando la ventana..."):
        samples, anomalies, last_state = \
            _fetch_and_detect(
                settings=settings,
                metric=metric.strip(),
                measurement=measurement.strip() or "naira_samples",
                bucket=bucket.strip(),
                node_id=node_id.strip() or None,
                hours=float(hours),
                limit=int(limit),
                method=method,
                window_hours=float(window_hours),
                window_samples=int(window_samples),
                min_samples=int(min_samples),
                z_threshold=float(z_threshold),
                mad_threshold=float(mad_threshold),
            )
except Exception as exc:  # pragma: no cover - interactive UI
    logger.exception("Error consultando InfluxDB")
    st.error(f"No fue posible leer datos o evaluar el detector: {exc}")
    st.stop()

if not samples:
    st.warning("No se encontraron muestras para la métrica seleccionada en la ventana solicitada.")
    st.stop()

ready_key = f"{metric}_window_ready" if method == "zscore" else f"{metric}_mad_window_ready"
score_key = f"{metric}_zscore" if method == "zscore" else f"{metric}_mad_score"
anomaly_key = f"{metric}_anomaly" if method == "zscore" else f"{metric}_mad_anomaly"

c1, c2, c3, c4 = st.columns(4)
c1.metric("Muestras leídas", len(samples))
c2.metric("Anomalías", len(anomalies))
c3.metric("Score actual", f"{float(last_state.get(score_key, 0.0)):.3f}")
c4.metric("Ventana lista", "Sí" if last_state.get(ready_key) else "No")

series_df = _build_series_df(samples, anomalies)

st.subheader("Serie temporal")
st.line_chart(series_df["value"], height=300)

st.subheader("Anomalías detectadas")
if anomalies:
    anomalies_df = _build_anomaly_df(anomalies, score_key)
    st.dataframe(anomalies_df, use_container_width=True)
else:
    st.success("Sin anomalías en la ventana consultada.")

with st.expander("Últimas muestras (orden cronológico)"):
    preview_cols = [col for col in ("value", "quality", "source", "unit", "node_id", "is_anomaly") if col in series_df.columns]
    st.dataframe(series_df[preview_cols].tail(200), use_container_width=True)

with st.expander("Estado del detector"):
    st.json(last_state)


def _fetch_and_detect(
    *,
    settings: Settings,
    metric: str,
    measurement: str,
    bucket: str,
    node_id: str | None,
    hours: float,
    limit: int,
    method: str,
    window_hours: float,
    window_samples: int,
    min_samples: int,
    z_threshold: float,
    mad_threshold: float,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    client_cls = influx_anomaly.InfluxDBClient
    if client_cls is None:  # pragma: no cover - safeguarded in UI
        raise RuntimeError("La dependencia influxdb-client no está disponible.")

    with client_cls(url=settings.influx_url, token=settings.influx_token, org=settings.influx_org) as client:
        samples = influx_anomaly.fetch_metric_samples(
            client=client,
            org=settings.influx_org,
            bucket=bucket,
            measurement=measurement,
            metric=metric,
            hours=hours,
            limit=limit,
            node_id=node_id,
        )

    anomalies, last_state = influx_anomaly.detect_anomalies(
        samples,
        metric=metric,
        window_hours=window_hours,
        window_samples=max(window_samples, min_samples),
        min_samples=min_samples,
        z_threshold=z_threshold,
        mad_threshold=mad_threshold,
        method=method,
    )
    return samples, anomalies, last_state


def _build_series_df(samples: Sequence[Dict[str, Any]], anomalies: Sequence[Dict[str, Any]]) -> pd.DataFrame:
    if not samples:
        return pd.DataFrame()
    df = pd.DataFrame(samples).copy()
    df["ts_raw"] = df["ts"]
    df["ts"] = pd.to_datetime(df["ts"], utc=True, errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    anomaly_ts = {item["ts"] for item in anomalies}
    df["is_anomaly"] = df["ts_raw"].isin(anomaly_ts)
    df.sort_values("ts", inplace=True)
    df.set_index("ts", inplace=True)
    df.drop(columns=["ts_raw"], inplace=True)
    return df


def _build_anomaly_df(anomalies: Sequence[Dict[str, Any]], score_key: str) -> pd.DataFrame:
    if not anomalies:
        return pd.DataFrame()
    df = pd.DataFrame(anomalies).copy()
    df = df[[col for col in ("ts", "value", score_key, "node_id", "quality", "source") if col in df.columns]]
    df.sort_values("ts", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df
