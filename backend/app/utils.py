"""Shared utilities for the Harvest Signal backend."""

import logging
from collections.abc import Callable
from typing import TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


async def fetch_with_fallback(
    fetch_fn: Callable[..., T],
    fallback_value: T,
    *args: object,
    **kwargs: object,
) -> T:
    """Call *fetch_fn* and return its result, falling back to *fallback_value* on error."""
    try:
        return await fetch_fn(*args, **kwargs)  # type: ignore[misc]
    except Exception:
        logger.exception("Fetch failed, using fallback")
        return fallback_value
