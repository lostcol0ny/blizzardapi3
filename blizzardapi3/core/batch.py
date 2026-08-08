"""Bounded-concurrency fan-out for bulk async calls.

A serial loop over N async calls pays N round-trips back to back. Overlapping
them with :func:`asyncio.gather` collapses that to roughly one round-trip's
worth of wall-clock — but unbounded fan-out can blow past Blizzard's rate
limit. The semaphore here caps how many requests are in flight at once, so you
get the speedup without tripping a 429.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Coroutine
from typing import TypeVar

T = TypeVar("T")


async def gather_limited(*awaitables: Awaitable[T], max_concurrency: int = 10) -> list[T]:
    """Await all ``awaitables`` concurrently, at most ``max_concurrency`` at a time.

    Results are returned in the same order as the inputs (like
    :func:`asyncio.gather`). If any awaitable raises, the rest are cancelled and
    the exception propagates.

    That cancellation is the difference from a bare :func:`asyncio.gather`, which
    reports the first failure but leaves its siblings running. Over a 500-realm
    pull, one bad ID would otherwise mean 499 requests still burning rate limit
    for a result nobody is waiting for — fired, quite possibly, at a client the
    caller has already left the ``async with`` block to close.
    """
    semaphore = asyncio.Semaphore(max_concurrency)

    async def _run(awaitable: Awaitable[T]) -> T:
        try:
            await semaphore.acquire()
        except asyncio.CancelledError:
            # Cancelled while still queued, so nothing ever awaited this
            # coroutine — and an un-awaited coroutine complains at collection
            # time, on whatever line happens to trigger the GC. Close it so a
            # cancelled batch stays quiet.
            if isinstance(awaitable, Coroutine):
                awaitable.close()
            raise
        try:
            return await awaitable
        finally:
            semaphore.release()

    tasks = [asyncio.ensure_future(_run(a)) for a in awaitables]
    try:
        return await asyncio.gather(*tasks)
    except BaseException:
        for task in tasks:
            task.cancel()
        # Drain before propagating: an un-awaited cancelled task surfaces later
        # as a stray "Task exception was never retrieved" on an unrelated line.
        await asyncio.gather(*tasks, return_exceptions=True)
        raise
