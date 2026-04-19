"""Unit tests for RequestExecutor — error translation, 401 retry, user tokens."""

from __future__ import annotations

import httpx
import pytest

from blizzardapi3.core.auth import TokenManager
from blizzardapi3.core.executor import ApiResponse, RequestExecutor
from blizzardapi3.exceptions import (
    BadRequestError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    RequestError,
    ServerError,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _Calls:
    """Tiny recorder used by the mock handlers below."""

    def __init__(self) -> None:
        self.requests: list[httpx.Request] = []


def _token_manager_with(token: str = "cached") -> TokenManager:
    """Build a TokenManager that reports a valid cached token without hitting the network."""
    import time as _time

    tm = TokenManager("id", "secret")
    tm._token = token
    tm._expires_at = _time.time() + 10_000
    return tm


def _build_executor(
    token: str = "cached",
) -> tuple[RequestExecutor, TokenManager, _Calls]:
    return RequestExecutor(_token_manager_with(token)), _token_manager_with(token), _Calls()


# ---------------------------------------------------------------------------
# ApiResponse shape
# ---------------------------------------------------------------------------


def test_api_response_preserves_dict_access_and_metadata():
    resp = ApiResponse({"id": 6, "name": "Level 10"}, {"X-Foo": "bar"}, 200)
    assert resp["id"] == 6
    assert resp["name"] == "Level 10"
    assert resp.headers == {"X-Foo": "bar"}
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Sync success / retry paths
# ---------------------------------------------------------------------------


def test_execute_returns_api_response_on_200():
    tm = _token_manager_with("cached")
    calls = _Calls()

    def handler(request: httpx.Request) -> httpx.Response:
        calls.requests.append(request)
        return httpx.Response(200, json={"id": 6}, headers={"x-ns": "static-us"})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        executor = RequestExecutor(tm)
        resp = executor.execute(
            region="us",
            path="/data/wow/achievement/6",
            params={"namespace": "static-us", "locale": "en_US"},
            client=client,
        )

    assert isinstance(resp, ApiResponse)
    assert resp["id"] == 6
    assert resp.status_code == 200
    assert resp.headers["x-ns"] == "static-us"
    assert calls.requests[0].headers["authorization"] == "Bearer cached"
    assert "namespace=static-us" in str(calls.requests[0].url)


def test_execute_retries_once_on_401_with_fresh_token():
    import time as _time

    tm = TokenManager("id", "secret")
    tm._token = "stale"
    tm._expires_at = _time.time() + 10_000

    calls = _Calls()

    def handler(request: httpx.Request) -> httpx.Response:
        calls.requests.append(request)
        # OAuth token refresh request
        if "battle.net" in str(request.url):
            return httpx.Response(200, json={"access_token": "fresh", "expires_in": 86400})
        # Data request: first call 401, second call 200
        data_calls = [r for r in calls.requests if "battle.net" not in str(r.url)]
        if len(data_calls) == 1:
            return httpx.Response(401, json={"error": "unauthorized"})
        return httpx.Response(200, json={"id": 6})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        executor = RequestExecutor(tm)
        resp = executor.execute(
            region="us",
            path="/data/wow/achievement/6",
            params={"namespace": "static-us", "locale": "en_US"},
            client=client,
        )

    assert resp["id"] == 6
    # Two data calls (401 + retry), one token refresh
    data_calls = [r for r in calls.requests if "battle.net" not in str(r.url)]
    assert len(data_calls) == 2
    assert data_calls[0].headers["authorization"] == "Bearer stale"
    assert data_calls[1].headers["authorization"] == "Bearer fresh"


def test_execute_user_token_is_used_and_not_retried():
    tm = _token_manager_with("cached")
    calls = _Calls()

    def handler(request: httpx.Request) -> httpx.Response:
        calls.requests.append(request)
        return httpx.Response(401, json={"error": "unauthorized"})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        executor = RequestExecutor(tm)
        with pytest.raises(RequestError):
            executor.execute(
                region="us",
                path="/profile/user/wow",
                params={"namespace": "profile-us", "locale": "en_US", "access_token": "usertoken"},
                client=client,
            )

    # One request (no retry), user-supplied bearer token, access_token stripped from query
    assert len(calls.requests) == 1
    assert calls.requests[0].headers["authorization"] == "Bearer usertoken"
    assert "access_token" not in str(calls.requests[0].url)


# ---------------------------------------------------------------------------
# Sync error translation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "status, exc_type",
    [
        (400, BadRequestError),
        (403, ForbiddenError),
        (404, NotFoundError),
        (500, ServerError),
        (503, ServerError),
        (418, RequestError),
    ],
)
def test_execute_translates_http_errors(status: int, exc_type: type[Exception]):
    tm = _token_manager_with()

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, json={"error": "boom"})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        executor = RequestExecutor(tm)
        with pytest.raises(exc_type) as exc_info:
            executor.execute(region="us", path="/x", params={"locale": "en_US"}, client=client)

    assert exc_info.value.status_code == status


def test_execute_rate_limit_preserves_retry_after():
    tm = _token_manager_with()

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, headers={"Retry-After": "30"}, json={"error": "rate limited"})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        executor = RequestExecutor(tm)
        with pytest.raises(RateLimitError) as exc_info:
            executor.execute(region="us", path="/x", params={"locale": "en_US"}, client=client)

    assert exc_info.value.status_code == 429
    assert exc_info.value.retry_after == 30


# ---------------------------------------------------------------------------
# Async paths
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_execute_async_returns_api_response_on_200():
    tm = _token_manager_with("cached")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"id": 42})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        executor = RequestExecutor(tm)
        resp = await executor.execute_async(
            region="us",
            path="/data/wow/achievement/42",
            params={"namespace": "static-us", "locale": "en_US"},
            client=client,
        )

    assert resp["id"] == 42


@pytest.mark.asyncio
async def test_execute_async_translates_errors():
    tm = _token_manager_with()

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"error": "nope"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        executor = RequestExecutor(tm)
        with pytest.raises(NotFoundError):
            await executor.execute_async(region="us", path="/x", params={"locale": "en_US"}, client=client)
