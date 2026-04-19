"""OAuth client-credentials token management (httpx-based)."""

from __future__ import annotations

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
    """

    def __init__(self, client_id: str, client_secret: str):
        self._basic_auth = httpx.BasicAuth(client_id, client_secret)
        self._token: str | None = None
        self._expires_at: float | None = None

    def is_valid(self) -> bool:
        if self._token is None or self._expires_at is None:
            return False
        return time.time() < (self._expires_at - TOKEN_BUFFER_SECONDS)

    def invalidate(self) -> None:
        self._token = None
        self._expires_at = None

    def get_token(self, region: str, client: httpx.Client) -> str:
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
        self._token = data["access_token"]
        self._expires_at = time.time() + data["expires_in"]
        return self._token


def _oauth_url(region: str) -> str:
    if region == "cn":
        return "https://oauth.battlenet.com.cn/token"
    return f"https://{region}.battle.net/oauth/token"


def _safe_json(response: httpx.Response) -> dict[str, Any] | None:
    try:
        return response.json()
    except ValueError:
        return None
