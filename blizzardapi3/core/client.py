"""Base client with httpx session management."""

from __future__ import annotations

from collections.abc import Awaitable
from importlib.metadata import PackageNotFoundError, version
from typing import Any, Self, TypeVar

import httpx

from ..types import Locale, Region, get_default_locale
from .auth import TokenManager
from .batch import gather_limited
from .executor import REQUEST_TIMEOUT

T = TypeVar("T")

try:
    _VERSION = version("blizzardapi3")
except PackageNotFoundError:  # running from a source checkout
    _VERSION = "unknown"

USER_AGENT = f"blizzardapi3/{_VERSION} (+https://github.com/lostcol0ny/blizzardapi3)"

# Every value is spelled out because httpx.Limits does not merge with its own
# defaults — passing keepalive_expiry alone would silently make max_connections
# unlimited. The connection count matches httpx's default; only the expiry is
# tuned, because a cold connection to Blizzard costs ~140 ms of TCP and TLS
# handshake and httpx discards idle ones after 5 s, so anything polling on a
# slower interval than that re-handshakes on every single call.
LIMITS = httpx.Limits(max_connections=100, max_keepalive_connections=20, keepalive_expiry=30.0)


def _client_kwargs() -> dict[str, Any]:
    """Shared configuration, so the sync and async sessions cannot drift apart."""
    return {"limits": LIMITS, "timeout": REQUEST_TIMEOUT, "headers": {"User-Agent": USER_AGENT}}


class BaseClient:
    """Owns the httpx sync/async sessions and the token manager.

    Use as a context manager::

        with BlizzardAPI(client_id, client_secret) as api:
            ...
        async with BlizzardAPI(client_id, client_secret) as api:
            ...
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        region: Region | str = Region.US,
        locale: Locale | str | None = None,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.default_region = Region(region) if isinstance(region, str) else region
        self.default_locale = (
            get_default_locale(self.default_region)
            if locale is None
            else (Locale(locale) if isinstance(locale, str) else locale)
        )

        self.token_manager = TokenManager(client_id, client_secret)
        self._sync_client: httpx.Client | None = None
        self._async_client: httpx.AsyncClient | None = None

    @property
    def sync_client(self) -> httpx.Client:
        if self._sync_client is None or self._sync_client.is_closed:
            self._sync_client = httpx.Client(**_client_kwargs())
        return self._sync_client

    @property
    def async_client(self) -> httpx.AsyncClient:
        if self._async_client is None or self._async_client.is_closed:
            self._async_client = httpx.AsyncClient(**_client_kwargs())
        return self._async_client

    def close(self) -> None:
        if self._sync_client is not None and not self._sync_client.is_closed:
            self._sync_client.close()
        self._sync_client = None

    async def aclose(self) -> None:
        if self._async_client is not None and not self._async_client.is_closed:
            await self._async_client.aclose()
        self._async_client = None

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()

    async def gather(self, *awaitables: Awaitable[T], max_concurrency: int = 10) -> list[T]:
        """Run many async calls concurrently, bounded by ``max_concurrency``.

        Convenience wrapper around :func:`~blizzardapi3.core.batch.gather_limited`
        for bulk pulls::

            async with BlizzardAPI(cid, secret) as api:
                realms = await api.gather(
                    *(api.wow.game_data.get_connected_realm_async(
                        region="us", locale="en_US", connected_realm_id=rid)
                      for rid in ids),
                    max_concurrency=10,
                )
        """
        return await gather_limited(*awaitables, max_concurrency=max_concurrency)
