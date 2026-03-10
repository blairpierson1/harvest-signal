"""Price trend data for soft commodities.

All three commodities use Yahoo Finance as the primary price source.
Alpha Vantage is kept as a last-resort fallback for Coffee only
(when Yahoo Finance fails).
30-day price history also uses Yahoo Finance for all three.
"""

import asyncio
import logging
import os
from datetime import UTC, datetime

import httpx

from app.models import PriceHistory, PriceHistoryPoint, PriceTrend

logger = logging.getLogger(__name__)

ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"
YAHOO_FINANCE_BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart"

# Routing table: Yahoo Finance is primary for all commodities.
# Alpha Vantage is a last-resort fallback for Coffee only.
COMMODITY_CONFIG: dict[str, dict[str, str]] = {
    "Coffee": {"source": "yahoo", "symbol": "KC=F", "av_fallback_function": "COFFEE"},
    "Sugar": {"source": "yahoo", "symbol": "SB=F"},
    "Cocoa": {"source": "yahoo", "symbol": "CC=F"},
}

# Yahoo Finance symbols for 30-day price history (all commodities).
YAHOO_SYMBOLS: dict[str, str] = {
    "Coffee": "KC=F",
    "Sugar": "SB=F",
    "Cocoa": "CC=F",
}


def _get_api_key() -> str | None:
    """Read the Alpha Vantage API key from environment."""
    return os.environ.get("ALPHA_VANTAGE_API_KEY")


async def _fetch_alpha_vantage_price(
    commodity: str, config: dict[str, str]
) -> PriceTrend:
    """Fetch price from Alpha Vantage commodity endpoint (Coffee)."""
    api_key = _get_api_key()
    if not api_key:
        return _get_estimated_price(commodity)

    try:
        params = {
            "function": config["function"],
            "interval": "daily",
            "apikey": api_key,
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(ALPHA_VANTAGE_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

        # Check for API error / rate-limit messages
        if "Information" in data or "Error Message" in data or "Note" in data:
            logger.warning(
                "Alpha Vantage error for %s: %s",
                commodity,
                data.get("Information") or data.get("Error Message") or data.get("Note"),
            )
            return _get_estimated_price(commodity)

        data_points = data.get("data", [])
        # Filter out entries with "." as value (missing data)
        valid_points = [
            p for p in data_points if p.get("value") and p["value"] != "."
        ]

        if len(valid_points) < 2:
            return _get_estimated_price(commodity)

        current_value = float(valid_points[0]["value"])
        previous_value = float(valid_points[1]["value"])

        if previous_value > 0:
            change_pct = (
                (current_value - previous_value) / previous_value
            ) * 100
            direction = (
                "up" if change_pct > 0 else "down" if change_pct < 0 else "flat"
            )
        else:
            change_pct = 0.0
            direction = "flat"

        return PriceTrend(
            current_price=round(current_value, 2),
            change_percent=round(change_pct, 2),
            direction=direction,
            source="alpha_vantage",
        )

    except Exception:
        logger.warning("Alpha Vantage request failed for %s", commodity, exc_info=True)
        return _get_estimated_price(commodity)


async def _fetch_yahoo_price(
    commodity: str, config: dict[str, str]
) -> PriceTrend:
    """Fetch price from Yahoo Finance chart endpoint (Sugar, Cocoa)."""
    try:
        symbol = config["symbol"]
        url = f"{YAHOO_FINANCE_BASE_URL}/{symbol}"
        params = {"range": "5d", "interval": "1d"}
        headers = {"User-Agent": "Mozilla/5.0"}

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

        result = data.get("chart", {}).get("result", [])
        if not result:
            return _get_estimated_price(commodity)

        meta = result[0].get("meta", {})
        current_price = meta.get("regularMarketPrice")
        if current_price is None:
            return _get_estimated_price(commodity)

        # Yahoo Finance uses chartPreviousClose or previousClose
        prev_close = meta.get("previousClose") or meta.get("chartPreviousClose")

        if prev_close and prev_close > 0:
            change_pct = ((current_price - prev_close) / prev_close) * 100
            direction = (
                "up" if change_pct > 0 else "down" if change_pct < 0 else "flat"
            )
        else:
            change_pct = 0.0
            direction = "flat"

        return PriceTrend(
            current_price=round(current_price, 2),
            change_percent=round(change_pct, 2),
            direction=direction,
            source="yahoo_finance",
        )

    except Exception:
        logger.warning("Yahoo Finance request failed for %s", commodity, exc_info=True)
        return _get_estimated_price(commodity)


async def fetch_price_trend(commodity: str) -> PriceTrend:
    """Fetch current price trend for a commodity.

    All commodities use Yahoo Finance as primary.
    Coffee falls back to Alpha Vantage if Yahoo Finance fails.
    """
    config = COMMODITY_CONFIG.get(commodity)
    if not config:
        return PriceTrend()

    result = await _fetch_yahoo_price(commodity, config)

    # If Yahoo Finance failed and there's an Alpha Vantage fallback, try it.
    if result.source == "estimated" and "av_fallback_function" in config:
        av_config = {"function": config["av_fallback_function"]}
        av_result = await _fetch_alpha_vantage_price(commodity, av_config)
        if av_result.source != "estimated":
            return av_result

    if result.source == "estimated":
        logger.warning("All price sources failed for %s, using estimated price", commodity)

    return result


def _get_estimated_price(commodity: str) -> PriceTrend:
    """Return estimated commodity prices as fallback when APIs fail."""
    estimates = {
        "Coffee": PriceTrend(
            current_price=365.00,
            change_percent=0.0,
            direction="flat",
            source="estimated",
        ),
        "Sugar": PriceTrend(
            current_price=14.00,
            change_percent=0.0,
            direction="flat",
            source="estimated",
        ),
        "Cocoa": PriceTrend(
            current_price=3050.00,
            change_percent=0.0,
            direction="flat",
            source="estimated",
        ),
    }
    return estimates.get(commodity, PriceTrend())


async def fetch_all_prices() -> dict[str, PriceTrend]:
    """Fetch price trends for all tracked commodities in parallel."""
    commodities = list(COMMODITY_CONFIG.keys())
    results = await asyncio.gather(
        *[fetch_price_trend(c) for c in commodities]
    )
    return dict(zip(commodities, results))


def _compute_trend_label(points: list[PriceHistoryPoint]) -> str:
    """Determine Uptrend / Downtrend / Sideways from 30-day price history."""
    if len(points) < 5:
        return "N/A"

    first_5_avg = sum(p.close for p in points[:5]) / 5
    last_5_avg = sum(p.close for p in points[-5:]) / 5

    if first_5_avg == 0:
        return "Sideways"

    pct_change = ((last_5_avg - first_5_avg) / first_5_avg) * 100

    if pct_change > 3.0:
        return "Uptrend"
    elif pct_change < -3.0:
        return "Downtrend"
    return "Sideways"


async def fetch_price_history(commodity: str) -> PriceHistory:
    """Fetch 30-day price history from Yahoo Finance for sparkline chart."""
    symbol = YAHOO_SYMBOLS.get(commodity)
    if not symbol:
        return PriceHistory()

    try:
        url = f"{YAHOO_FINANCE_BASE_URL}/{symbol}"
        params = {"range": "1mo", "interval": "1d"}
        headers = {"User-Agent": "Mozilla/5.0"}

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

        result = data.get("chart", {}).get("result", [])
        if not result:
            return PriceHistory()

        timestamps = result[0].get("timestamp", [])
        closes_raw = (
            result[0].get("indicators", {}).get("quote", [{}])[0].get("close", [])
        )

        points: list[PriceHistoryPoint] = []
        for ts, close in zip(timestamps, closes_raw):
            if close is not None:
                date_str = datetime.fromtimestamp(ts, tz=UTC).strftime("%Y-%m-%d")
                points.append(PriceHistoryPoint(date=date_str, close=round(close, 2)))

        trend_label = _compute_trend_label(points)

        return PriceHistory(
            points=points,
            trend_label=trend_label,
            source="yahoo_finance",
        )

    except Exception:
        logger.exception("Failed to fetch price history, using fallback")
        return PriceHistory()


async def fetch_all_price_histories() -> dict[str, PriceHistory]:
    """Fetch 30-day price history for all commodities in parallel."""
    commodities = list(YAHOO_SYMBOLS.keys())
    results = await asyncio.gather(
        *[fetch_price_history(c) for c in commodities]
    )
    return dict(zip(commodities, results))
