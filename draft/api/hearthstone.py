"""Hearthstone API — direct endpoint methods.

Hearthstone has no namespace concept — every call is just region + locale +
an optional bag of filters. No static/dynamic/profile distinction.

This draft shows the full endpoint surface (8 methods across 4 pair-sets)
because Hearthstone is small enough to demonstrate end-to-end.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from draft.core.client import BaseClient
from draft.core.executor import ApiResponse, RequestExecutor
from blizzardapi3.types import Locale, Region


class Hearthstone:
    """Hearthstone Game Data endpoints."""

    def __init__(self, client: BaseClient, executor: RequestExecutor):
        self._client = client
        self._executor = executor

    def _get(
        self, region: Region | str, locale: Locale | str, path: str, **extra: Any
    ) -> ApiResponse:
        r = region.value if isinstance(region, Region) else region
        l = locale.value if isinstance(locale, Locale) else locale
        params = {"locale": l, **extra}
        return self._executor.execute(region=r, path=path, params=params, client=self._client.sync_client)

    async def _get_async(
        self, region: Region | str, locale: Locale | str, path: str, **extra: Any
    ) -> ApiResponse:
        r = region.value if isinstance(region, Region) else region
        l = locale.value if isinstance(locale, Locale) else locale
        params = {"locale": l, **extra}
        return await self._executor.execute_async(
            region=r, path=path, params=params, client=self._client.async_client
        )

    # ------------------------------------------------------------------
    # Cards
    # ------------------------------------------------------------------

    def search_cards(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search Hearthstone cards. Pass filters like ``set=``, ``class=``, etc."""
        return self._get(region, locale, "/hearthstone/cards", **filters)

    async def search_cards_async(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search Hearthstone cards."""
        return await self._get_async(region, locale, "/hearthstone/cards", **filters)

    def get_card(
        self, *, region: Region | str, locale: Locale | str, id_or_slug: str | int
    ) -> ApiResponse:
        """Get a card by ID or slug."""
        return self._get(region, locale, f"/hearthstone/cards/{id_or_slug}")

    async def get_card_async(
        self, *, region: Region | str, locale: Locale | str, id_or_slug: str | int
    ) -> ApiResponse:
        """Get a card by ID or slug."""
        return await self._get_async(region, locale, f"/hearthstone/cards/{id_or_slug}")

    # ------------------------------------------------------------------
    # Card Backs
    # ------------------------------------------------------------------

    def search_card_backs(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search Hearthstone card backs."""
        return self._get(region, locale, "/hearthstone/cardbacks", **filters)

    async def search_card_backs_async(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search Hearthstone card backs."""
        return await self._get_async(region, locale, "/hearthstone/cardbacks", **filters)

    def get_card_back(
        self, *, region: Region | str, locale: Locale | str, id_or_slug: str | int
    ) -> ApiResponse:
        """Get a card back by ID or slug."""
        return self._get(region, locale, f"/hearthstone/cardbacks/{id_or_slug}")

    async def get_card_back_async(
        self, *, region: Region | str, locale: Locale | str, id_or_slug: str | int
    ) -> ApiResponse:
        """Get a card back by ID or slug."""
        return await self._get_async(region, locale, f"/hearthstone/cardbacks/{id_or_slug}")

    # ------------------------------------------------------------------
    # Decks
    #
    # Blizzard now recommends the query-parameter form. The deck code may
    # contain ``=`` characters which break the legacy path form; we
    # URL-encode it into the ``code`` query parameter via httpx.
    # ------------------------------------------------------------------

    def get_deck(
        self, *, region: Region | str, locale: Locale | str, deck_code: str
    ) -> ApiResponse:
        """Get a deck by deck code (query-parameter form, recommended)."""
        return self._get(region, locale, "/hearthstone/deck", code=deck_code)

    async def get_deck_async(
        self, *, region: Region | str, locale: Locale | str, deck_code: str
    ) -> ApiResponse:
        """Get a deck by deck code (query-parameter form, recommended)."""
        return await self._get_async(region, locale, "/hearthstone/deck", code=deck_code)

    def get_deck_by_path(
        self, *, region: Region | str, locale: Locale | str, deck_code: str
    ) -> ApiResponse:
        """Get a deck by deck code (legacy path form).

        Retained for backwards compatibility with v3.0.x callers. Prefer
        :meth:`get_deck` — the path form does not URL-decode the deck code
        and will fail on codes containing ``=``.
        """
        return self._get(region, locale, f"/hearthstone/deck/{quote(deck_code, safe='')}")

    async def get_deck_by_path_async(
        self, *, region: Region | str, locale: Locale | str, deck_code: str
    ) -> ApiResponse:
        """Get a deck by deck code (legacy path form)."""
        return await self._get_async(
            region, locale, f"/hearthstone/deck/{quote(deck_code, safe='')}"
        )

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    def get_metadata(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get all Hearthstone metadata."""
        return self._get(region, locale, "/hearthstone/metadata")

    async def get_metadata_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get all Hearthstone metadata."""
        return await self._get_async(region, locale, "/hearthstone/metadata")

    def get_metadata_type(
        self, *, region: Region | str, locale: Locale | str, metadata_type: str
    ) -> ApiResponse:
        """Get metadata for a specific type (``sets``, ``rarities``, etc.)."""
        return self._get(region, locale, f"/hearthstone/metadata/{metadata_type}")

    async def get_metadata_type_async(
        self, *, region: Region | str, locale: Locale | str, metadata_type: str
    ) -> ApiResponse:
        """Get metadata for a specific type."""
        return await self._get_async(region, locale, f"/hearthstone/metadata/{metadata_type}")
