from datetime import UTC, datetime, timedelta

from src.models.zscore_anomaly import RollingAnomalyDetector


def test_detector_flags_anomaly_after_window() -> None:
    detector = RollingAnomalyDetector(metric="soil", window=timedelta(days=3), min_samples=5, z_threshold=1.0)
    base = datetime(2025, 1, 1, tzinfo=UTC)

    for idx in range(5):
        result = detector.evaluate(base + timedelta(hours=idx), 10.0)
        assert result["soil_window_samples"] == idx + 1
        assert result["soil_anomaly"] is False
        assert result["soil_window_ready"] is (idx + 1 >= 5)

    anomaly = detector.evaluate(base + timedelta(hours=6), 25.0)
    assert anomaly["soil_window_ready"] is True
    assert anomaly["soil_anomaly"] is True
    assert anomaly["soil_zscore"] > 1.0


def test_detector_handles_missing_values_gracefully() -> None:
    detector = RollingAnomalyDetector(metric="soil")
    base = datetime(2025, 1, 1, tzinfo=UTC)

    blank = detector.evaluate(base, None)
    assert blank["soil_anomaly"] is False

    detector.evaluate(base + timedelta(hours=1), 5.0)
    detector.evaluate(base + timedelta(hours=2), 5.0)
    ok = detector.evaluate(base + timedelta(hours=3), 5.0)
    assert ok["soil_rolling_std"] == 0.0
    assert ok["soil_anomaly"] is False
