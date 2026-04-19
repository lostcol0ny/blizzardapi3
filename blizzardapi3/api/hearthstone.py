"""Hearthstone API — direct endpoint methods.

Hearthstone has no namespace concept; every endpoint is just region +
locale + optional path params. Search endpoints accept arbitrary filter
kwargs (``class_``, ``manaCost``, ``set``, ``rarity``, ``collectible``,
etc.) which are forwarded as query-string params.
"""

from __future__ import annotations

from typing import Any

from ..core.client import BaseClient
from ..core.executor import ApiResponse, RequestExecutor
from ..types import Locale, Region


class HearthstoneAPI:
    """Hearthstone endpoints (cards, card backs, decks, metadata)."""

    def __init__(self, client: BaseClient, executor: RequestExecutor):
        self._client = client
        self._executor = executor

    # ------------------------------------------------------------------
    # Shared helpers — no namespace, just locale
    # ------------------------------------------------------------------

    def _get(
        self, region: Region | str, locale: Locale | str, path: str, **extra: Any
    ) -> ApiResponse:
        r = region.value if isinstance(region, Region) else region
        l = locale.value if isinstance(locale, Locale) else locale
        params: dict[str, Any] = {"locale": l, **extra}
        return self._executor.execute(
            region=r, path=path, params=params, client=self._client.sync_client
        )

    async def _get_async(
        self, region: Region | str, locale: Locale | str, path: str, **extra: Any
    ) -> ApiResponse:
        r = region.value if isinstance(region, Region) else region
        l = locale.value if isinstance(locale, Locale) else locale
        params: dict[str, Any] = {"locale": l, **extra}
        return await self._executor.execute_async(
            region=r, path=path, params=params, client=self._client.async_client
        )

    # ------------------------------------------------------------------
    # Cards
    # ------------------------------------------------------------------

    def search_cards(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        **filters: Any,
    ) -> ApiResponse:
        """Search for Hearthstone cards.

        Blizzard's card search accepts many filters (``class``, ``set``,
        ``manaCost``, ``rarity``, ``collectible``, ``textFilter``,
        ``gameMode``, ``page``, ``pageSize``, ``sort``, etc.). Pass any
        of them as kwargs — they're forwarded as query params.
        """
        return self._get(region, locale, "/hearthstone/cards", **filters)

    async def search_cards_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        **filters: Any,
    ) -> ApiResponse:
        """Async variant of :py:meth:`search_cards`."""
        return await self._get_async(
            region, locale, "/hearthstone/cards", **filters
        )

    def get_card(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        id_or_slug: str | int,
        **filters: Any,
    ) -> ApiResponse:
        """Get a Hearthstone card by ID or slug."""
        return self._get(
            region, locale, f"/hearthstone/cards/{id_or_slug}", **filters
        )

    async def get_card_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        id_or_slug: str | int,
        **filters: Any,
    ) -> ApiResponse:
        """Get a Hearthstone card by ID or slug."""
        return await self._get_async(
            region, locale, f"/hearthstone/cards/{id_or_slug}", **filters
        )

    # ------------------------------------------------------------------
    # Card backs
    # ------------------------------------------------------------------

    def search_card_backs(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        **filters: Any,
    ) -> ApiResponse:
        """Search for Hearthstone card backs (``cardBackCategory``,
        ``textFilter``, ``sort``, ``order``, ``page``, ``pageSize`` are
        all valid kwargs)."""
        return self._get(region, locale, "/hearthstone/cardbacks", **filters)

    async def search_card_backs_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        **filters: Any,
    ) -> ApiResponse:
        """Async variant of :py:meth:`search_card_backs`."""
        return await self._get_async(
            region, locale, "/hearthstone/cardbacks", **filters
        )

    def get_card_back(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        id_or_slug: str | int,
    ) -> ApiResponse:
        """Get a Hearthstone card back by ID or slug."""
        return self._get(region, locale, f"/hearthstone/cardbacks/{id_or_slug}")

    async def get_card_back_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        id_or_slug: str | int,
    ) -> ApiResponse:
        """Get a Hearthstone card back by ID or slug."""
        return await self._get_async(
            region, locale, f"/hearthstone/cardbacks/{id_or_slug}"
        )

    # ------------------------------------------------------------------
    # Decks
    # ------------------------------------------------------------------

    def get_deck(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        deck_code: str,
    ) -> ApiResponse:
        """Get a Hearthstone deck by full deck code (path form)."""
        return self._get(region, locale, f"/hearthstone/deck/{deck_code}")

    async def get_deck_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        deck_code: str,
    ) -> ApiResponse:
        """Get a Hearthstone deck by full deck code (path form)."""
        return await self._get_async(
            region, locale, f"/hearthstone/deck/{deck_code}"
        )

    def get_deck_by_code(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        code: str,
    ) -> ApiResponse:
        """Get a Hearthstone deck via the ``?code=`` query form.

        Equivalent to :py:meth:`get_deck`, but uses the newer
        query-parameter style the Blizzard docs now recommend.
        """
        return self._get(region, locale, "/hearthstone/deck", code=code)

    async def get_deck_by_code_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        code: str,
    ) -> ApiResponse:
        """Get a Hearthstone deck via the ``?code=`` query form."""
        return await self._get_async(
            region, locale, "/hearthstone/deck", code=code
        )

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    def get_metadata(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get Hearthstone metadata (all types)."""
        return self._get(region, locale, "/hearthstone/metadata")

    async def get_metadata_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get Hearthstone metadata (all types)."""
        return await self._get_async(region, locale, "/hearthstone/metadata")

    def get_metadata_type(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        metadata_type: str,
    ) -> ApiResponse:
        """Get Hearthstone metadata by type (``sets``, ``setGroups``,
        ``types``, ``rarities``, ``classes``, etc.)."""
        return self._get(
            region, locale, f"/hearthstone/metadata/{metadata_type}"
        )

    async def get_metadata_type_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        metadata_type: str,
    ) -> ApiResponse:
        """Get Hearthstone metadata by type."""
        return await self._get_async(
            region, locale, f"/hearthstone/metadata/{metadata_type}"
        )
