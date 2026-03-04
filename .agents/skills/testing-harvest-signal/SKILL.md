# Testing Harvest Signal Dashboard

## Overview
Harvest Signal is a soft commodity weather signal dashboard with a FastAPI backend and Next.js frontend. It displays weather-driven trading signals for 6 commodities: Coffee, Sugar, Cocoa, Orange Juice, Lumber, and Palm Oil.

## Architecture
- **Backend**: FastAPI (Python) at `backend/app/main.py` — deployed to Fly.io
- **Frontend**: Next.js + Tailwind CSS at `frontend/` — deployed as static export to Devin static hosting
- **APIs**: Open-Meteo (weather, free), Yahoo Finance (prices, no key), NewsAPI (news, requires key), Alpha Vantage (Coffee fallback, requires key)

## Devin Secrets Needed
- `NEWSAPI_KEY` — NewsAPI.org API key for commodity news headlines
- `ALPHA_VANTAGE_API_KEY` — Alpha Vantage API key (only used as Coffee price fallback)

## Local Testing Setup
1. Start backend: `cd backend && poetry run fastapi dev app/main.py` (runs on port 8000)
2. Start frontend: `cd frontend && npm run dev` (runs on port 3000)
3. Frontend expects `NEXT_PUBLIC_API_URL` in `frontend/.env.local` — set to `http://localhost:8000` for local or the deployed backend URL
4. Backend loads env vars from `backend/.env` via python-dotenv

## Deployed URLs
- Frontend: Deployed via `deploy frontend` tool with `frontend/out` directory
- Backend: Deployed via `deploy backend` tool with `backend/` directory
- Backend env vars (NEWSAPI_KEY, ALPHA_VANTAGE_API_KEY) are set in `backend/.env` and included in deployment

## Testing Checklist

### Dashboard Load
- Navigate to frontend URL
- Verify 6 commodity cards load in 2x3 responsive grid (3 cols on large screens, 2 on medium)
- Header should show signal summary (e.g. "5 Bull 1 Neut") and LIVE status
- Loading skeleton should show 6 placeholder cards while data fetches

### Per-Commodity Card Verification
Each card should display:
- Commodity name with emoji icon (Coffee ☕, Sugar 🍬, Cocoa 🍫, OJ 🍊, Lumber 🌲, Palm Oil 🌴)
- Signal badge (Bullish green / Bearish red / Neutral amber)
- Key driver text (e.g. "Drought conditions in...")
- Price with unit (Coffee/Sugar/OJ: ¢/lb, Cocoa/Palm Oil: $/ton, Lumber: $/MBF)
- Confidence meter (High/Medium/Low)
- Forecast direction label (e.g. "Potential Reversal Upward", "Momentum Confirmed Upward")
- 30-day price sparkline chart with trend label (Uptrend/Downtrend/Sideways)
- Rationale text

### Expandable Sections
Each card has 3 expandable sections (click toggle text to expand/collapse):
1. **Show region details** — Shows growing regions with temp, rain, humidity, and status
2. **Show top producers** — Shows 5 countries with global share %, weather stats, and risk badge (Normal/Watch/Alert)
3. **Show latest news** — Shows up to 3 headlines with source and date (requires NEWSAPI_KEY)

### Price Sources
- Coffee, Sugar, Cocoa, OJ, Lumber: Live from Yahoo Finance (no "est." label)
- Palm Oil: Estimated price ~$925/ton with "(est.)" label (FCPO ticker not available on Yahoo Finance)
- If Yahoo Finance fails, commodities fall back to estimated prices with "(est.)" label

### News Section
- Requires NEWSAPI_KEY environment variable on backend
- Returns 3 headlines per commodity with 1-hour in-memory cache
- If NEWSAPI_KEY is not set, the "Show latest news" button won't appear (graceful degradation)
- After backend restart, first request fetches fresh data (cache doesn't persist)
- Free tier: 100 requests/day — with 6 commodities and 1-hour caching, ~144 requests/day at max

### Backend API Verification
- `GET /api/signals` returns all commodity data
- Verify with: `curl -s <backend_url>/api/signals | python3 -c "import json,sys; [print(f\"{s['commodity']}: {s['signal']}, price={s['price_trend']['current_price']} ({s['price_trend']['source']}), news={len(s.get('news',[]))}\") for s in json.load(sys.stdin)['signals']]"`

## Known Limitations
- Lumber and Palm Oil may show "Price history unavailable" if Yahoo Finance doesn't return 30-day history for LBS=F or FCPO=F
- Palm Oil's Riau and Sumatra regions have very similar coordinates — weather data may be nearly identical
- All commodities except Coffee depend solely on Yahoo Finance for pricing (single point of failure)
- NewsAPI free tier has daily request limits — heavy testing may exhaust the quota
- Backend response time increases with more commodities (~54 Open-Meteo API calls per refresh, parallelized)

## Common Issues
- **News not appearing**: Check that NEWSAPI_KEY is set in backend/.env and backend was redeployed after setting it
- **Stale frontend**: The frontend is a static export — changes require `npm run build` in frontend/ and redeployment of the `out/` directory
- **Prices showing "est."**: Yahoo Finance may be rate-limiting or the ticker symbol may be invalid. Check backend logs.
- **All signals showing same value**: May indicate Open-Meteo API is down or returning default values. Check backend logs for weather fetch errors.
