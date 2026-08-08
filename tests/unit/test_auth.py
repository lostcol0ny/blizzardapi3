"""Unit tests for the OAuth TokenManager."""

from __future__ import annotations

import asyncio
import threading
import time

import httpx
import pytest

from blizzardapi3.core.auth import TOKEN_BUFFER_SECONDS, TokenManager, _oauth_url
from blizzardapi3.exceptions import TokenError


def _mock_transport(status: int, body: dict | str) -> httpx.MockTransport:
    """Build an httpx transport that always returns ``(status, body)``."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, json=body) if isinstance(body, dict) else httpx.Response(status, text=body)

    return httpx.MockTransport(handler)


def test_oauth_url_regions():
    assert _oauth_url("us") == "https://us.battle.net/oauth/token"
    assert _oauth_url("eu") == "https://eu.battle.net/oauth/token"
    assert _oauth_url("cn") == "https://oauth.battlenet.com.cn/token"


def test_is_valid_starts_false():
    tm = TokenManager("id", "secret")
    assert tm.is_valid() is False


def test_get_token_caches_successful_response():
    tm = TokenManager("id", "secret")
    transport = _mock_transport(200, {"access_token": "abc", "expires_in": 86400, "token_type": "bearer"})
    with httpx.Client(transport=transport) as client:
        token1 = tm.get_token("us", client)
        token2 = tm.get_token("us", client)
    assert token1 == token2 == "abc"
    assert tm.is_valid() is True


def test_is_valid_respects_buffer():
    tm = TokenManager("id", "secret")
    tm._token = "abc"
    tm._expires_at = time.time() + TOKEN_BUFFER_SECONDS - 10
    assert tm.is_valid() is False


def test_invalidate_clears_token():
    tm = TokenManager("id", "secret")
    tm._token = "abc"
    tm._expires_at = time.time() + 10_000
    assert tm.is_valid() is True
    tm.invalidate()
    assert tm.is_valid() is False


def test_get_token_raises_on_non_200():
    tm = TokenManager("id", "secret")
    transport = _mock_transport(401, {"error": "invalid_client"})
    with httpx.Client(transport=transport) as client:
        with pytest.raises(TokenError) as exc_info:
            tm.get_token("us", client)
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_token_async_caches_successful_response():
    tm = TokenManager("id", "secret")
    transport = _mock_transport(200, {"access_token": "abc", "expires_in": 86400, "token_type": "bearer"})
    async with httpx.AsyncClient(transport=transport) as client:
        token1 = await tm.get_token_async("us", client)
        token2 = await tm.get_token_async("us", client)
    assert token1 == token2 == "abc"


@pytest.mark.asyncio
async def test_get_token_async_raises_on_non_200():
    tm = TokenManager("id", "secret")
    transport = _mock_transport(500, {"error": "server_error"})
    async with httpx.AsyncClient(transport=transport) as client:
        with pytest.raises(TokenError):
            await tm.get_token_async("us", client)


def _counting_transport(delay: float = 0.0) -> tuple[httpx.MockTransport, list[int]]:
    """Transport issuing a uniquely numbered token per call, plus a POST counter."""
    count = [0]

    def handler(request: httpx.Request) -> httpx.Response:
        count[0] += 1
        if delay:
            time.sleep(delay)
        return httpx.Response(200, json={"access_token": f"T{count[0]}", "expires_in": 86400})

    return httpx.MockTransport(handler), count


def test_invalidate_ignores_a_token_that_is_no_longer_current():
    tm = TokenManager("id", "secret")
    tm._token = "fresh"
    tm._expires_at = time.time() + 10_000

    tm.invalidate("stale")
    assert tm.is_valid() is True, "a late 401 must not discard a token someone else refreshed"

    tm.invalidate("fresh")
    assert tm.is_valid() is False


@pytest.mark.asyncio
async def test_concurrent_cold_callers_share_one_token_request():
    tm = TokenManager("id", "secret")

    async def handler(request: httpx.Request) -> httpx.Response:
        count[0] += 1
        await asyncio.sleep(0.01)  # hold the acquisition open so callers pile up
        return httpx.Response(200, json={"access_token": f"T{count[0]}", "expires_in": 86400})

    count = [0]
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        tokens = await asyncio.gather(*(tm.get_token_async("us", client) for _ in range(50)))

    assert count[0] == 1
    assert set(tokens) == {"T1"}


def test_concurrent_threads_share_one_token_request():
    tm = TokenManager("id", "secret")
    transport, count = _counting_transport(delay=0.01)
    tokens: list[str] = []

    with httpx.Client(transport=transport) as client:
        threads = [threading.Thread(target=lambda: tokens.append(tm.get_token("us", client))) for _ in range(20)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    assert count[0] == 1
    assert set(tokens) == {"T1"}
