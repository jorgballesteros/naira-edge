from datetime import UTC, datetime, timedelta

from src.models.mad_anomaly import RollingMadAnomalyDetector


def test_mad_detector_flags_large_outlier() -> None:
    detector = RollingMadAnomalyDetector(metric="temp", window=timedelta(hours=4), min_samples=5, mad_threshold=3.0)
    base = datetime(2025, 1, 1, tzinfo=UTC)

    for idx in range(5):
        result = detector.evaluate(base + timedelta(minutes=idx), 20.0)
        assert result["temp_mad_anomaly"] is False
        assert result["temp_mad_window_ready"] is (idx + 1 >= 5)

    spike = detector.evaluate(base + timedelta(minutes=10), 45.0)
    assert spike["temp_mad_window_ready"] is True
    assert spike["temp_mad_anomaly"] is True
    assert spike["temp_mad_score"] > 3.0


def test_mad_detector_handles_identical_values() -> None:
    detector = RollingMadAnomalyDetector(metric="temp", mad_threshold=3.0)
    base = datetime(2025, 1, 1, tzinfo=UTC)

    for idx in range(3):
        state = detector.evaluate(base + timedelta(minutes=idx), 18.0)
        assert state["temp_mad_deviation"] == 0.0
        assert state["temp_mad_anomaly"] is False
