"""Tests for weather data parsing."""

from app.weather import parse_weather_data


class TestParseWeatherData:
    """Tests for parse_weather_data()."""

    def test_valid_response(self):
        """Valid Open-Meteo response structure should be parsed correctly."""
        data = {
            "daily": {
                "temperature_2m_mean": [24.0, 25.0, 23.0, 26.0, 24.5, 25.5, 24.0],
                "temperature_2m_max": [30.0, 31.0, 29.0, 32.0, 30.5, 31.5, 30.0],
                "precipitation_sum": [2.0, 3.0, 0.0, 5.0, 1.0, 2.5, 3.5],
            },
            "hourly": {
                "relative_humidity_2m": [70.0, 72.0, 68.0, 75.0, 71.0, 73.0],
            },
        }
        result = parse_weather_data(data)
        assert result["temperature_avg"] == round(
            sum([24.0, 25.0, 23.0, 26.0, 24.5, 25.5, 24.0]) / 7, 1
        )
        assert result["temperature_max"] == 32.0
        assert result["precipitation_sum"] == round(
            sum([2.0, 3.0, 0.0, 5.0, 1.0, 2.5, 3.5]), 1
        )
        assert result["precipitation_daily_avg"] == round(
            sum([2.0, 3.0, 0.0, 5.0, 1.0, 2.5, 3.5]) / 7, 1
        )
        assert result["relative_humidity"] == round(
            sum([70.0, 72.0, 68.0, 75.0, 71.0, 73.0]) / 6, 1
        )

    def test_empty_null_values_return_defaults(self):
        """Empty or null values should return defaults (0.0)."""
        data = {
            "daily": {
                "temperature_2m_mean": None,
                "temperature_2m_max": [],
                "precipitation_sum": [None, None],
            },
            "hourly": {
                "relative_humidity_2m": None,
            },
        }
        result = parse_weather_data(data)
        assert result["temperature_avg"] == 0.0
        assert result["temperature_max"] == 0.0
        assert result["precipitation_sum"] == 0.0
        assert result["precipitation_daily_avg"] == 0.0
        assert result["relative_humidity"] == 0.0

    def test_missing_keys_return_defaults(self):
        """Completely missing keys should return defaults."""
        data = {}
        result = parse_weather_data(data)
        assert result["temperature_avg"] == 0.0
        assert result["temperature_max"] == 0.0
        assert result["precipitation_sum"] == 0.0
        assert result["precipitation_daily_avg"] == 0.0
        assert result["relative_humidity"] == 0.0
