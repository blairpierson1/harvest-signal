"""Commodity news fetching from NewsAPI.org with 1-hour caching."""

from __future__ import annotations

import asyncio
import os
import time

import httpx

from app.models import NewsArticle

NEWSAPI_BASE_URL = "https://newsapi.org/v2/everything"

# Query terms per commodity
NEWS_QUERIES: dict[str, str] = {
    "Coffee": "coffee commodity",
    "Sugar": "sugar commodity",
    "Cocoa": "cocoa commodity",
    "Orange Juice": "orange juice commodity",
    "Lumber": "lumber timber commodity",
    "Palm Oil": "palm oil commodity",
}

# In-memory cache: {commodity: (timestamp, [NewsArticle, ...])}
_cache: dict[str, tuple[float, list[NewsArticle]]] = {}
CACHE_TTL_SECONDS = 3600  # 1 hour


def _get_api_key() -> str | None:
    """Read the NewsAPI key from environment."""
    return os.environ.get("NEWSAPI_KEY")


async def _fetch_news_for_commodity(commodity: str) -> list[NewsArticle]:
    """Fetch top 3 recent headlines for a commodity from NewsAPI."""
    # Check cache first
    cached = _cache.get(commodity)
    if cached:
        cache_time, articles = cached
        if time.time() - cache_time < CACHE_TTL_SECONDS:
            return articles

    api_key = _get_api_key()
    if not api_key:
        return []

    query = NEWS_QUERIES.get(commodity, f"{commodity} commodity")

    try:
        params = {
            "q": query,
            "sortBy": "publishedAt",
            "pageSize": 3,
            "language": "en",
            "apiKey": api_key,
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(NEWSAPI_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

        if data.get("status") != "ok":
            return []

        articles: list[NewsArticle] = []
        for item in data.get("articles", [])[:3]:
            articles.append(
                NewsArticle(
                    title=item.get("title", "Untitled"),
                    source=item.get("source", {}).get("name", "Unknown"),
                    url=item.get("url", ""),
                    published_at=item.get("publishedAt"),
                )
            )

        # Update cache
        _cache[commodity] = (time.time(), articles)
        return articles

    except Exception:
        # Return cached data if available (even if stale), otherwise empty
        if cached:
            return cached[1]
        return []


async def fetch_all_news() -> dict[str, list[NewsArticle]]:
    """Fetch news for all commodities in parallel."""
    commodities = list(NEWS_QUERIES.keys())
    results = await asyncio.gather(
        *[_fetch_news_for_commodity(c) for c in commodities]
    )
    return dict(zip(commodities, results))
