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
from .cache import ResponseCache

BASE_URL = "https://{region}.api.blizzard.com"
REQUEST_TIMEOUT = 30.0
MAX_RETRIES = 2  # transient-failure retries (429/5xx), on top of the first attempt
BACKOFF_BASE = 0.5  # seconds; exponential base for retries lacking a Retry-After
BACKOFF_CAP = 8.0  # seconds; ceiling for computed (non-Retry-After) backoff


class ApiResponse(dict):
    """dict with ``.headers`` and ``.status_code`` attached.

    Preserves v3's bracket-access contract while exposing HTTP metadata.
    """

    def __init__(self, data: dict[str, Any], headers: dict[str, str], status_code: int):
        super().__init__(data)
        self._headers = headers
        self._status_code = status_code

    @property
    def headers(self) -> dict[str, str]:
        return self._headers

    @property
    def status_code(self) -> int:
        return self._status_code


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

    def cached(self) -> ApiResponse | None:
        if self.cache is None:
            return None
        return self.cache.get(self.region, self.path, self.params)

    def should_reauth(self, response: httpx.Response) -> bool:
        """A 401 is worth re-authenticating only for tokens we manage."""
        return response.status_code == 401 and not self.user_token

    def retry_delay(self, response: httpx.Response, attempt: int) -> float | None:
        """Seconds to wait before retrying, or ``None`` to accept this response."""
        if attempt >= self.max_retries or not _is_retryable(response.status_code):
            return None
        return _retry_delay(response, attempt)

    def finish(self, response: httpx.Response) -> ApiResponse:
        result = _decode(response, self.url)
        if self.cache is not None:
            self.cache.store(self.region, self.path, self.params, result)
        return result


class RequestExecutor:
    """Executes a request with automatic token refresh on 401.

    Both paths are pure I/O drivers over :class:`_RequestPlan`, which owns the
    caching, re-auth, retry, and decoding policy.
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
        hit = plan.cached()
        if hit is not None:
            return hit

        token = plan.user_token or self._tokens.get_token(region, client)
        attempt = 0
        while True:
            response = client.get(plan.url, params=plan.params, headers=_auth(token), timeout=REQUEST_TIMEOUT)

            if plan.should_reauth(response):
                self._tokens.invalidate(token)
                token = self._tokens.get_token(region, client)
                response = client.get(plan.url, params=plan.params, headers=_auth(token), timeout=REQUEST_TIMEOUT)

            delay = plan.retry_delay(response, attempt)
            if delay is None:
                return plan.finish(response)
            time.sleep(delay)
            attempt += 1

    async def execute_async(
        self,
        *,
        region: str,
        path: str,
        params: dict[str, Any],
        client: httpx.AsyncClient,
    ) -> ApiResponse:
        plan = self._plan(region, path, params)
        hit = plan.cached()
        if hit is not None:
            return hit

        token = plan.user_token or await self._tokens.get_token_async(region, client)
        attempt = 0
        while True:
            response = await client.get(plan.url, params=plan.params, headers=_auth(token), timeout=REQUEST_TIMEOUT)

            if plan.should_reauth(response):
                self._tokens.invalidate(token)
                token = await self._tokens.get_token_async(region, client)
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


def _decode(response: httpx.Response, url: str) -> ApiResponse:
    """Turn an ``httpx.Response`` into :class:`ApiResponse` or raise an error.

    Works for both sync and async — ``httpx.Response.json()`` is synchronous
    in both transports.
    """
    if response.status_code == 200:
        return ApiResponse(response.json(), dict(response.headers), 200)

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
