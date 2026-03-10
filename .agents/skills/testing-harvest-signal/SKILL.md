# Testing Harvest Signal Dashboard

## Overview
Harvest Signal is a soft commodity weather signal dashboard with a Next.js frontend (static export) and FastAPI backend. The frontend is deployed to Devin's static hosting and the backend to Fly.io.

## Deployed URLs
- **Frontend**: Deployed via `deploy frontend dir="frontend/out"` — produces a `*.devinapps.com` URL
- **Backend**: Deployed to Fly.io at `https://harvest-signal-backend-eyzjavel.fly.dev`
- The frontend's backend URL is configured in `frontend/.env.local` as `NEXT_PUBLIC_API_URL`

## Devin Secrets Needed
- `NEWSAPI_KEY` — required for the news section to display headlines. Without it, news sections will be empty (graceful degradation).
- `ALPHA_VANTAGE_API_KEY` — optional, used as last-resort fallback for Coffee pricing only. Yahoo Finance is the primary price source.

## Build & Deploy Process
1. Frontend: `cd frontend && npm run build` produces static files in `frontend/out/`
2. Deploy frontend: `deploy frontend dir="frontend/out"`
3. Backend: Deploy using `deploy backend dir="backend"` or manual Fly.io deployment
4. **Important**: Always rebuild frontend before deploying — the deploy tool does NOT build for you

## Testing the Dashboard

### Quick Smoke Test
1. Navigate to the deployed frontend URL
2. **Hard-refresh** (Ctrl+Shift+R) to bypass browser cache — stale cached versions are a common issue
3. Verify all 6 commodity cards load: Coffee, Sugar, Cocoa, Orange Juice, Lumber, Palm Oil
4. Check the 2x3 grid layout renders correctly

### News Section
- News headlines should appear directly on each card under a "LATEST NEWS" header — no toggle/button required
- Each article shows: headline text, source name (in cyan), and publication date
- Articles are clickable links that open in new tabs
- If news is empty, the section is hidden (not an error)
- **Common issue**: If you see a "Show latest news" toggle instead of direct headlines, the frontend cache is stale — hard-refresh
- News requires `NEWSAPI_KEY` to be set on the backend. Free tier: 100 requests/day, cached for 1 hour

### Price Data
- All commodities use Yahoo Finance as primary price source
- Palm Oil (`FCPO=F`) is not available on Yahoo Finance — always shows estimated price with "(est.)" label. This is expected.
- Lumber uses `LBS=F`, Coffee uses `KC=F`, Sugar uses `SB=F`, Cocoa uses `CC=F`, OJ uses `OJ=F`
- If Yahoo Finance fails, only Coffee has Alpha Vantage as fallback; others fall to estimated prices

### Sparkline Charts
- 30-day price history charts appear under each commodity
- Lumber and Palm Oil may show "Price history unavailable" if Yahoo Finance doesn't return historical data for those tickers
- Trend labels: Uptrend (green), Downtrend (red), Sideways (amber)

### Producer Countries
- Expandable section via "Show top producers" toggle
- Shows 5 countries per commodity with weather risk badges (Normal/Watch/Alert)
- Risk badges are based on live Open-Meteo weather data

### Signals
- All 6 commodities show Bullish/Bearish/Neutral signals
- Signals are weather-driven: drought/heat → Bullish, excess rain → Bearish, normal → Neutral
- Country-level weather alerts can elevate Neutral to Bullish when major producers are affected
- Heat >= 4 independently triggers Bullish

## Common Issues
- **Browser caching**: After redeployment, always hard-refresh. The static frontend aggressively caches.
- **Backend cold start**: Fly.io may take 5-10 seconds on first request after idle. If dashboard shows LOADING for too long, click Refresh.
- **NewsAPI rate limits**: Free tier is 100 req/day. If news stops appearing, the API key may be rate-limited.
- **Yahoo Finance instability**: This is an unofficial API. Prices may occasionally fail or return stale data.
