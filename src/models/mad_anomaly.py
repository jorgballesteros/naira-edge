"""Median absolute deviation based anomaly detector."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from math import isnan
from statistics import median
from typing import Deque, Dict, Iterable, Tuple


def _ensure_dt(ts: str | datetime | None) -> datetime:
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
class RollingMadAnomalyDetector:
    """Sliding window anomaly detector using median absolute deviation."""

    metric: str
    window: timedelta = timedelta(days=3)
    min_samples: int = 48
    mad_threshold: float = 3.5
    max_samples: int = 2048
    scale_factor: float = 1.4826  # approx to convert MAD into stddev for normal dist
    _samples: Deque[Tuple[datetime, float]] = field(default_factory=deque, init=False)

    def evaluate(self, ts: str | datetime | None, value: float | int | str | None) -> Dict[str, float | int | bool]:
        numeric_value = _safe_float(value)
        if numeric_value is None:
            return self._empty_result()

        ts_dt = _ensure_dt(ts)
        self._trim(ts_dt)
        self._samples.append((ts_dt, numeric_value))
        if len(self._samples) > self.max_samples:
            self._samples.popleft()

        med, mad = self._stats()
        scaled = self.scale_factor * mad
        if scaled == 0.0:
            diff = numeric_value - med
            mad_score = 0.0 if diff == 0.0 else self.mad_threshold + abs(diff)
        else:
            mad_score = (numeric_value - med) / scaled
        window_ready = len(self._samples) >= self.min_samples
        anomaly = window_ready and abs(mad_score) >= self.mad_threshold

        return {
            f"{self.metric}_mad_window_samples": len(self._samples),
            f"{self.metric}_mad_window_hours": round(self._window_hours(), 2),
            f"{self.metric}_mad_median": round(med, 3),
            f"{self.metric}_mad_deviation": round(mad, 3),
            f"{self.metric}_mad_score": round(mad_score, 3),
            f"{self.metric}_mad_anomaly": anomaly,
            f"{self.metric}_mad_window_ready": window_ready,
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
        med = median(values_list)
        deviations = [abs(sample - med) for sample in values_list]
        mad = median(deviations)
        return med, mad

    def _window_hours(self) -> float:
        if len(self._samples) < 2:
            return 0.0
        delta = self._samples[-1][0] - self._samples[0][0]
        return max(delta.total_seconds() / 3600.0, 0.0)

    def _empty_result(self) -> Dict[str, float | int | bool]:
        return {
            f"{self.metric}_mad_window_samples": len(self._samples),
            f"{self.metric}_mad_window_hours": self._window_hours(),
            f"{self.metric}_mad_median": 0.0,
            f"{self.metric}_mad_deviation": 0.0,
            f"{self.metric}_mad_score": 0.0,
            f"{self.metric}_mad_anomaly": False,
            f"{self.metric}_mad_window_ready": len(self._samples) >= self.min_samples,
        }


__all__ = ["RollingMadAnomalyDetector"]
