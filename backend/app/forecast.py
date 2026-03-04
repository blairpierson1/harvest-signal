"""Price forecast direction combining weather signal with price trend."""

from __future__ import annotations

from app.models import Confidence, ForecastDirection, Signal


def compute_forecast_direction(
    signal: Signal,
    trend_label: str,
    signal_confidence: Confidence,
) -> ForecastDirection:
    """Combine weather signal with 30-day price trend into a forecast label.

    Logic:
      Bullish + Downtrend  → 'Potential Reversal Upward'
      Bullish + Uptrend    → 'Momentum Confirmed Upward'
      Bearish + Uptrend    → 'Potential Reversal Downward'
      Bearish + Downtrend  → 'Momentum Confirmed Downward'
      Neutral (any trend)  → 'No Clear Directional Bias'
      Any + N/A trend      → 'No Clear Directional Bias'
    """
    if signal == Signal.NEUTRAL or trend_label in ("N/A", "Sideways"):
        return ForecastDirection(
            label="No Clear Directional Bias",
            confidence=Confidence.LOW,
        )

    if signal == Signal.BULLISH:
        if trend_label == "Downtrend":
            return ForecastDirection(
                label="Potential Reversal Upward",
                confidence=Confidence.MEDIUM if signal_confidence != Confidence.LOW else Confidence.LOW,
            )
        if trend_label == "Uptrend":
            return ForecastDirection(
                label="Momentum Confirmed Upward",
                confidence=signal_confidence,
            )

    if signal == Signal.BEARISH:
        if trend_label == "Uptrend":
            return ForecastDirection(
                label="Potential Reversal Downward",
                confidence=Confidence.MEDIUM if signal_confidence != Confidence.LOW else Confidence.LOW,
            )
        if trend_label == "Downtrend":
            return ForecastDirection(
                label="Momentum Confirmed Downward",
                confidence=signal_confidence,
            )

    # Fallback for any other combination
    return ForecastDirection(
        label="No Clear Directional Bias",
        confidence=Confidence.LOW,
    )
