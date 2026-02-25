"""API routes for Harvest Signal dashboard."""

import asyncio
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException

from app.models import (
    CommoditySignal,
    DashboardResponse,
    PriceTrend,
    RegionWeather,
)
from app.weather import get_all_weather
from app.signals import generate_commodity_signal, generate_condition_summary, analyze_region
from app.prices import fetch_all_prices

router = APIRouter()


@router.get("/")
async def health_check():
    return {"status": "ok", "service": "Harvest Signal API", "version": "1.0.0"}


@router.get("/api/signals", response_model=DashboardResponse)
async def get_signals():
    """Get weather-based trading signals for all tracked soft commodities."""
    try:
        # Fetch weather and price data concurrently
        weather_data, price_data = await asyncio.gather(
            get_all_weather(), fetch_all_prices()
        )

        signals = []
        for commodity, regions in weather_data.items():
            # Generate signal
            signal, confidence, key_driver, rationale = generate_commodity_signal(
                commodity, regions
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

            commodity_signal = CommoditySignal(
                commodity=commodity,
                signal=signal,
                confidence=confidence,
                key_driver=key_driver,
                rationale=rationale,
                price_trend=price_data.get(commodity, PriceTrend()),
                regions=region_models,
                last_updated=datetime.now(timezone.utc).isoformat(),
            )
            signals.append(commodity_signal)

        return DashboardResponse(
            signals=signals,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate signals: {str(e)}")


@router.get("/api/health")
async def api_health():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "commodities": ["Coffee", "Sugar", "Cocoa"],
    }
