export type Signal = "Bullish" | "Bearish" | "Neutral";
export type Confidence = "High" | "Medium" | "Low";

export interface RegionWeather {
  region_name: string;
  country: string;
  latitude: number;
  longitude: number;
  temperature_avg: number;
  temperature_max: number;
  precipitation_sum: number;
  relative_humidity: number;
  condition_summary: string;
}

export interface PriceTrend {
  current_price: number | null;
  change_percent: number | null;
  direction: string;
  source: string;
}

export interface CommoditySignal {
  commodity: string;
  signal: Signal;
  confidence: Confidence;
  key_driver: string;
  rationale: string;
  price_trend: PriceTrend;
  regions: RegionWeather[];
  last_updated: string;
}

export interface DashboardResponse {
  signals: CommoditySignal[];
  generated_at: string;
}
