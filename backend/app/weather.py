"""Weather data fetching from Open-Meteo API."""

import asyncio
import logging
from datetime import datetime, timedelta

import httpx

from app.commodity_config import COMMODITIES
from app.utils import fetch_with_fallback

logger = logging.getLogger(__name__)

# Derive legacy structures from the central config
COMMODITY_REGIONS = {name: c["regions"] for name, c in COMMODITIES.items()}
BASELINE_TEMP = {name: c["baselines"]["temp"] for name, c in COMMODITIES.items()}
BASELINE_PRECIP = {name: c["baselines"]["precip"] for name, c in COMMODITIES.items()}


async def fetch_region_weather(
    latitude: float, longitude: float
) -> dict:
    """Fetch 7-day weather data for a specific coordinate from Open-Meteo."""
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
        return response.json()


def parse_weather_data(data: dict) -> dict:
    """Parse Open-Meteo response into averaged weather metrics."""
    daily = data.get("daily", {})
    hourly = data.get("hourly", {})

    temps_mean = [t for t in (daily.get("temperature_2m_mean") or []) if t is not None]
    temps_max = [t for t in (daily.get("temperature_2m_max") or []) if t is not None]
    precip = [p for p in (daily.get("precipitation_sum") or []) if p is not None]

    # Humidity comes from hourly data — aggregate to overall mean
    humidity_hourly = [
        h for h in (hourly.get("relative_humidity_2m") or []) if h is not None
    ]

    return {
        "temperature_avg": round(sum(temps_mean) / len(temps_mean), 1) if temps_mean else 0.0,
        "temperature_max": round(max(temps_max), 1) if temps_max else 0.0,
        "precipitation_sum": round(sum(precip), 1) if precip else 0.0,
        "precipitation_daily_avg": round(sum(precip) / len(precip), 1) if precip else 0.0,
        "relative_humidity": round(sum(humidity_hourly) / len(humidity_hourly), 1) if humidity_hourly else 0.0,
    }


_WEATHER_FALLBACK = {
    "temperature_avg": 25.0,
    "temperature_max": 32.0,
    "precipitation_sum": 20.0,
    "precipitation_daily_avg": 2.9,
    "relative_humidity": 70.0,
}


async def _fetch_and_parse(latitude: float, longitude: float) -> dict:
    """Fetch weather and parse it — may raise on network errors."""
    raw_data = await fetch_region_weather(latitude, longitude)
    return parse_weather_data(raw_data)


async def _fetch_single_region(region: dict) -> dict:
    """Fetch and parse weather for a single region with fallback."""
    parsed = await fetch_with_fallback(
        _fetch_and_parse, _WEATHER_FALLBACK, region["latitude"], region["longitude"]
    )
    return {
        "region_name": region["region_name"],
        "country": region["country"],
        "latitude": region["latitude"],
        "longitude": region["longitude"],
        **parsed,
    }


async def get_all_weather() -> dict[str, list[dict]]:
    """Fetch weather for all commodity regions in parallel."""
    # Build flat list of all regions with their commodity keys
    all_tasks: list[tuple[str, dict]] = []
    for commodity, regions in COMMODITY_REGIONS.items():
        for region in regions:
            all_tasks.append((commodity, region))

    # Fetch all regions concurrently
    fetched = await asyncio.gather(
        *[_fetch_single_region(region) for _, region in all_tasks]
    )

    # Group results by commodity
    results: dict[str, list[dict]] = {}
    for (commodity, _), weather in zip(all_tasks, fetched):
        if commodity not in results:
            results[commodity] = []
        results[commodity].append(weather)

    return results
