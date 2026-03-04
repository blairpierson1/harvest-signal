# Harvest Signal

Soft commodity weather signal dashboard that shows daily price direction signals (Bullish / Bearish / Neutral) for six commodities based on real-time weather data from growing regions worldwide.

## What It Does

Harvest Signal monitors weather conditions across major commodity-producing regions and generates trading signals based on supply risk analysis:

- **Drought / heat stress** -> Bullish (supply risk drives prices up)
- **Excess rainfall / flooding** -> Bearish (harvest disruption)
- **Normal conditions** -> Neutral

### Commodities Tracked

| Commodity | Ticker | Growing Regions | Top Producers |
|-----------|--------|-----------------|---------------|
| Coffee | KC=F | Brazil, Vietnam | Brazil, Vietnam, Colombia, Indonesia, Ethiopia |
| Sugar | SB=F | Brazil, India | Brazil, India, Thailand, China, Pakistan |
| Cocoa | CC=F | Ghana, Ivory Coast | Ivory Coast, Ghana, Indonesia, Nigeria, Ecuador |
| Orange Juice | OJ=F | Florida, Brazil | Brazil, USA, Mexico, Spain, Italy |
| Lumber | LBS=F | Pacific NW, Canada | USA, Canada, Russia, Sweden, Finland |
| Palm Oil | FCPO | Sumatra, Borneo | Indonesia, Malaysia, Thailand, Colombia, Nigeria |

### Features

- Signal badges with confidence levels (High / Medium / Low)
- 30-day price sparkline charts with trend labels
- Price forecast direction combining weather signals with price trends
- Top 5 producing countries per commodity with weather risk badges
- Latest news headlines per commodity via NewsAPI
- Auto-refresh every 5 minutes

## Tech Stack

### Backend
- **Python 3.11+** with **FastAPI**
- **Open-Meteo API** for weather data (free, no key needed)
- **Yahoo Finance** for commodity prices (primary source)
- **Alpha Vantage** as fallback for Coffee pricing
- **NewsAPI** for commodity news headlines
- **httpx** for async HTTP requests
- **Pydantic** for data models
- All API calls parallelized via `asyncio.gather()`

### Frontend
- **Next.js 16** (static export)
- **React 19**
- **Tailwind CSS v4**
- **Recharts** for sparkline charts
- **TypeScript**
- Dark Bloomberg-terminal aesthetic

## Running Locally

### Prerequisites

- Python 3.11+
- Node.js 18+
- [Poetry](https://python-poetry.org/) for Python dependency management

### Backend

```bash
cd backend

# Install dependencies
poetry install

# (Optional) Create .env file for API keys
cat > .env << EOF
NEWSAPI_KEY=your_newsapi_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
EOF

# Start the development server
poetry run fastapi dev app/main.py
```

The backend will be available at `http://localhost:8000`. Weather data and Yahoo Finance prices work without any API keys. NewsAPI requires a key for the news section (free tier at [newsapi.org](https://newsapi.org/)).

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local pointing to your local backend
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:3000`.

### Building for Production

```bash
cd frontend
npm run build
```

This produces a static export in `frontend/out/` that can be deployed to any static hosting provider.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEWSAPI_KEY` | Optional | [NewsAPI.org](https://newsapi.org/) key for commodity news headlines. Free tier: 100 requests/day. Without this, the news section will be empty. |
| `ALPHA_VANTAGE_API_KEY` | Optional | [Alpha Vantage](https://www.alphavantage.co/) key, used as last-resort fallback for Coffee pricing only. Free tier: 25 requests/day. |
| `NEXT_PUBLIC_API_URL` | Required (frontend) | Backend API URL. Defaults to `http://localhost:8000` for local development. |

## Deployed URLs

- **Frontend**: https://soft-commodity-dashboard-ao789btn.devinapps.com
- **Backend API**: https://harvest-signal-backend-eyzjavel.fly.dev
- **API endpoint**: https://harvest-signal-backend-eyzjavel.fly.dev/api/signals

## Project Structure

```
harvest-signal/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app with CORS
│   │   ├── routes.py        # /api/signals endpoint
│   │   ├── models.py        # Pydantic data models
│   │   ├── weather.py       # Open-Meteo API integration
│   │   ├── prices.py        # Yahoo Finance + Alpha Vantage
│   │   ├── signals.py       # Signal generation logic
│   │   ├── forecast.py      # Price forecast direction
│   │   ├── producers.py     # Top producing countries + weather
│   │   └── news.py          # NewsAPI integration
│   └── pyproject.toml
├── frontend/
│   ├── app/
│   │   ├── components/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── CommodityCard.tsx
│   │   │   ├── CommodityNews.tsx
│   │   │   ├── SparklineChart.tsx
│   │   │   ├── ForecastLabel.tsx
│   │   │   ├── ProducerCountries.tsx
│   │   │   └── ...
│   │   ├── types.ts
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── next.config.ts
│   └── package.json
└── README.md
```
