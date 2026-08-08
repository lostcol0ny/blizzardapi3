"""OAuth client-credentials token management (httpx-based)."""

from __future__ import annotations

import asyncio
import threading
import time
from typing import Any

import httpx

from ..exceptions import TokenError

TOKEN_BUFFER_SECONDS = 300
TOKEN_TIMEOUT = 10.0


class TokenManager:
    """Caches an OAuth token and refreshes it when near expiry.

    A single TokenManager is shared across sync and async clients — the
    underlying token is the same regardless of transport.

    Acquisition is coalesced: concurrent callers that find no valid token queue
    on a lock and re-check inside it, so a cold fan-out of N requests costs one
    token round-trip rather than N.
    """

    def __init__(self, client_id: str, client_secret: str):
        self._basic_auth = httpx.BasicAuth(client_id, client_secret)
        self._token: str | None = None
        self._expires_at: float | None = None
        # Separate locks because a threading.Lock cannot be held across an
        # await. Sync and async callers therefore only coalesce among
        # themselves; the worst case for a program using both is one redundant
        # token fetch, never a corrupt token.
        self._sync_lock = threading.Lock()
        self._async_lock = asyncio.Lock()

    def is_valid(self) -> bool:
        if self._token is None or self._expires_at is None:
            return False
        return time.time() < (self._expires_at - TOKEN_BUFFER_SECONDS)

    def invalidate(self, stale: str | None = None) -> None:
        """Discard the cached token.

        Pass the token that just failed. 401s from a burst of in-flight
        requests arrive staggered, so a caller holding an old token can return
        long after someone else refreshed — an unconditional clear would throw
        away that fresh token and restart the stampede. Naming the stale token
        makes the clear a no-op once it is no longer current.
        """
        if stale is not None and self._token != stale:
            return
        self._token = None
        self._expires_at = None

    def get_token(self, region: str, client: httpx.Client) -> str:
        if self.is_valid():
            return self._token  # type: ignore[return-value]
        with self._sync_lock:
            if self.is_valid():
                return self._token  # type: ignore[return-value]
            url = _oauth_url(region)
            response = client.post(
                url,
                auth=self._basic_auth,
                data={"grant_type": "client_credentials"},
                timeout=TOKEN_TIMEOUT,
            )
            return self._store(response, url)

    async def get_token_async(self, region: str, client: httpx.AsyncClient) -> str:
        if self.is_valid():
            return self._token  # type: ignore[return-value]
        async with self._async_lock:
            if self.is_valid():
                return self._token  # type: ignore[return-value]
            url = _oauth_url(region)
            response = await client.post(
                url,
                auth=self._basic_auth,
                data={"grant_type": "client_credentials"},
                timeout=TOKEN_TIMEOUT,
            )
            return self._store(response, url)

    def _store(self, response: httpx.Response, url: str) -> str:
        if response.status_code != 200:
            raise TokenError(
                f"Failed to obtain token: {response.status_code}",
                status_code=response.status_code,
                request_url=url,
                response_data=_safe_json(response),
            )
        data = response.json()
        token: str = data["access_token"]
        self._token = token
        self._expires_at = time.time() + data["expires_in"]
        return token


def _oauth_url(region: str) -> str:
    if region == "cn":
        return "https://oauth.battlenet.com.cn/token"
    return f"https://{region}.battle.net/oauth/token"


def _safe_json(response: httpx.Response) -> dict[str, Any] | None:
    try:
        return response.json()
    except ValueError:
        return None
