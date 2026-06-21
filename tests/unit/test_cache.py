"""Unit tests for the response cache — directive parsing, TTL, executor wiring."""

from __future__ import annotations

import time as _time

import httpx
import pytest

from blizzardapi3.core.auth import TokenManager
from blizzardapi3.core.cache import ResponseCache, _make_key, _max_age
from blizzardapi3.core.executor import ApiResponse, RequestExecutor


def _token_manager() -> TokenManager:
    tm = TokenManager("id", "secret")
    tm._token = "cached"
    tm._expires_at = _time.time() + 10_000
    return tm


# ---------------------------------------------------------------------------
# Cache-Control parsing
# ---------------------------------------------------------------------------


def test_max_age_reads_directive():
    assert _max_age({"cache-control": "public, max-age=86400"}, None) == 86400


def test_max_age_no_store_overrides_even_with_default():
    assert _max_age({"cache-control": "no-store"}, 300) is None
    assert _max_age({"cache-control": "private, max-age=60"}, 300) is None


def test_max_age_absent_header_falls_back_to_default():
    assert _max_age({}, None) is None
    assert _max_age({}, 300) == 300


def test_max_age_zero_is_not_cached():
    assert _max_age({"cache-control": "max-age=0"}, 300) is None


# ---------------------------------------------------------------------------
# ResponseCache behavior
# ---------------------------------------------------------------------------


def _resp(data, headers):
    return ApiResponse(data, headers, 200)


def test_store_and_get_roundtrip():
    cache = ResponseCache()
    resp = _resp({"id": 6}, {"cache-control": "max-age=100"})
    cache.store("us", "/a", {"locale": "en_US"}, resp)
    assert cache.get("us", "/a", {"locale": "en_US"})["id"] == 6


def test_param_order_does_not_affect_key():
    cache = ResponseCache()
    resp = _resp({"id": 6}, {"cache-control": "max-age=100"})
    cache.store("us", "/a", {"namespace": "static-us", "locale": "en_US"}, resp)
    assert cache.get("us", "/a", {"locale": "en_US", "namespace": "static-us"}) is not None


def test_uncacheable_response_is_not_stored():
    cache = ResponseCache()
    cache.store("us", "/a", {}, _resp({"id": 6}, {}))  # no cache-control
    assert cache.get("us", "/a", {}) is None


def test_default_ttl_caches_header_less_response():
    cache = ResponseCache(default_ttl=300)
    cache.store("us", "/profile", {}, _resp({"name": "Beyloc"}, {}))
    assert cache.get("us", "/profile", {})["name"] == "Beyloc"


def test_expired_entry_is_evicted_on_get():
    cache = ResponseCache()
    cache.store("us", "/a", {}, _resp({"id": 6}, {"cache-control": "max-age=1"}))
    key = _make_key("us", "/a", {})
    # Force expiry by rewriting the stored deadline into the past.
    response, _ = cache._store[key]
    cache._store[key] = (response, _time.monotonic() - 1)
    assert cache.get("us", "/a", {}) is None


def test_lru_eviction_respects_max_entries():
    cache = ResponseCache(max_entries=2)
    for i in range(3):
        cache.store("us", f"/a{i}", {}, _resp({"id": i}, {"cache-control": "max-age=100"}))
    # First inserted should have been evicted.
    assert cache.get("us", "/a0", {}) is None
    assert cache.get("us", "/a2", {}) is not None


# ---------------------------------------------------------------------------
# Executor integration
# ---------------------------------------------------------------------------


def test_cache_hit_skips_second_network_call():
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200, json={"id": 6}, headers={"cache-control": "max-age=100"})

    cache = ResponseCache()
    executor = RequestExecutor(_token_manager(), cache=cache)
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        first = executor.execute(region="us", path="/data/wow/achievement/6", params={"locale": "en_US"}, client=client)
        second = executor.execute(region="us", path="/data/wow/achievement/6", params={"locale": "en_US"}, client=client)

    assert first["id"] == second["id"] == 6
    assert len(calls) == 1  # second served from cache


def test_response_without_cache_control_is_refetched():
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200, json={"name": "Beyloc"})  # no cache-control (profile data)

    executor = RequestExecutor(_token_manager(), cache=ResponseCache())
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        executor.execute(region="us", path="/profile/.../equipment", params={"locale": "en_US"}, client=client)
        executor.execute(region="us", path="/profile/.../equipment", params={"locale": "en_US"}, client=client)

    assert len(calls) == 2  # uncacheable, so two real calls


def test_user_token_request_bypasses_cache():
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200, json={"id": 6}, headers={"cache-control": "max-age=100"})

    executor = RequestExecutor(_token_manager(), cache=ResponseCache())
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        executor.execute(
            region="us", path="/profile/user/wow",
            params={"locale": "en_US", "access_token": "usertoken"}, client=client,
        )
        executor.execute(
            region="us", path="/profile/user/wow",
            params={"locale": "en_US", "access_token": "usertoken"}, client=client,
        )

    assert len(calls) == 2  # user-token responses are never cached


@pytest.mark.asyncio
async def test_async_cache_hit_skips_second_network_call():
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200, json={"id": 42}, headers={"cache-control": "max-age=100"})

    executor = RequestExecutor(_token_manager(), cache=ResponseCache())
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        await executor.execute_async(region="us", path="/data/wow/achievement/42", params={"locale": "en_US"}, client=client)
        await executor.execute_async(region="us", path="/data/wow/achievement/42", params={"locale": "en_US"}, client=client)

    assert len(calls) == 1
