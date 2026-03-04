"use client";

import { useState } from "react";
import type { CommoditySignal } from "../types";
import SignalBadge from "./SignalBadge";
import ConfidenceMeter from "./ConfidenceMeter";
import PriceTicker from "./PriceTicker";
import SparklineChart from "./SparklineChart";
import ForecastLabel from "./ForecastLabel";
import RegionDetail from "./RegionDetail";
import ProducerCountries from "./ProducerCountries";
import CommodityNews from "./CommodityNews";

interface CommodityCardProps {
  data: CommoditySignal;
}

const commodityIcons: Record<string, string> = {
  Coffee: "\u2615",
  Sugar: "\uD83C\uDF6C",
  Cocoa: "\uD83C\uDF6B",
  "Orange Juice": "\uD83C\uDF4A",
  Lumber: "\uD83C\uDF32",
  "Palm Oil": "\uD83C\uDF34",
};

const signalBorderColor: Record<string, string> = {
  Bullish: "border-l-signal-bullish",
  Bearish: "border-l-signal-bearish",
  Neutral: "border-l-signal-neutral",
};

export default function CommodityCard({ data }: CommodityCardProps) {
  const [expanded, setExpanded] = useState(false);
  const icon = commodityIcons[data.commodity] ?? "\uD83D\uDCC8";
  const borderColor = signalBorderColor[data.signal] ?? "border-l-navy-600";

  return (
    <div
      className={`relative overflow-hidden rounded-lg border border-border-subtle bg-surface-elevated ${borderColor} border-l-4 transition-all duration-300 hover:border-navy-600`}
    >
      {/* Card Header */}
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{icon}</span>
            <div>
              <h3 className="text-lg font-bold text-text-primary tracking-wide">
                {data.commodity}
              </h3>
              <span className="text-xs text-text-muted">
                {new Date(data.last_updated).toLocaleTimeString("en-US", {
                  hour: "2-digit",
                  minute: "2-digit",
                  timeZoneName: "short",
                })}
              </span>
            </div>
          </div>
          <SignalBadge signal={data.signal} />
        </div>

        {/* Key Driver */}
        <div className="mb-4 rounded-md bg-navy-900/60 px-4 py-3 border border-navy-700/50">
          <span className="text-xs text-text-muted uppercase tracking-widest block mb-1">
            Key Driver
          </span>
          <p className="text-sm font-medium text-accent-cyan">
            {data.key_driver}
          </p>
        </div>

        {/* Price + Confidence Row */}
        <div className="flex items-center justify-between mb-4">
          <PriceTicker trend={data.price_trend} commodity={data.commodity} />
          <ConfidenceMeter confidence={data.confidence} />
        </div>

        {/* Price Forecast Direction */}
        {data.forecast_direction && (
          <ForecastLabel forecast={data.forecast_direction} />
        )}

        {/* 30-Day Price Sparkline */}
        {data.price_history && (
          <SparklineChart history={data.price_history} />
        )}

        {/* Rationale */}
        <div className="mb-2">
          <span className="text-xs text-text-muted uppercase tracking-widest block mb-1">
            Rationale
          </span>
          <p className="text-sm text-text-secondary leading-relaxed">
            {data.rationale}
          </p>
        </div>

        {/* Expand Toggle */}
        <button
          onClick={() => setExpanded(!expanded)}
          className="mt-3 flex items-center gap-1 text-xs text-text-muted hover:text-accent-blue transition-colors cursor-pointer"
        >
          <span
            className={`transition-transform duration-200 ${expanded ? "rotate-90" : ""}`}
          >
            &#9654;
          </span>
          {expanded ? "Hide" : "Show"} region details
        </button>

        {/* Region Details (expandable) */}
        {expanded && <RegionDetail regions={data.regions} />}

        {/* Top Producing Countries (expandable) */}
        {data.producers && data.producers.length > 0 && (
          <ProducerCountries producers={data.producers} />
        )}

        {/* Latest News (expandable) */}
        {data.news && data.news.length > 0 && (
          <CommodityNews articles={data.news} />
        )}
      </div>
    </div>
  );
}
