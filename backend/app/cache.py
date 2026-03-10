"""Simple async TTL cache for expensive data-fetching functions."""

import asyncio
import functools
import time
from typing import TypeVar

T = TypeVar("T")

_DEFAULT_TTL = 300  # 5 minutes


def async_ttl_cache(ttl: int = _DEFAULT_TTL):
    """Decorator that caches the result of an async function for *ttl* seconds.

    The cache can be bypassed by passing the keyword argument ``force_refresh=True``.
    The cached value can be cleared by calling ``cache_clear()`` on the wrapper.
    """

    def decorator(fn):  # noqa: ANN001, ANN202
        cache: dict[str, tuple[float, object]] = {}
        lock = asyncio.Lock()

        @functools.wraps(fn)
        async def wrapper(*args, force_refresh: bool = False, **kwargs):  # noqa: ANN002, ANN003, ANN202
            key = f"{args}:{kwargs}"
            now = time.monotonic()

            if not force_refresh:
                entry = cache.get(key)
                if entry is not None:
                    ts, value = entry
                    if now - ts < ttl:
                        return value

            async with lock:
                # Double-check after acquiring lock
                if not force_refresh:
                    entry = cache.get(key)
                    if entry is not None:
                        ts, value = entry
                        if now - ts < ttl:
                            return value

                result = await fn(*args, **kwargs)
                cache[key] = (time.monotonic(), result)
                return result

        def cache_clear() -> None:
            cache.clear()

        wrapper.cache_clear = cache_clear  # type: ignore[attr-defined]
        return wrapper

    return decorator
