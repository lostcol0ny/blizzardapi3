"""Unit tests for gather_limited — ordering, concurrency bound, error propagation."""

from __future__ import annotations

import asyncio

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
