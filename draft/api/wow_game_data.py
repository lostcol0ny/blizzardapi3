"""World of Warcraft Game Data API — direct endpoint methods.

This file shows what a real endpoint module looks like after dumping the
YAML + factory. Each endpoint is a plain Python method with typed keyword
arguments, so IDEs resolve everything natively.

This draft includes a representative slice (~25 of 122 endpoints in the
real wow_game_data). The remaining endpoints follow the same four shapes:
  - `_static_get`        — static namespace, e.g. achievements, items
  - `_dynamic_get`       — dynamic namespace, e.g. auctions, realms, pvp
  - `search_*`           — search endpoints with **filters kwargs
  - custom path helpers  — endpoints with multi-part paths (item subclass, etc.)

Classic is intentionally out of scope here — see ``wow_classic.py``.
"""

from __future__ import annotations

from typing import Any

from draft.core.client import BaseClient
from draft.core.executor import ApiResponse, RequestExecutor
from blizzardapi3.types import Locale, Region


class WowGameData:
    """WoW Game Data endpoints (retail).

    Each endpoint comes in paired `name` / `name_async` variants. Use the
    synchronous form inside a `with BlizzardAPI(...)` block, and the async
    form inside an `async with BlizzardAPI(...)` block.
    """

    def __init__(self, client: BaseClient, executor: RequestExecutor):
        self._client = client
        self._executor = executor

    # ------------------------------------------------------------------
    # Shared helpers — four of these cover every endpoint in the module.
    # Endpoint methods stay to 1-2 lines of body.
    # ------------------------------------------------------------------

    def _static_get(
        self, region: Region | str, locale: Locale | str, path: str, **extra: Any
    ) -> ApiResponse:
        r, params = _normalize(region, locale, namespace_type="static", extra=extra)
        return self._executor.execute(region=r, path=path, params=params, client=self._client.sync_client)

    async def _static_get_async(
        self, region: Region | str, locale: Locale | str, path: str, **extra: Any
    ) -> ApiResponse:
        r, params = _normalize(region, locale, namespace_type="static", extra=extra)
        return await self._executor.execute_async(
            region=r, path=path, params=params, client=self._client.async_client
        )

    def _dynamic_get(
        self, region: Region | str, locale: Locale | str, path: str, **extra: Any
    ) -> ApiResponse:
        r, params = _normalize(region, locale, namespace_type="dynamic", extra=extra)
        return self._executor.execute(region=r, path=path, params=params, client=self._client.sync_client)

    async def _dynamic_get_async(
        self, region: Region | str, locale: Locale | str, path: str, **extra: Any
    ) -> ApiResponse:
        r, params = _normalize(region, locale, namespace_type="dynamic", extra=extra)
        return await self._executor.execute_async(
            region=r, path=path, params=params, client=self._client.async_client
        )

    # ------------------------------------------------------------------
    # Achievement
    # ------------------------------------------------------------------

    def get_achievements_index(self, *, region: Region | str, locale: Locale | str) -> ApiResponse:
        """Get an index of achievements."""
        return self._static_get(region, locale, "/data/wow/achievement/index")

    async def get_achievements_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of achievements."""
        return await self._static_get_async(region, locale, "/data/wow/achievement/index")

    def get_achievement(
        self, *, region: Region | str, locale: Locale | str, achievement_id: int
    ) -> ApiResponse:
        """Get an achievement by ID."""
        return self._static_get(region, locale, f"/data/wow/achievement/{achievement_id}")

    async def get_achievement_async(
        self, *, region: Region | str, locale: Locale | str, achievement_id: int
    ) -> ApiResponse:
        """Get an achievement by ID."""
        return await self._static_get_async(region, locale, f"/data/wow/achievement/{achievement_id}")

    def get_achievement_media(
        self, *, region: Region | str, locale: Locale | str, achievement_id: int
    ) -> ApiResponse:
        """Get media for an achievement."""
        return self._static_get(region, locale, f"/data/wow/media/achievement/{achievement_id}")

    async def get_achievement_media_async(
        self, *, region: Region | str, locale: Locale | str, achievement_id: int
    ) -> ApiResponse:
        """Get media for an achievement."""
        return await self._static_get_async(region, locale, f"/data/wow/media/achievement/{achievement_id}")

    # ------------------------------------------------------------------
    # Item  (exercises static namespace + multi-param paths + search)
    # ------------------------------------------------------------------

    def get_item(self, *, region: Region | str, locale: Locale | str, item_id: int) -> ApiResponse:
        """Get an item by ID."""
        return self._static_get(region, locale, f"/data/wow/item/{item_id}")

    async def get_item_async(self, *, region: Region | str, locale: Locale | str, item_id: int) -> ApiResponse:
        """Get an item by ID."""
        return await self._static_get_async(region, locale, f"/data/wow/item/{item_id}")

    def get_item_subclass(
        self, *, region: Region | str, locale: Locale | str, class_id: int, subclass_id: int
    ) -> ApiResponse:
        """Get an item subclass."""
        return self._static_get(
            region, locale, f"/data/wow/item-class/{class_id}/item-subclass/{subclass_id}"
        )

    async def get_item_subclass_async(
        self, *, region: Region | str, locale: Locale | str, class_id: int, subclass_id: int
    ) -> ApiResponse:
        """Get an item subclass."""
        return await self._static_get_async(
            region, locale, f"/data/wow/item-class/{class_id}/item-subclass/{subclass_id}"
        )

    def search_item(self, *, region: Region | str, locale: Locale | str, **filters: Any) -> ApiResponse:
        """Search for items. Accepts `name.{locale}`, `orderby`, `_page`, etc."""
        return self._static_get(region, locale, "/data/wow/search/item", **filters)

    async def search_item_async(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for items."""
        return await self._static_get_async(region, locale, "/data/wow/search/item", **filters)

    # ------------------------------------------------------------------
    # Auctions  (exercises dynamic namespace + path parameter)
    # ------------------------------------------------------------------

    def get_auctions(
        self, *, region: Region | str, locale: Locale | str, connected_realm_id: int
    ) -> ApiResponse:
        """Get auction house data for a connected realm."""
        return self._dynamic_get(
            region, locale, f"/data/wow/connected-realm/{connected_realm_id}/auctions"
        )

    async def get_auctions_async(
        self, *, region: Region | str, locale: Locale | str, connected_realm_id: int
    ) -> ApiResponse:
        """Get auction house data for a connected realm."""
        return await self._dynamic_get_async(
            region, locale, f"/data/wow/connected-realm/{connected_realm_id}/auctions"
        )

    def get_commodities(self, *, region: Region | str, locale: Locale | str) -> ApiResponse:
        """Get commodity auction data."""
        return self._dynamic_get(region, locale, "/data/wow/auctions/commodities")

    async def get_commodities_async(self, *, region: Region | str, locale: Locale | str) -> ApiResponse:
        """Get commodity auction data."""
        return await self._dynamic_get_async(region, locale, "/data/wow/auctions/commodities")

    # ------------------------------------------------------------------
    # Realm  (exercises slug normalization)
    # ------------------------------------------------------------------

    def get_realm(self, *, region: Region | str, locale: Locale | str, realm_slug: str) -> ApiResponse:
        """Get a realm by slug."""
        return self._dynamic_get(region, locale, f"/data/wow/realm/{realm_slug.lower()}")

    async def get_realm_async(
        self, *, region: Region | str, locale: Locale | str, realm_slug: str
    ) -> ApiResponse:
        """Get a realm by slug."""
        return await self._dynamic_get_async(region, locale, f"/data/wow/realm/{realm_slug.lower()}")

    # ------------------------------------------------------------------
    # Item Appearance  (new in Midnight alpha — set/slot/appearance hierarchy)
    # ------------------------------------------------------------------

    def get_item_appearance(
        self, *, region: Region | str, locale: Locale | str, appearance_id: int
    ) -> ApiResponse:
        """Get an item appearance by ID."""
        return self._static_get(region, locale, f"/data/wow/item-appearance/{appearance_id}")

    async def get_item_appearance_async(
        self, *, region: Region | str, locale: Locale | str, appearance_id: int
    ) -> ApiResponse:
        """Get an item appearance by ID."""
        return await self._static_get_async(region, locale, f"/data/wow/item-appearance/{appearance_id}")

    def get_item_appearance_set(
        self, *, region: Region | str, locale: Locale | str, appearance_set_id: int
    ) -> ApiResponse:
        """Get an item appearance set by ID."""
        return self._static_get(
            region, locale, f"/data/wow/item-appearance/set/{appearance_set_id}"
        )

    async def get_item_appearance_set_async(
        self, *, region: Region | str, locale: Locale | str, appearance_set_id: int
    ) -> ApiResponse:
        """Get an item appearance set by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/item-appearance/set/{appearance_set_id}"
        )

    # ------------------------------------------------------------------
    # Neighborhood Map  (new in Midnight alpha — housing world data)
    # ------------------------------------------------------------------

    def get_neighborhood_map_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of neighborhood maps."""
        return self._static_get(region, locale, "/data/wow/neighborhood-map/index")

    async def get_neighborhood_map_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of neighborhood maps."""
        return await self._static_get_async(region, locale, "/data/wow/neighborhood-map/index")

    def get_neighborhood_map(
        self, *, region: Region | str, locale: Locale | str, neighborhood_map_id: int
    ) -> ApiResponse:
        """Get a neighborhood map by ID."""
        return self._static_get(
            region, locale, f"/data/wow/neighborhood-map/{neighborhood_map_id}"
        )

    async def get_neighborhood_map_async(
        self, *, region: Region | str, locale: Locale | str, neighborhood_map_id: int
    ) -> ApiResponse:
        """Get a neighborhood map by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/neighborhood-map/{neighborhood_map_id}"
        )


# ----------------------------------------------------------------------
# Module-level helpers — pure functions, tested independently.
# ----------------------------------------------------------------------


def _normalize(
    region: Region | str,
    locale: Locale | str,
    *,
    namespace_type: str,
    extra: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    """Normalize region/locale to strings and build the query-param dict."""
    r = region.value if isinstance(region, Region) else region
    l = locale.value if isinstance(locale, Locale) else locale
    return r, {"namespace": f"{namespace_type}-{r}", "locale": l, **extra}
