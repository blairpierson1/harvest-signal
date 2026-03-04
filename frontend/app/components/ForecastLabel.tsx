"use client";

import type { ForecastDirection } from "../types";

interface ForecastLabelProps {
  forecast: ForecastDirection;
}

const labelColors: Record<string, string> = {
  "Potential Reversal Upward": "text-signal-bullish",
  "Momentum Confirmed Upward": "text-signal-bullish",
  "Potential Reversal Downward": "text-signal-bearish",
  "Momentum Confirmed Downward": "text-signal-bearish",
  "No Clear Directional Bias": "text-signal-neutral",
};

const labelIcons: Record<string, string> = {
  "Potential Reversal Upward": "\u21BB",
  "Momentum Confirmed Upward": "\u2191\u2191",
  "Potential Reversal Downward": "\u21BB",
  "Momentum Confirmed Downward": "\u2193\u2193",
  "No Clear Directional Bias": "\u2194",
};

const confidenceDots: Record<string, number> = {
  High: 3,
  Medium: 2,
  Low: 1,
};

export default function ForecastLabel({ forecast }: ForecastLabelProps) {
  const color = labelColors[forecast.label] ?? "text-text-muted";
  const icon = labelIcons[forecast.label] ?? "";
  const dots = confidenceDots[forecast.confidence] ?? 1;

  return (
    <div className="flex items-center gap-2 mt-1">
      <span className={`text-xs font-medium ${color}`}>
        {icon} {forecast.label}
      </span>
      <div className="flex items-center gap-0.5">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className={`w-1 h-1 rounded-full ${
              i <= dots ? "bg-text-secondary" : "bg-navy-700"
            }`}
          />
        ))}
      </div>
    </div>
  );
}
