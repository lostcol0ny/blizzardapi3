"""Unit tests for the response cache — directive parsing, TTL, executor wiring."""

from __future__ import annotations

import asyncio
import json
import time as _time

import httpx
import pytest

from blizzardapi3.core.auth import TokenManager
from blizzardapi3.core.cache import ResponseCache, _make_key, _max_age
from blizzardapi3.core.executor import RequestExecutor
from blizzardapi3.core.response import RawResponse
from blizzardapi3.exceptions import NotFoundError


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


def _raw(data, headers):
    return RawResponse(json.dumps(data).encode(), headers, 200)


def test_store_and_get_roundtrip():
    cache = ResponseCache()
    cache.store("us", "/a", {"locale": "en_US"}, _raw({"id": 6}, {"cache-control": "max-age=100"}))
    assert cache.get("us", "/a", {"locale": "en_US"}).parse()["id"] == 6


def test_param_order_does_not_affect_key():
    cache = ResponseCache()
    raw = _raw({"id": 6}, {"cache-control": "max-age=100"})
    cache.store("us", "/a", {"namespace": "static-us", "locale": "en_US"}, raw)
    assert cache.get("us", "/a", {"locale": "en_US", "namespace": "static-us"}) is not None


def test_uncacheable_response_is_not_stored():
    cache = ResponseCache()
    cache.store("us", "/a", {}, _raw({"id": 6}, {}))  # no cache-control
    assert cache.get("us", "/a", {}) is None


def test_default_ttl_caches_header_less_response():
    cache = ResponseCache(default_ttl=300)
    cache.store("us", "/profile", {}, _raw({"name": "Beyloc"}, {}))
    assert cache.get("us", "/profile", {}).parse()["name"] == "Beyloc"


def test_expired_entry_is_evicted_on_get():
    cache = ResponseCache()
    cache.store("us", "/a", {}, _raw({"id": 6}, {"cache-control": "max-age=1"}))
    key = _make_key("us", "/a", {})
    # Force expiry by rewriting the stored deadline into the past.
    raw, _ = cache._store[key]
    cache._store[key] = (raw, _time.monotonic() - 1)
    assert cache.get("us", "/a", {}) is None


def test_lru_eviction_respects_max_entries():
    cache = ResponseCache(max_entries=2)
    for i in range(3):
        cache.store("us", f"/a{i}", {}, _raw({"id": i}, {"cache-control": "max-age=100"}))
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
        second = executor.execute(
            region="us", path="/data/wow/achievement/6", params={"locale": "en_US"}, client=client
        )

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
            region="us",
            path="/profile/user/wow",
            params={"locale": "en_US", "access_token": "usertoken"},
            client=client,
        )
        executor.execute(
            region="us",
            path="/profile/user/wow",
            params={"locale": "en_US", "access_token": "usertoken"},
            client=client,
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
        await executor.execute_async(
            region="us", path="/data/wow/achievement/42", params={"locale": "en_US"}, client=client
        )
        await executor.execute_async(
            region="us", path="/data/wow/achievement/42", params={"locale": "en_US"}, client=client
        )

    assert len(calls) == 1


# ---------------------------------------------------------------------------
# Single-flight (async)
# ---------------------------------------------------------------------------


def _slow_handler(calls: list[httpx.Request], status: int = 200, cacheable: bool = True):
    """Handler slow enough that concurrent callers pile up behind the first."""
    headers = {"cache-control": "public, max-age=86400"} if cacheable else {}

    async def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        await asyncio.sleep(0.02)
        return httpx.Response(status, json={"id": 6}, headers=headers)

    return handler


@pytest.mark.asyncio
async def test_concurrent_calls_for_one_key_share_a_single_request():
    calls: list[httpx.Request] = []
    executor = RequestExecutor(_token_manager(), cache=ResponseCache())

    async with httpx.AsyncClient(transport=httpx.MockTransport(_slow_handler(calls))) as client:
        results = await asyncio.gather(
            *(
                executor.execute_async(region="us", path="/data/wow/achievement/6", params={}, client=client)
                for _ in range(50)
            )
        )

    assert len(calls) == 1
    assert all(r["id"] == 6 for r in results)
    assert executor._inflight == {}, "the in-flight entry must be released once the request settles"


@pytest.mark.asyncio
async def test_distinct_keys_are_not_collapsed():
    calls: list[httpx.Request] = []
    executor = RequestExecutor(_token_manager(), cache=ResponseCache())

    async with httpx.AsyncClient(transport=httpx.MockTransport(_slow_handler(calls))) as client:
        await asyncio.gather(
            *(
                executor.execute_async(region="us", path=f"/data/wow/achievement/{i}", params={}, client=client)
                for i in range(20)
            )
        )
        await asyncio.gather(
            *(
                executor.execute_async(region="us", path="/data/wow/realm/1", params={"locale": loc}, client=client)
                for loc in ("en_US", "de_DE")
            )
        )

    assert len(calls) == 22  # 20 distinct paths + 2 distinct locales


@pytest.mark.asyncio
async def test_followers_see_the_leaders_failure():
    calls: list[httpx.Request] = []
    executor = RequestExecutor(_token_manager(), cache=ResponseCache(), max_retries=0)

    async with httpx.AsyncClient(transport=httpx.MockTransport(_slow_handler(calls, status=404))) as client:
        results = await asyncio.gather(
            *(
                executor.execute_async(region="us", path="/data/wow/achievement/6", params={}, client=client)
                for _ in range(10)
            ),
            return_exceptions=True,
        )

    assert len(calls) == 1
    assert all(isinstance(r, NotFoundError) for r in results)


@pytest.mark.asyncio
async def test_cancelling_one_caller_does_not_cancel_the_others():
    calls: list[httpx.Request] = []
    executor = RequestExecutor(_token_manager(), cache=ResponseCache())

    async with httpx.AsyncClient(transport=httpx.MockTransport(_slow_handler(calls))) as client:
        tasks = [
            asyncio.ensure_future(
                executor.execute_async(region="us", path="/data/wow/achievement/6", params={}, client=client)
            )
            for _ in range(5)
        ]
        await asyncio.sleep(0)  # let them all register against the same key
        tasks[0].cancel()
        results = await asyncio.gather(*tasks, return_exceptions=True)

    assert len(calls) == 1
    assert isinstance(results[0], asyncio.CancelledError)
    assert all(r["id"] == 6 for r in results[1:])


@pytest.mark.asyncio
async def test_user_token_calls_are_never_shared():
    calls: list[httpx.Request] = []
    executor = RequestExecutor(_token_manager(), cache=ResponseCache())

    async with httpx.AsyncClient(transport=httpx.MockTransport(_slow_handler(calls))) as client:
        await asyncio.gather(
            *(
                executor.execute_async(
                    region="us", path="/profile/user/wow", params={"access_token": "user-tok"}, client=client
                )
                for _ in range(5)
            )
        )

    assert len(calls) == 5, "caller-scoped responses must not be served to a different caller"


# ---------------------------------------------------------------------------
# Caller isolation
# ---------------------------------------------------------------------------


def _nested_handler(calls: list[httpx.Request]):
    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(
            200,
            json={"realms": [{"name": "Illidan"}]},
            headers={"cache-control": "max-age=100"},
        )

    return handler


def test_mutating_a_cached_response_does_not_affect_the_next_reader():
    calls: list[httpx.Request] = []
    executor = RequestExecutor(_token_manager(), cache=ResponseCache())

    with httpx.Client(transport=httpx.MockTransport(_nested_handler(calls))) as client:
        first = executor.execute(region="us", path="/data/wow/realm/index", params={}, client=client)
        first["realms"][0]["name"] = "poisoned"
        first.headers["cache-control"] = "poisoned"
        second = executor.execute(region="us", path="/data/wow/realm/index", params={}, client=client)

    assert len(calls) == 1, "the second call must still be a cache hit"
    assert second is not first
    assert second["realms"][0]["name"] == "Illidan"
    assert second.headers["cache-control"] == "max-age=100"


@pytest.mark.asyncio
async def test_coalesced_callers_do_not_share_one_response_object():
    calls: list[httpx.Request] = []
    executor = RequestExecutor(_token_manager(), cache=ResponseCache())

    async def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        await asyncio.sleep(0.02)  # hold the leader open so followers pile up
        return httpx.Response(
            200,
            json={"realms": [{"name": "Illidan"}]},
            headers={"cache-control": "max-age=100"},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        results = await asyncio.gather(
            *(
                executor.execute_async(region="us", path="/data/wow/realm/index", params={}, client=client)
                for _ in range(10)
            )
        )

    assert len(calls) == 1
    results[0]["realms"][0]["name"] = "poisoned"
    assert all(r["realms"][0]["name"] == "Illidan" for r in results[1:])
    assert len({id(r) for r in results}) == 10
