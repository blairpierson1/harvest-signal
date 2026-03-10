"""Tests for producer risk classification."""

from app.models import WeatherRisk
from app.producers import _classify_risk


class TestClassifyRisk:
    """Tests for _classify_risk()."""

    def test_alert_when_temp_exceeds_alert_threshold(self):
        """Temp max above alert threshold should classify as Alert."""
        weather = {
            "temperature_avg": 30.0,
            "temperature_max": 35.0,  # above Coffee temp_alert (32.0)
            "precipitation_daily_avg": 5.0,
            "relative_humidity": 70.0,
        }
        risk, detail = _classify_risk("Coffee", weather)
        assert risk == WeatherRisk.ALERT
        assert "Extreme heat" in detail

    def test_watch_when_precip_below_watch_but_above_alert(self):
        """Precip below watch threshold but above alert should classify as Watch."""
        weather = {
            "temperature_avg": 24.0,
            "temperature_max": 26.0,  # below watch threshold
            "precipitation_daily_avg": 1.5,  # below precip_low_watch (2.0) but above precip_low_alert (1.0)
            "relative_humidity": 70.0,
        }
        risk, detail = _classify_risk("Coffee", weather)
        assert risk == WeatherRisk.WATCH
        assert "Below-avg rainfall" in detail

    def test_normal_when_all_values_in_range(self):
        """All values within normal range should classify as Normal."""
        weather = {
            "temperature_avg": 24.0,
            "temperature_max": 26.0,
            "precipitation_daily_avg": 5.0,
            "relative_humidity": 70.0,
        }
        risk, detail = _classify_risk("Coffee", weather)
        assert risk == WeatherRisk.NORMAL
        assert detail == "Conditions within normal range"
