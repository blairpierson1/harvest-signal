"""API routes for Harvest Signal dashboard."""

import asyncio
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request

from app.dependencies import limiter, verify_api_key
from app.models import (
    CommoditySignal,
    DashboardResponse,
    PriceHistory,
    PriceTrend,
    RegionWeather,
)
from app.cache import async_ttl_cache
from app.commodity_config import COMMODITIES
from app.weather import get_all_weather as _get_all_weather
from app.signals import generate_commodity_signal, generate_condition_summary, analyze_region
from app.prices import fetch_all_prices as _fetch_all_prices
from app.prices import fetch_all_price_histories as _fetch_all_price_histories
from app.producers import fetch_all_producers as _fetch_all_producers

logger = logging.getLogger(__name__)

router = APIRouter()

# Cached wrappers for the four main data-fetching functions (5-min TTL).


@async_ttl_cache()
async def get_all_weather():
    return await _get_all_weather()


@async_ttl_cache()
async def fetch_all_prices():
    return await _fetch_all_prices()


@async_ttl_cache()
async def fetch_all_price_histories():
    return await _fetch_all_price_histories()


@async_ttl_cache()
async def fetch_all_producers():
    return await _fetch_all_producers()


@router.get("/")
async def health_check():
    return {"status": "ok", "service": "Harvest Signal API", "version": "1.0.0"}


@router.get("/api/signals", response_model=DashboardResponse)
@limiter.limit("10/minute")
async def get_signals(request: Request, _auth: None = Depends(verify_api_key)):
    """Get weather-based trading signals for all tracked soft commodities."""
    try:
        # Fetch weather, prices, price history, and producer data concurrently
        weather_data, price_data, history_data, producer_data = await asyncio.gather(
            get_all_weather(),
            fetch_all_prices(),
            fetch_all_price_histories(),
            fetch_all_producers(),
        )

        signals = []
        for commodity, regions in weather_data.items():
            # Generate signal (pass producer data so country-level alerts influence signal)
            commodity_producers = producer_data.get(commodity, [])
            signal, confidence, key_driver, rationale = generate_commodity_signal(
                commodity, regions, producers=commodity_producers
            )

            # Build region weather models with condition summaries
            region_models = []
            for region in regions:
                analysis = analyze_region(commodity, region)
                condition = generate_condition_summary(analysis)
                region_models.append(
                    RegionWeather(
                        region_name=region["region_name"],
                        country=region["country"],
                        latitude=region["latitude"],
                        longitude=region["longitude"],
                        temperature_avg=region["temperature_avg"],
                        temperature_max=region["temperature_max"],
                        precipitation_sum=region["precipitation_sum"],
                        relative_humidity=region["relative_humidity"],
                        condition_summary=condition,
                    )
                )

            cfg = COMMODITIES.get(commodity, {})
            commodity_signal = CommoditySignal(
                commodity=commodity,
                icon=cfg.get("icon", ""),
                unit=cfg.get("unit", ""),
                signal=signal,
                confidence=confidence,
                key_driver=key_driver,
                rationale=rationale,
                price_trend=price_data.get(commodity, PriceTrend()),
                price_history=history_data.get(commodity, PriceHistory()),
                regions=region_models,
                producers=producer_data.get(commodity, []),
                last_updated=datetime.now(timezone.utc).isoformat(),
            )
            signals.append(commodity_signal)

        return DashboardResponse(
            signals=signals,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    except Exception as e:
        logger.exception("Failed to generate signals")
        raise HTTPException(status_code=500, detail="An internal error occurred. Please try again later.")


@router.get("/api/health")
async def api_health():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "commodities": ["Coffee", "Sugar", "Cocoa"],
    }
