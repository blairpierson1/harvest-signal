"""Top producing countries with weather risk assessment for each commodity."""

import asyncio
import logging
from datetime import datetime, timedelta

import httpx

from app.commodity_config import COMMODITIES
from app.models import ProducerCountry, WeatherRisk
from app.utils import fetch_with_fallback

logger = logging.getLogger(__name__)

# Derive producer config and risk thresholds from central config
PRODUCER_CONFIG: dict[str, list[dict]] = {name: c["producers"] for name, c in COMMODITIES.items()}
RISK_THRESHOLDS: dict[str, dict] = {name: c["thresholds"]["risk"] for name, c in COMMODITIES.items()}


async def _fetch_producer_weather(latitude: float, longitude: float) -> dict:
    """Fetch 7-day weather for a producer country's primary growing region."""
    today = datetime.utcnow().date()
    start_date = (today - timedelta(days=6)).isoformat()
    end_date = today.isoformat()

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum",
        "hourly": "relative_humidity_2m",
        "start_date": start_date,
        "end_date": end_date,
        "timezone": "auto",
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    daily = data.get("daily", {})
    hourly = data.get("hourly", {})

    temps_mean = [t for t in (daily.get("temperature_2m_mean") or []) if t is not None]
    temps_max = [t for t in (daily.get("temperature_2m_max") or []) if t is not None]
    precip = [p for p in (daily.get("precipitation_sum") or []) if p is not None]
    humidity_hourly = [h for h in (hourly.get("relative_humidity_2m") or []) if h is not None]

    return {
        "temperature_avg": round(sum(temps_mean) / len(temps_mean), 1) if temps_mean else 25.0,
        "temperature_max": round(max(temps_max), 1) if temps_max else 32.0,
        "precipitation_sum": round(sum(precip), 1) if precip else 20.0,
        "precipitation_daily_avg": round(sum(precip) / len(precip), 1) if precip else 2.9,
        "relative_humidity": round(sum(humidity_hourly) / len(humidity_hourly), 1) if humidity_hourly else 70.0,
    }


def _classify_risk(commodity: str, weather: dict) -> tuple[WeatherRisk, str]:
    """Classify weather risk for a producer country as Normal/Watch/Alert."""
    t = RISK_THRESHOLDS[commodity]
    temp_avg = weather["temperature_avg"]
    temp_max = weather["temperature_max"]
    precip_daily = weather["precipitation_daily_avg"]
    humidity = weather["relative_humidity"]

    alerts: list[str] = []
    watches: list[str] = []

    # Temperature checks
    if temp_max > t["temp_alert"]:
        alerts.append(f"Extreme heat ({temp_max:.0f}°C)")
    elif temp_max > t["temp_watch"]:
        watches.append(f"Elevated temps ({temp_max:.0f}°C)")

    # Low precipitation (drought risk)
    if precip_daily < t["precip_low_alert"]:
        alerts.append(f"Very low rainfall ({precip_daily:.1f}mm/day)")
    elif precip_daily < t["precip_low_watch"]:
        watches.append(f"Below-avg rainfall ({precip_daily:.1f}mm/day)")

    # High precipitation (flood risk)
    if precip_daily > t["precip_high_alert"]:
        alerts.append(f"Heavy rainfall ({precip_daily:.1f}mm/day)")
    elif precip_daily > t["precip_high_watch"]:
        watches.append(f"Above-avg rainfall ({precip_daily:.1f}mm/day)")

    # Low humidity
    if humidity < t["humidity_low"]:
        watches.append(f"Low humidity ({humidity:.0f}%)")

    if alerts:
        return WeatherRisk.ALERT, "; ".join(alerts)
    elif watches:
        return WeatherRisk.WATCH, "; ".join(watches)
    return WeatherRisk.NORMAL, "Conditions within normal range"


_PRODUCER_WEATHER_FALLBACK = {
    "temperature_avg": 25.0,
    "temperature_max": 32.0,
    "precipitation_sum": 20.0,
    "precipitation_daily_avg": 2.9,
    "relative_humidity": 70.0,
}


async def _fetch_single_producer(commodity: str, config: dict) -> ProducerCountry:
    """Fetch weather and classify risk for a single producer country."""
    weather = await fetch_with_fallback(
        _fetch_producer_weather,
        _PRODUCER_WEATHER_FALLBACK,
        config["latitude"],
        config["longitude"],
    )

    risk, detail = _classify_risk(commodity, weather)

    return ProducerCountry(
        country=config["country"],
        share_percent=config["share_percent"],
        weather_risk=risk,
        risk_detail=detail,
        temperature_avg=weather["temperature_avg"],
        precipitation_sum=weather["precipitation_sum"],
        relative_humidity=weather["relative_humidity"],
    )


async def fetch_all_producers() -> dict[str, list[ProducerCountry]]:
    """Fetch weather risk for all producer countries across all commodities."""
    all_tasks: list[tuple[str, dict]] = []
    for commodity, producers in PRODUCER_CONFIG.items():
        for producer in producers:
            all_tasks.append((commodity, producer))

    results = await asyncio.gather(
        *[_fetch_single_producer(commodity, config) for commodity, config in all_tasks]
    )

    grouped: dict[str, list[ProducerCountry]] = {}
    for (commodity, _), producer in zip(all_tasks, results):
        if commodity not in grouped:
            grouped[commodity] = []
        grouped[commodity].append(producer)

    return grouped
