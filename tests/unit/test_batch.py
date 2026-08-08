"""Unit tests for gather_limited — ordering, concurrency bound, error propagation."""

from __future__ import annotations

import asyncio
import gc

import pytest

from blizzardapi3 import gather_limited


@pytest.mark.asyncio
async def test_gather_limited_preserves_input_order():
    async def value(n: int) -> int:
        # Reverse the natural completion order: later inputs finish first.
        await asyncio.sleep((5 - n) * 0.01)
        return n

    results = await gather_limited(*(value(n) for n in range(5)), max_concurrency=5)
    assert results == [0, 1, 2, 3, 4]


@pytest.mark.asyncio
async def test_gather_limited_caps_in_flight_requests():
    in_flight = 0
    peak = 0

    async def track() -> None:
        nonlocal in_flight, peak
        in_flight += 1
        peak = max(peak, in_flight)
        await asyncio.sleep(0.02)
        in_flight -= 1

    await gather_limited(*(track() for _ in range(20)), max_concurrency=4)
    assert peak <= 4


@pytest.mark.asyncio
async def test_gather_limited_propagates_exceptions():
    async def ok() -> int:
        return 1

    async def boom() -> int:
        raise ValueError("kaboom")

    with pytest.raises(ValueError, match="kaboom"):
        await gather_limited(ok(), boom(), ok(), max_concurrency=2)


@pytest.mark.asyncio
async def test_a_failure_cancels_its_siblings():
    finished: list[int] = []

    async def slow(n: int) -> int:
        await asyncio.sleep(0.05)
        finished.append(n)
        return n

    async def boom() -> int:
        await asyncio.sleep(0.01)
        raise ValueError("kaboom")

    with pytest.raises(ValueError, match="kaboom"):
        await gather_limited(boom(), *(slow(n) for n in range(5)), max_concurrency=10)

    await asyncio.sleep(0.1)  # long enough for any survivor to finish
    assert finished == [], "siblings must not keep burning rate limit for a result nobody awaits"


@pytest.mark.asyncio
async def test_cancelling_the_batch_cancels_the_work():
    finished: list[int] = []

    async def slow(n: int) -> int:
        await asyncio.sleep(0.05)
        finished.append(n)
        return n

    batch = asyncio.ensure_future(gather_limited(*(slow(n) for n in range(20)), max_concurrency=2))
    await asyncio.sleep(0.01)
    batch.cancel()
    with pytest.raises(asyncio.CancelledError):
        await batch

    await asyncio.sleep(0.1)
    assert finished == []


@pytest.mark.asyncio
async def test_cancelled_batch_does_not_warn_about_unawaited_coroutines(recwarn):
    """Work still queued behind the semaphore was never awaited — close it quietly."""

    async def slow(n: int) -> int:
        await asyncio.sleep(0.05)
        return n

    async def boom() -> int:
        await asyncio.sleep(0.01)
        raise ValueError("kaboom")

    # max_concurrency=1 leaves nearly every input queued when the failure lands.
    with pytest.raises(ValueError, match="kaboom"):
        await gather_limited(boom(), *(slow(n) for n in range(20)), max_concurrency=1)

    gc.collect()  # un-awaited coroutines only complain once collected
    assert [w for w in recwarn if issubclass(w.category, RuntimeWarning)] == []
