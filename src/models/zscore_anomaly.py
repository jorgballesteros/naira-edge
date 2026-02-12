"""Detección simple de anomalías para series temporales.

Este módulo implementa un detector basado en una ventana móvil y 
una métrica tipo *z-score*. Está pensado para ejecutarse en hardware
limitado (RPi) sin dependencias externas.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from math import isnan
from statistics import fmean, pstdev
from typing import Deque, Dict, Iterable, Tuple


def _ensure_dt(ts: str | datetime | None) -> datetime:
    """Convierte una marca de tiempo en datetime (UTC)."""
    if isinstance(ts, datetime):
        return ts.astimezone(UTC)
    if isinstance(ts, str):
        value = ts.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(value)
            return parsed.astimezone(UTC)
        except ValueError:
            pass
    return datetime.now(UTC)


def _safe_float(value: float | int | str | None) -> float | None:
    try:
        numeric = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return None if isnan(numeric) else numeric


@dataclass(slots=True)
class RollingAnomalyDetector:
    """Detector simple de anomalías usando ventana fija y z-score."""

    metric: str
    window: timedelta = timedelta(days=3)
    min_samples: int = 48
    z_threshold: float = 3.0
    max_samples: int = 2048
    _samples: Deque[Tuple[datetime, float]] = field(default_factory=deque, init=False)

    def evaluate(self, ts: str | datetime | None, value: float | int | str | None) -> Dict[str, float | int | bool]:
        """Actualiza la ventana y devuelve métricas de anomalía."""
        numeric_value = _safe_float(value)
        if numeric_value is None:
            return self._empty_result()

        ts_dt = _ensure_dt(ts)
        self._trim(ts_dt)
        self._samples.append((ts_dt, numeric_value))
        if len(self._samples) > self.max_samples:
            self._samples.popleft()

        avg, std_dev = self._stats()
        zscore = 0.0 if std_dev == 0.0 else (numeric_value - avg) / std_dev
        window_ready = len(self._samples) >= self.min_samples
        anomaly = window_ready and abs(zscore) >= self.z_threshold

        return {
            f"{self.metric}_window_samples": len(self._samples),
            f"{self.metric}_window_hours": round(self._window_hours(), 2),
            f"{self.metric}_rolling_mean": round(avg, 3),
            f"{self.metric}_rolling_std": round(std_dev, 3),
            f"{self.metric}_zscore": round(zscore, 3),
            f"{self.metric}_anomaly": anomaly,
            f"{self.metric}_window_ready": window_ready,
        }

    def _trim(self, current_ts: datetime) -> None:
        cutoff = current_ts - self.window
        while self._samples and self._samples[0][0] < cutoff:
            self._samples.popleft()

    def _stats(self) -> Tuple[float, float]:
        values: Iterable[float] = (sample[1] for sample in self._samples)
        values_list = list(values)
        if not values_list:
            return 0.0, 0.0
        if len(values_list) == 1:
            return values_list[0], 0.0
        avg = fmean(values_list)
        std_dev = pstdev(values_list)
        return avg, std_dev

    def _window_hours(self) -> float:
        if len(self._samples) < 2:
            return 0.0
        delta = self._samples[-1][0] - self._samples[0][0]
        return max(delta.total_seconds() / 3600.0, 0.0)

    def _empty_result(self) -> Dict[str, float | int | bool]:
        return {
            f"{self.metric}_window_samples": len(self._samples),
            f"{self.metric}_window_hours": self._window_hours(),
            f"{self.metric}_rolling_mean": 0.0,
            f"{self.metric}_rolling_std": 0.0,
            f"{self.metric}_zscore": 0.0,
            f"{self.metric}_anomaly": False,
            f"{self.metric}_window_ready": len(self._samples) >= self.min_samples,
        }


__all__ = ["RollingAnomalyDetector"]
