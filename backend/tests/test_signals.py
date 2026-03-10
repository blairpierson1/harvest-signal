"""Tests for signal generation logic."""

from app.signals import analyze_region, generate_commodity_signal, generate_condition_summary


class TestAnalyzeRegion:
    """Tests for analyze_region()."""

    def test_drought_detection(self):
        """Low precip + low humidity + high temp should produce high drought_score."""
        region = {
            "region_name": "Test Region",
            "country": "Brazil",
            "precipitation_daily_avg": 0.5,  # well below Coffee precip_low (1.5)
            "temperature_max": 28.0,
            "temperature_avg": 31.0,  # above Coffee temp_high (30.0)
            "relative_humidity": 40.0,  # below Coffee humidity_low (50.0)
        }
        result = analyze_region("Coffee", region)
        # precip < 1.5 -> +2, humidity < 50 -> +1, temp_avg > 30 -> +1 = 4
        assert result["drought_score"] >= 3

    def test_flood_detection(self):
        """High precip + high humidity should produce high flood_score."""
        region = {
            "region_name": "Test Region",
            "country": "Brazil",
            "precipitation_daily_avg": 16.0,  # above Coffee precip_high (12.0)
            "temperature_max": 25.0,
            "temperature_avg": 22.0,
            "relative_humidity": 92.0,  # above Coffee humidity_high (88.0)
        }
        result = analyze_region("Coffee", region)
        # precip > 12 -> +2, humidity > 88 -> +1 = 3
        assert result["flood_score"] >= 2

    def test_heat_stress_detection(self):
        """Temp max above threshold should produce heat_score = 2."""
        region = {
            "region_name": "Test Region",
            "country": "Brazil",
            "precipitation_daily_avg": 5.0,
            "temperature_max": 40.0,  # well above Coffee heat_stress (33.0)
            "temperature_avg": 25.0,
            "relative_humidity": 70.0,
        }
        result = analyze_region("Coffee", region)
        assert result["heat_score"] == 2

    def test_normal_conditions(self):
        """Normal values should produce all scores = 0."""
        region = {
            "region_name": "Test Region",
            "country": "Brazil",
            "precipitation_daily_avg": 5.0,  # well above precip_low
            "temperature_max": 25.0,  # below heat_stress threshold
            "temperature_avg": 22.0,  # below temp_high
            "relative_humidity": 70.0,  # above humidity_low, below humidity_high
        }
        result = analyze_region("Coffee", region)
        assert result["drought_score"] == 0
        assert result["flood_score"] == 0
        assert result["heat_score"] == 0


class TestGenerateCommoditySignal:
    """Tests for generate_commodity_signal()."""

    def test_bullish_drought(self):
        """Regions with drought scores >= 5 total should produce Bullish signal."""
        regions = [
            {
                "region_name": "Region A",
                "country": "Brazil",
                "precipitation_daily_avg": 0.5,
                "temperature_max": 28.0,
                "temperature_avg": 31.0,
                "relative_humidity": 40.0,
            },
            {
                "region_name": "Region B",
                "country": "Vietnam",
                "precipitation_daily_avg": 0.8,
                "temperature_max": 28.0,
                "temperature_avg": 31.0,
                "relative_humidity": 45.0,
            },
        ]
        signal, confidence, key_driver, rationale = generate_commodity_signal(
            "Coffee", regions
        )
        assert signal.value == "Bullish"

    def test_bearish_flood(self):
        """Regions with flood scores >= 4 total should produce Bearish signal."""
        regions = [
            {
                "region_name": "Region A",
                "country": "Brazil",
                "precipitation_daily_avg": 16.0,
                "temperature_max": 25.0,
                "temperature_avg": 22.0,
                "relative_humidity": 92.0,
            },
            {
                "region_name": "Region B",
                "country": "Vietnam",
                "precipitation_daily_avg": 15.0,
                "temperature_max": 25.0,
                "temperature_avg": 22.0,
                "relative_humidity": 90.0,
            },
        ]
        signal, confidence, key_driver, rationale = generate_commodity_signal(
            "Coffee", regions
        )
        assert signal.value == "Bearish"

    def test_neutral(self):
        """Normal conditions across all regions should produce Neutral signal."""
        regions = [
            {
                "region_name": "Region A",
                "country": "Brazil",
                "precipitation_daily_avg": 5.0,
                "temperature_max": 25.0,
                "temperature_avg": 22.0,
                "relative_humidity": 70.0,
            },
            {
                "region_name": "Region B",
                "country": "Vietnam",
                "precipitation_daily_avg": 6.0,
                "temperature_max": 26.0,
                "temperature_avg": 23.0,
                "relative_humidity": 72.0,
            },
        ]
        signal, confidence, key_driver, rationale = generate_commodity_signal(
            "Coffee", regions
        )
        assert signal.value == "Neutral"


class TestGenerateConditionSummary:
    """Tests for generate_condition_summary()."""

    def test_severe_drought(self):
        analysis = {"drought_score": 4, "flood_score": 0, "heat_score": 0}
        assert generate_condition_summary(analysis) == "Severe drought conditions"

    def test_dry_conditions(self):
        analysis = {"drought_score": 2, "flood_score": 0, "heat_score": 0}
        assert generate_condition_summary(analysis) == "Dry conditions, below-average rainfall"

    def test_heavy_rainfall(self):
        analysis = {"drought_score": 0, "flood_score": 2, "heat_score": 0}
        assert generate_condition_summary(analysis) == "Heavy rainfall, potential flooding"

    def test_above_avg_rainfall(self):
        analysis = {"drought_score": 0, "flood_score": 1, "heat_score": 0}
        assert generate_condition_summary(analysis) == "Above-average rainfall"

    def test_extreme_heat(self):
        analysis = {"drought_score": 0, "flood_score": 0, "heat_score": 2}
        assert generate_condition_summary(analysis) == "Extreme heat stress"

    def test_elevated_temps(self):
        analysis = {"drought_score": 0, "flood_score": 0, "heat_score": 1}
        assert generate_condition_summary(analysis) == "Elevated temperatures"

    def test_normal(self):
        analysis = {"drought_score": 0, "flood_score": 0, "heat_score": 0}
        assert generate_condition_summary(analysis) == "Normal growing conditions"
