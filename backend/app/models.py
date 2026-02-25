from enum import Enum
from pydantic import BaseModel


class Signal(str, Enum):
    BULLISH = "Bullish"
    BEARISH = "Bearish"
    NEUTRAL = "Neutral"


class Confidence(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class RegionWeather(BaseModel):
    region_name: str
    country: str
    latitude: float
    longitude: float
    temperature_avg: float
    temperature_max: float
    precipitation_sum: float
    relative_humidity: float
    condition_summary: str


class PriceTrend(BaseModel):
    current_price: float | None = None
    change_percent: float | None = None
    direction: str = "N/A"
    source: str = "estimated"


class CommoditySignal(BaseModel):
    commodity: str
    signal: Signal
    confidence: Confidence
    key_driver: str
    rationale: str
    price_trend: PriceTrend
    regions: list[RegionWeather]
    last_updated: str


class DashboardResponse(BaseModel):
    signals: list[CommoditySignal]
    generated_at: str
