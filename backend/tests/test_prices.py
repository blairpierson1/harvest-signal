"""Tests for price trend computation."""

from app.models import PriceHistoryPoint
from app.prices import _compute_trend_label


class TestComputeTrendLabel:
    """Tests for _compute_trend_label()."""

    def test_uptrend(self):
        """Last 5 avg > first 5 avg by >3% should be Uptrend."""
        # First 5 close ~100, last 5 close ~110 => ~10% change
        points = [
            PriceHistoryPoint(date=f"2025-01-{i+1:02d}", close=100.0)
            for i in range(5)
        ] + [
            PriceHistoryPoint(date=f"2025-01-{i+6:02d}", close=110.0)
            for i in range(5)
        ]
        assert _compute_trend_label(points) == "Uptrend"

    def test_downtrend(self):
        """Last 5 avg < first 5 avg by >3% should be Downtrend."""
        # First 5 close ~100, last 5 close ~90 => ~-10% change
        points = [
            PriceHistoryPoint(date=f"2025-01-{i+1:02d}", close=100.0)
            for i in range(5)
        ] + [
            PriceHistoryPoint(date=f"2025-01-{i+6:02d}", close=90.0)
            for i in range(5)
        ]
        assert _compute_trend_label(points) == "Downtrend"

    def test_sideways(self):
        """Change < 3% should be Sideways."""
        # First 5 close ~100, last 5 close ~101 => ~1% change
        points = [
            PriceHistoryPoint(date=f"2025-01-{i+1:02d}", close=100.0)
            for i in range(5)
        ] + [
            PriceHistoryPoint(date=f"2025-01-{i+6:02d}", close=101.0)
            for i in range(5)
        ]
        assert _compute_trend_label(points) == "Sideways"

    def test_na_when_fewer_than_5_points(self):
        """Fewer than 5 points should return N/A."""
        points = [
            PriceHistoryPoint(date=f"2025-01-{i+1:02d}", close=100.0)
            for i in range(3)
        ]
        assert _compute_trend_label(points) == "N/A"
