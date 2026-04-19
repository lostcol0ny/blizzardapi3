"""Unit tests for the OAuth TokenManager."""

from __future__ import annotations

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
