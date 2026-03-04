"""API routes for Harvest Signal dashboard."""

import asyncio
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException

from app.models import (
    CommoditySignal,
    DashboardResponse,
    ForecastDirection,
    PriceHistory,
    PriceTrend,
    RegionWeather,
)
from app.weather import get_all_weather
from app.signals import generate_commodity_signal, generate_condition_summary, analyze_region
from app.prices import fetch_all_prices, fetch_all_price_histories
from app.producers import fetch_all_producers
from app.forecast import compute_forecast_direction
from app.news import fetch_all_news

router = APIRouter()


@router.get("/")
async def health_check():
    return {"status": "ok", "service": "Harvest Signal API", "version": "1.0.0"}


@router.get("/api/signals", response_model=DashboardResponse)
async def get_signals():
    """Get weather-based trading signals for all tracked soft commodities."""
    try:
        # Fetch weather, prices, price history, producer data, and news concurrently
        weather_data, price_data, history_data, producer_data, news_data = await asyncio.gather(
            get_all_weather(),
            fetch_all_prices(),
            fetch_all_price_histories(),
            fetch_all_producers(),
            fetch_all_news(),
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

            # Compute forecast direction from signal + price trend
            commodity_history = history_data.get(commodity, PriceHistory())
            forecast = compute_forecast_direction(
                signal, commodity_history.trend_label, confidence
            )

            commodity_signal = CommoditySignal(
                commodity=commodity,
                signal=signal,
                confidence=confidence,
                key_driver=key_driver,
                rationale=rationale,
                price_trend=price_data.get(commodity, PriceTrend()),
                price_history=commodity_history,
                forecast_direction=forecast,
                regions=region_models,
                producers=producer_data.get(commodity, []),
                news=news_data.get(commodity, []),
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
        "commodities": ["Coffee", "Sugar", "Cocoa", "Orange Juice", "Lumber", "Palm Oil"],
    }
