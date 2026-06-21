"""Bounded-concurrency fan-out for bulk async calls.

A serial loop over N async calls pays N round-trips back to back. Overlapping
them with :func:`asyncio.gather` collapses that to roughly one round-trip's
worth of wall-clock — but unbounded fan-out can blow past Blizzard's rate
limit. The semaphore here caps how many requests are in flight at once, so you
get the speedup without tripping a 429.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable
from typing import TypeVar

T = TypeVar("T")


async def gather_limited(*awaitables: Awaitable[T], max_concurrency: int = 10) -> list[T]:
    """Await all ``awaitables`` concurrently, at most ``max_concurrency`` at a time.

    Results are returned in the same order as the inputs (like
    :func:`asyncio.gather`). If any awaitable raises, the exception propagates
    once the gather settles.
    """
    semaphore = asyncio.Semaphore(max_concurrency)

    async def _run(awaitable: Awaitable[T]) -> T:
        async with semaphore:
            return await awaitable

    return await asyncio.gather(*(_run(a) for a in awaitables))
