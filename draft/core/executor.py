"""Unified request executor — one implementation, sync and async paths."""

from __future__ import annotations

from typing import Any

import httpx

from blizzardapi3.exceptions import (
    BadRequestError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    RequestError,
    ServerError,
)

from .auth import TokenManager

BASE_URL = "https://{region}.api.blizzard.com"
REQUEST_TIMEOUT = 30.0


class ApiResponse(dict):
    """dict with `.headers` and `.status_code` attached.

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
    JSON decoding, and retry policy is shared.
    """

    def __init__(self, token_manager: TokenManager):
        self._tokens = token_manager

    def execute(
        self,
        *,
        region: str,
        path: str,
        params: dict[str, Any],
        client: httpx.Client,
        user_token: str | None = None,
    ) -> ApiResponse:
        url = f"{BASE_URL.format(region=region)}{path}"
        token = user_token or self._tokens.get_token(region, client)

        response = client.get(url, params=params, headers=_auth(token), timeout=REQUEST_TIMEOUT)

        if response.status_code == 401 and not user_token:
            self._tokens.invalidate()
            token = self._tokens.get_token(region, client)
            response = client.get(url, params=params, headers=_auth(token), timeout=REQUEST_TIMEOUT)

        return _decode(response, url)

    async def execute_async(
        self,
        *,
        region: str,
        path: str,
        params: dict[str, Any],
        client: httpx.AsyncClient,
        user_token: str | None = None,
    ) -> ApiResponse:
        url = f"{BASE_URL.format(region=region)}{path}"
        token = user_token or await self._tokens.get_token_async(region, client)

        response = await client.get(url, params=params, headers=_auth(token), timeout=REQUEST_TIMEOUT)

        if response.status_code == 401 and not user_token:
            self._tokens.invalidate()
            token = await self._tokens.get_token_async(region, client)
            response = await client.get(url, params=params, headers=_auth(token), timeout=REQUEST_TIMEOUT)

        return _decode(response, url)


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _decode(response: httpx.Response, url: str) -> ApiResponse:
    """Turn an httpx.Response into ApiResponse or raise an appropriate error.

    Works for both sync and async — httpx.Response.json() is sync in both paths.
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
