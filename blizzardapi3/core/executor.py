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
MAX_RETRIES = 2          # transient-failure retries (429/5xx), on top of the first attempt
BACKOFF_BASE = 0.5       # seconds; exponential base for retries lacking a Retry-After
BACKOFF_CAP = 8.0        # seconds; ceiling for computed (non-Retry-After) backoff


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


class RequestExecutor:
    """Executes a request with automatic token refresh on 401.

    Sync and async paths are ~15 lines each. All error translation,
    JSON decoding, and retry policy is shared via :func:`_decode`.
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

    def execute(
        self,
        *,
        region: str,
        path: str,
        params: dict[str, Any],
        client: httpx.Client,
    ) -> ApiResponse:
        url = f"{BASE_URL.format(region=region)}{path}"
        user_token = params.pop("access_token", None)

        # User-token requests bypass the cache entirely: their responses may be
        # caller-scoped, so they must never be stored under a shared key nor
        # served to a different caller.
        cache = self._cache if user_token is None else None
        if cache is not None:
            cached = cache.get(region, path, params)
            if cached is not None:
                return cached

        token = user_token or self._tokens.get_token(region, client)

        for attempt in range(self._max_retries + 1):
            response = client.get(url, params=params, headers=_auth(token), timeout=REQUEST_TIMEOUT)

            if response.status_code == 401 and not user_token:
                self._tokens.invalidate()
                token = self._tokens.get_token(region, client)
                response = client.get(url, params=params, headers=_auth(token), timeout=REQUEST_TIMEOUT)

            if attempt < self._max_retries and _is_retryable(response.status_code):
                time.sleep(_retry_delay(response, attempt))
                continue

            result = _decode(response, url)
            if cache is not None:
                cache.store(region, path, params, result)
            return result

        raise RuntimeError("unreachable: retry loop always returns or raises")

    async def execute_async(
        self,
        *,
        region: str,
        path: str,
        params: dict[str, Any],
        client: httpx.AsyncClient,
    ) -> ApiResponse:
        url = f"{BASE_URL.format(region=region)}{path}"
        user_token = params.pop("access_token", None)

        cache = self._cache if user_token is None else None
        if cache is not None:
            cached = cache.get(region, path, params)
            if cached is not None:
                return cached

        token = user_token or await self._tokens.get_token_async(region, client)

        for attempt in range(self._max_retries + 1):
            response = await client.get(url, params=params, headers=_auth(token), timeout=REQUEST_TIMEOUT)

            if response.status_code == 401 and not user_token:
                self._tokens.invalidate()
                token = await self._tokens.get_token_async(region, client)
                response = await client.get(url, params=params, headers=_auth(token), timeout=REQUEST_TIMEOUT)

            if attempt < self._max_retries and _is_retryable(response.status_code):
                await asyncio.sleep(_retry_delay(response, attempt))
                continue

            result = _decode(response, url)
            if cache is not None:
                cache.store(region, path, params, result)
            return result

        raise RuntimeError("unreachable: retry loop always returns or raises")


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
