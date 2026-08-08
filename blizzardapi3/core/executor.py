"""Unified request executor — one implementation, sync and async paths."""

from __future__ import annotations

import asyncio
import random
import time
from typing import Any

import httpx

from ..exceptions import (
    BadRequestError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    RequestError,
    ServerError,
)
from .auth import TokenManager
from .cache import CacheKey, ResponseCache, _make_key
from .response import ApiResponse, RawResponse

BASE_URL = "https://{region}.api.blizzard.com"
REQUEST_TIMEOUT = 30.0
MAX_RETRIES = 2  # transient-failure retries (429/5xx), on top of the first attempt
BACKOFF_BASE = 0.5  # seconds; exponential base for retries lacking a Retry-After
BACKOFF_CAP = 8.0  # seconds; ceiling for computed (non-Retry-After) backoff


class _RequestPlan:
    """Every decision for one request, resolved once and without I/O.

    The sync and async executors differ only in how they perform I/O. Keeping
    the decisions here means there is one place to change policy, and it can be
    tested without a transport.
    """

    __slots__ = ("cache", "max_retries", "params", "path", "region", "url", "user_token")

    def __init__(
        self,
        region: str,
        path: str,
        params: dict[str, Any],
        cache: ResponseCache | None,
        max_retries: int,
    ):
        user_token = params.get("access_token")
        if "access_token" in params:
            # Copy rather than pop: the caller's dict is theirs, not ours.
            params = {k: v for k, v in params.items() if k != "access_token"}

        self.region = region
        self.path = path
        self.params = params
        self.url = f"{BASE_URL.format(region=region)}{path}"
        self.user_token = user_token
        # User-token requests bypass the cache entirely: their responses may be
        # caller-scoped, so they must never be stored under a shared key nor
        # served to a different caller.
        self.cache = cache if user_token is None else None
        self.max_retries = max_retries

    def cached(self) -> RawResponse | None:
        if self.cache is None:
            return None
        return self.cache.get(self.region, self.path, self.params)

    def cache_key(self) -> CacheKey:
        return _make_key(self.region, self.path, self.params)

    def should_reauth(self, response: httpx.Response) -> bool:
        """A 401 is worth re-authenticating only for tokens we manage."""
        return response.status_code == 401 and not self.user_token

    def retry_delay(self, response: httpx.Response, attempt: int) -> float | None:
        """Seconds to wait before retrying, or ``None`` to accept this response."""
        if attempt >= self.max_retries or not _is_retryable(response.status_code):
            return None
        return _retry_delay(response, attempt)

    def finish(self, response: httpx.Response) -> RawResponse:
        raw = _decode(response, self.url)
        if self.cache is not None:
            self.cache.store(self.region, self.path, self.params, raw)
        return raw


class RequestExecutor:
    """Executes a request with automatic token refresh on 401.

    Both paths are pure I/O drivers over :class:`_RequestPlan`, which owns the
    caching, re-auth, retry, and decoding policy. They deal in
    :class:`RawResponse` throughout and parse exactly once, on the way out — the
    single point where a caller stops sharing anything with the cache or with
    the peers it was coalesced against.
    """

    def __init__(
        self,
        token_manager: TokenManager,
        cache: ResponseCache | None = None,
        max_retries: int = MAX_RETRIES,
    ):
        self._tokens = token_manager
        self._cache = cache
        self._max_retries = max_retries
        self._inflight: dict[CacheKey, asyncio.Task[RawResponse]] = {}

    def _plan(self, region: str, path: str, params: dict[str, Any]) -> _RequestPlan:
        return _RequestPlan(region, path, params, self._cache, self._max_retries)

    def execute(
        self,
        *,
        region: str,
        path: str,
        params: dict[str, Any],
        client: httpx.Client,
    ) -> ApiResponse:
        plan = self._plan(region, path, params)
        raw = plan.cached()
        if raw is None:
            raw = self._send(plan, client)
        return raw.parse()

    async def execute_async(
        self,
        *,
        region: str,
        path: str,
        params: dict[str, Any],
        client: httpx.AsyncClient,
    ) -> ApiResponse:
        plan = self._plan(region, path, params)
        raw = plan.cached()
        if raw is None:
            raw = await self._coalesced_async(plan, client)
        return raw.parse()

    def _send(self, plan: _RequestPlan, client: httpx.Client) -> RawResponse:
        token = plan.user_token or self._tokens.get_token(plan.region, client)
        attempt = 0
        while True:
            response = client.get(plan.url, params=plan.params, headers=_auth(token), timeout=REQUEST_TIMEOUT)

            if plan.should_reauth(response):
                self._tokens.invalidate(token)
                token = self._tokens.get_token(plan.region, client)
                response = client.get(plan.url, params=plan.params, headers=_auth(token), timeout=REQUEST_TIMEOUT)

            delay = plan.retry_delay(response, attempt)
            if delay is None:
                return plan.finish(response)
            time.sleep(delay)
            attempt += 1

    async def _coalesced_async(self, plan: _RequestPlan, client: httpx.AsyncClient) -> RawResponse:
        if plan.cache is None:
            return await self._send_async(plan, client)

        # Cacheable and not yet cached: a fan-out over one resource would
        # otherwise send N identical requests, because every caller misses
        # before any of them stores. Share one in-flight request instead.
        key = plan.cache_key()
        leader = self._inflight.get(key)
        if leader is None:
            leader = asyncio.ensure_future(self._send_async(plan, client))
            self._inflight[key] = leader
            leader.add_done_callback(lambda _: self._inflight.pop(key, None))
        # Shielded: a caller that gets cancelled must not cancel the request
        # the other callers are waiting on.
        return await asyncio.shield(leader)

    async def _send_async(self, plan: _RequestPlan, client: httpx.AsyncClient) -> RawResponse:
        token = plan.user_token or await self._tokens.get_token_async(plan.region, client)
        attempt = 0
        while True:
            response = await client.get(plan.url, params=plan.params, headers=_auth(token), timeout=REQUEST_TIMEOUT)

            if plan.should_reauth(response):
                self._tokens.invalidate(token)
                token = await self._tokens.get_token_async(plan.region, client)
                response = await client.get(plan.url, params=plan.params, headers=_auth(token), timeout=REQUEST_TIMEOUT)

            delay = plan.retry_delay(response, attempt)
            if delay is None:
                return plan.finish(response)
            await asyncio.sleep(delay)
            attempt += 1


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _is_retryable(status: int) -> bool:
    """A 429 or any 5xx is a transient failure worth retrying (GETs are idempotent)."""
    return status == 429 or 500 <= status < 600


def _retry_delay(response: httpx.Response, attempt: int) -> float:
    """Seconds to wait before the next attempt.

    A ``Retry-After`` (sent on 429) is authoritative — the server is telling us
    exactly when to come back, so we honor it. Otherwise we use full-jitter
    exponential backoff: ``random(0, min(cap, base * 2**attempt))``. The jitter
    spreads a fleet of concurrent callers out instead of having them all retry
    on the same beat (the thundering-herd problem).
    """
    retry_after = response.headers.get("retry-after")
    if retry_after is not None:
        try:
            return max(0.0, float(retry_after))
        except ValueError:
            pass
    return random.uniform(0, min(BACKOFF_CAP, BACKOFF_BASE * 2**attempt))


def _decode(response: httpx.Response, url: str) -> RawResponse:
    """Turn an ``httpx.Response`` into :class:`RawResponse` or raise an error.

    Works for both sync and async — the body has already been read by the time
    a response object exists in either transport.
    """
    if response.status_code == 200:
        return RawResponse(response.content, dict(response.headers), 200)

    try:
        body = response.json()
    except ValueError:
        body = None

    status = response.status_code
    match status:
        case 400:
            raise BadRequestError("Bad request", status_code=400, request_url=url, response_data=body)
        case 403:
            raise ForbiddenError("Forbidden", status_code=403, request_url=url, response_data=body)
        case 404:
            raise NotFoundError("Not found", status_code=404, request_url=url, response_data=body)
        case 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                "Rate limit exceeded",
                status_code=429,
                request_url=url,
                retry_after=int(retry_after) if retry_after else None,
                response_data=body,
            )
        case _ if 500 <= status < 600:
            raise ServerError(f"Server error: {status}", status_code=status, request_url=url, response_data=body)
        case _:
            raise RequestError(f"Request failed: {status}", status_code=status, request_url=url, response_data=body)
