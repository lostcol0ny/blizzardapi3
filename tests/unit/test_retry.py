"""Unit tests for transient-failure retries — 429/5xx, Retry-After, backoff bounds."""

from __future__ import annotations

import time as _time
from unittest.mock import AsyncMock

import httpx
import pytest

from blizzardapi3.core.auth import TokenManager
from blizzardapi3.core.executor import (
    BACKOFF_CAP,
    RequestExecutor,
    _is_retryable,
    _retry_delay,
)
from blizzardapi3.exceptions import RateLimitError, ServerError


def _token_manager() -> TokenManager:
    tm = TokenManager("id", "secret")
    tm._token = "cached"
    tm._expires_at = _time.time() + 10_000
    return tm


def _counter():
    calls: list[httpx.Request] = []
    return calls


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("status, retryable", [(429, True), (500, True), (503, True), (400, False), (404, False), (200, False)])
def test_is_retryable(status: int, retryable: bool):
    assert _is_retryable(status) is retryable


def test_retry_delay_honors_retry_after():
    resp = httpx.Response(429, headers={"Retry-After": "7"})
    assert _retry_delay(resp, 0) == 7.0


def test_retry_delay_backoff_stays_within_cap():
    resp = httpx.Response(503)
    for attempt in range(6):
        assert 0.0 <= _retry_delay(resp, attempt) <= BACKOFF_CAP


# ---------------------------------------------------------------------------
# Sync retry behavior
# ---------------------------------------------------------------------------


def test_retries_429_then_succeeds(mocker):
    sleep = mocker.patch("blizzardapi3.core.executor.time.sleep")
    calls = _counter()

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        if len(calls) == 1:
            return httpx.Response(429, headers={"Retry-After": "0"}, json={"error": "slow down"})
        return httpx.Response(200, json={"id": 6})

    executor = RequestExecutor(_token_manager(), max_retries=2)
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        resp = executor.execute(region="us", path="/x", params={"locale": "en_US"}, client=client)

    assert resp["id"] == 6
    assert len(calls) == 2
    sleep.assert_called_once()


def test_retries_exhausted_raises_last_error(mocker):
    mocker.patch("blizzardapi3.core.executor.time.sleep")
    calls = _counter()

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(503, json={"error": "down"})

    executor = RequestExecutor(_token_manager(), max_retries=2)
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(ServerError):
            executor.execute(region="us", path="/x", params={"locale": "en_US"}, client=client)

    assert len(calls) == 3  # first attempt + 2 retries


def test_max_retries_zero_surfaces_immediately(mocker):
    sleep = mocker.patch("blizzardapi3.core.executor.time.sleep")
    calls = _counter()

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(429, headers={"Retry-After": "1"}, json={"error": "slow down"})

    executor = RequestExecutor(_token_manager(), max_retries=0)
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(RateLimitError):
            executor.execute(region="us", path="/x", params={"locale": "en_US"}, client=client)

    assert len(calls) == 1
    sleep.assert_not_called()


# ---------------------------------------------------------------------------
# Async retry behavior
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_async_retries_503_then_succeeds(mocker):
    sleep = mocker.patch("blizzardapi3.core.executor.asyncio.sleep", new_callable=AsyncMock)
    calls = _counter()

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        if len(calls) == 1:
            return httpx.Response(503, json={"error": "down"})
        return httpx.Response(200, json={"id": 42})

    executor = RequestExecutor(_token_manager(), max_retries=2)
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        resp = await executor.execute_async(region="us", path="/x", params={"locale": "en_US"}, client=client)

    assert resp["id"] == 42
    assert len(calls) == 2
    sleep.assert_awaited_once()
