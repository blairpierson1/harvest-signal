# Testing Harvest Signal Backend

## Overview
The Harvest Signal backend is a FastAPI app in `backend/`. It fetches weather/price data from external APIs and returns commodity trading signals.

## Local Setup
```bash
cd backend
poetry install
poetry run fastapi dev app/main.py
```
The backend runs at `http://localhost:8000`.

## Key Endpoints
- `GET /` — Health check (unauthenticated)
- `GET /api/health` — Health check (unauthenticated)
- `GET /api/signals` — Main signals endpoint (authenticated if `API_KEY` is set, rate-limited)

## Testing Auth
- **Without API_KEY**: All endpoints work without any key. A startup warning is logged.
- **With API_KEY**: Set `API_KEY=<value>` env var before starting the server.
  - Requests without a key → 401
  - `X-API-Key: <value>` header → 200
  - `Authorization: Bearer <value>` header → 200
  - Wrong key → 401
  - Health endpoints remain unauthenticated

## Testing CORS
```bash
# Allowed origin (should include Access-Control-Allow-Origin header)
curl -H "Origin: http://localhost:3000" -H "Access-Control-Request-Method: GET" -X OPTIONS http://localhost:8000/api/signals

# Disallowed origin (should return 400 Bad Request)
curl -H "Origin: http://evil.com" -H "Access-Control-Request-Method: GET" -X OPTIONS http://localhost:8000/api/signals
```
The `ALLOWED_ORIGINS` env var controls allowed origins (comma-separated, default: `http://localhost:3000`).

## Testing Rate Limiting
The `/api/signals` endpoint is limited to 10 requests/minute per IP. Sequential requests may not trigger the limit because each request takes ~3-4 seconds (external API calls). Use **parallel** requests to reliably trigger rate limiting:
```bash
for i in $(seq 1 12); do
  curl -s -o /dev/null -w "Request $i: HTTP %{http_code}\n" -H "X-API-Key: <key>" http://localhost:8000/api/signals &
done
wait
```
Expect some requests to return 429 when the limit is exceeded.

## Notes
- The `/api/signals` endpoint is slow (~3-4s) because it fetches live weather and price data from external APIs.
- No CI is configured on this repo.
- `NEWSAPI_KEY` env var is optional (for news headlines). Weather and price data work without any API keys.

## Devin Secrets Needed
- `NEWSAPI_KEY` — Optional, for fetching commodity news headlines
