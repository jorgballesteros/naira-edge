"""CLI to pull the last hour of InfluxDB data and run anomaly detection."""

from __future__ import annotations

import argparse
import json
import logging
from datetime import UTC, timedelta
from typing import Any, Dict, Iterable, List, Sequence

from src.config import load_settings
from src.models.mad_anomaly import RollingMadAnomalyDetector
from src.models.zscore_anomaly import RollingAnomalyDetector

try:  # optional import, keeps the script importable without Influx deps
    from influxdb_client import InfluxDBClient
except ImportError:  # pragma: no cover - optional dependency
    InfluxDBClient = None  # type: ignore[assignment]


logger = logging.getLogger(__name__)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metric", required=True, help="metric tag to query")
    parser.add_argument(
        "--bucket",
        help="bucket override (defaults to settings.influx_bucket_telemetry)",
    )
    parser.add_argument("--measurement", default="naira_samples", help="measurement name")
    parser.add_argument("--node", help="optional node_id tag filter")
    parser.add_argument("--hours", type=float, default=1.0, help="time window to read (hours)")
    parser.add_argument(
        "--window-hours",
        type=float,
        default=72.0,
        help="rolling window for the detector (hours)",
    )
    parser.add_argument(
        "--window-samples",
        type=int,
        default=500,
        help="maximum samples kept in the rolling window",
    )
    parser.add_argument(
        "--min-samples",
        type=int,
        default=72,
        help="minimum samples before enabling anomaly flags",
    )
    parser.add_argument(
        "--z-threshold",
        type=float,
        default=2.5,
        help="absolute z-score threshold marking an anomaly",
    )
    parser.add_argument(
        "--mad-threshold",
        type=float,
        default=3.5,
        help="median absolute deviation threshold for MAD mode",
    )
    parser.add_argument(
        "--method",
        choices=["zscore", "mad"],
        default="zscore",
        help="anomaly detection technique to use",
    )
    parser.add_argument("--limit", type=int, default=5000, help="max Flux rows to fetch")
    parser.add_argument("--log", default="INFO", help="logging level (DEBUG, INFO, ...)")
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit anomalies as JSON to stdout",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    if InfluxDBClient is None:
        logger.error("influxdb-client is not installed. Run 'pip install influxdb-client'.")
        return 2

    settings = load_settings()
    bucket = args.bucket or settings.influx_bucket_telemetry or settings.influx_bucket
    if not bucket:
        logger.error("Missing bucket configuration. Set NAIRA_INFLUX_BUCKET(_TELEMETRY).")
        return 2

    if not settings.influx_url or not settings.influx_token or not settings.influx_org:
        logger.error("InfluxDB connection parameters are incomplete in config.")
        return 2

    try:
        with InfluxDBClient(url=settings.influx_url, token=settings.influx_token, org=settings.influx_org) as client:
            samples = fetch_metric_samples(
                client=client,
                org=settings.influx_org,
                bucket=bucket,
                measurement=args.measurement,
                metric=args.metric,
                hours=args.hours,
                limit=args.limit,
                node_id=args.node,
            )
    except Exception as exc:  # pragma: no cover - network dependent
        logger.error("Error querying InfluxDB: %s", exc)
        return 2

    if not samples:
        logger.warning("No samples found for metric=%s within last %sh", args.metric, args.hours)
        return 1

    anomalies, last_state = detect_anomalies(
        samples,
        metric=args.metric,
        window_hours=args.window_hours,
        window_samples=args.window_samples,
        min_samples=args.min_samples,
        z_threshold=args.z_threshold,
        mad_threshold=args.mad_threshold,
        method=args.method,
    )

    ready_key = (
        f"{args.metric}_window_ready"
        if args.method == "zscore"
        else f"{args.metric}_mad_window_ready"
    )
    score_key = f"{args.metric}_zscore" if args.method == "zscore" else f"{args.metric}_mad_score"
    logger.info(
        "Evaluated %d samples; window_ready=%s, score=%.3f",
        len(samples),
        bool(last_state.get(ready_key)),
        last_state.get(score_key, 0.0),
    )

    anomaly_key = f"{args.metric}_anomaly" if args.method == "zscore" else f"{args.metric}_mad_anomaly"
    if anomalies:
        for entry in anomalies:
            logger.warning(
                "Anomaly metric=%s ts=%s value=%s score=%.3f",
                args.metric,
                entry["ts"],
                entry["value"],
                entry.get(score_key, 0.0),
            )
    else:
        logger.info("No anomalies detected for metric=%s in the requested window.", args.metric)

    if args.json and anomalies:
        print(json.dumps(anomalies, ensure_ascii=True, indent=2))

    return 0


def fetch_metric_samples(
    *,
    client: "InfluxDBClient",
    org: str,
    bucket: str,
    measurement: str,
    metric: str,
    hours: float,
    limit: int,
    node_id: str | None = None,
) -> List[Dict[str, Any]]:
    """Query InfluxDB and return samples sorted chronologically."""

    flux = _build_flux_query(
        bucket=bucket,
        measurement=measurement,
        metric=metric,
        hours=hours,
        limit=limit,
        node_id=node_id,
    )
    logger.debug("Flux query executed:\n%s", flux)
    tables = client.query_api().query(org=org, query=flux)

    samples: List[Dict[str, Any]] = []
    for table in tables:
        for record in table.records:
            samples.append(
                {
                    "ts": record.get_time().astimezone(UTC).isoformat().replace("+00:00", "Z"),
                    "value": record.get_value(),
                    "node_id": record.values.get("node_id"),
                    "metric": record.values.get("metric"),
                    "source": record.values.get("source"),
                    "unit": record.values.get("unit"),
                    "quality": record.values.get("quality", "ok"),
                }
            )
    samples.sort(key=lambda item: item["ts"])
    return samples


def detect_anomalies(
    samples: Iterable[Dict[str, Any]],
    *,
    metric: str,
    window_hours: float,
    window_samples: int,
    min_samples: int,
    z_threshold: float,
    mad_threshold: float,
    method: str,
) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    if method == "mad":
        detector = RollingMadAnomalyDetector(
            metric=metric,
            window=timedelta(hours=window_hours),
            min_samples=min_samples,
            mad_threshold=mad_threshold,
            max_samples=max(window_samples, min_samples),
        )
        anomaly_key = f"{metric}_mad_anomaly"
    else:
        detector = RollingAnomalyDetector(
            metric=metric,
            window=timedelta(hours=window_hours),
            min_samples=min_samples,
            z_threshold=z_threshold,
            max_samples=max(window_samples, min_samples),
        )
        anomaly_key = f"{metric}_anomaly"
    anomalies: List[Dict[str, Any]] = []
    last_state: Dict[str, Any] = {}
    for sample in samples:
        last_state = detector.evaluate(sample.get("ts"), sample.get("value"))
        if last_state.get(anomaly_key):
            enriched = dict(sample)
            enriched.update(last_state)
            anomalies.append(enriched)
    return anomalies, last_state


def _build_flux_query(
    *,
    bucket: str,
    measurement: str,
    metric: str,
    hours: float,
    limit: int,
    node_id: str | None = None,
) -> str:
    bucket_s = _flux_string(bucket)
    meas_s = _flux_string(measurement)
    metric_s = _flux_string(metric)
    duration = _format_duration(hours)
    query_lines = [
        f'from(bucket: "{bucket_s}")',
        f"  |> range(start: -{duration})",
        f'  |> filter(fn: (r) => r["_measurement"] == "{meas_s}")',
        f'  |> filter(fn: (r) => r["metric"] == "{metric_s}")',
        '  |> filter(fn: (r) => r["_field"] == "value")',
    ]
    if node_id:
        query_lines.append(f'  |> filter(fn: (r) => r["node_id"] == "{_flux_string(node_id)}")')
    query_lines.append('  |> sort(columns: ["_time"])')
    if limit > 0:
        query_lines.append(f"  |> limit(n: {limit})")
    return "\n".join(query_lines)


def _flux_string(value: str) -> str:
    return value.replace('"', '\\"')


def _format_duration(hours: float) -> str:
    total_seconds = max(int(hours * 3600), 1)
    hrs, rem = divmod(total_seconds, 3600)
    mins, secs = divmod(rem, 60)
    parts: List[str] = []
    if hrs:
        parts.append(f"{hrs}h")
    if mins:
        parts.append(f"{mins}m")
    if secs or not parts:
        parts.append(f"{secs}s")
    return "".join(parts)


if __name__ == "__main__":
    raise SystemExit(main())
