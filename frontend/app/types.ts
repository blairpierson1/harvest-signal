export type Signal = "Bullish" | "Bearish" | "Neutral";
export type Confidence = "High" | "Medium" | "Low";
export type WeatherRisk = "Normal" | "Watch" | "Alert";

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

export interface PriceHistoryPoint {
  date: string;
  close: number;
}

export interface PriceHistory {
  points: PriceHistoryPoint[];
  trend_label: string;
  source: string;
}

export interface ProducerCountry {
  country: string;
  share_percent: number;
  weather_risk: WeatherRisk;
  risk_detail: string;
  temperature_avg: number;
  precipitation_sum: number;
  relative_humidity: number;
}

export interface CommoditySignal {
  commodity: string;
  icon: string;
  unit: string;
  signal: Signal;
  confidence: Confidence;
  key_driver: string;
  rationale: string;
  price_trend: PriceTrend;
  price_history: PriceHistory;
  regions: RegionWeather[];
  producers: ProducerCountry[];
  last_updated: string;
}

export interface DashboardResponse {
  signals: CommoditySignal[];
  generated_at: string;
}
