"""World of Warcraft Classic API — direct endpoint methods.

Classic is separated from retail because:
  1. Every Classic endpoint uses a different namespace token
     (``static-classic1x-us``, ``dynamic-classic-eu``, etc.), driven by the
     :class:`ClassicTrack` the caller is querying.
  2. Several Classic-only endpoints don't exist on retail (multi-house
     auctions, the ``pvp-region`` hierarchy).

Usage::

    with BlizzardAPI(client_id, client_secret) as api:
        api.wow.classic.game_data.get_achievement(
            region="us", locale="en_US", achievement_id=1
        )
        # Era / Classic 1x uses the classic_era sub-facade:
        api.wow.classic_era.game_data.get_item(
            region="us", locale="en_US", item_id=19019
        )
"""

from __future__ import annotations

from typing import Any

from ..core.client import BaseClient
from ..core.executor import ApiResponse, RequestExecutor
from ..types import ClassicTrack, Locale, Region


class WowClassicGameData:
    """Classic Game Data endpoints for a specific Classic track."""

    def __init__(
        self,
        client: BaseClient,
        executor: RequestExecutor,
        track: ClassicTrack = ClassicTrack.progression,
    ):
        self._client = client
        self._executor = executor
        self._track = track

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def _static_get(
        self, region: Region | str, locale: Locale | str, path: str, **extra: Any
    ) -> ApiResponse:
        r, params = _normalize(region, locale, "static", self._track, extra)
        return self._executor.execute(
            region=r, path=path, params=params, client=self._client.sync_client
        )

    async def _static_get_async(
        self, region: Region | str, locale: Locale | str, path: str, **extra: Any
    ) -> ApiResponse:
        r, params = _normalize(region, locale, "static", self._track, extra)
        return await self._executor.execute_async(
            region=r, path=path, params=params, client=self._client.async_client
        )

    def _dynamic_get(
        self, region: Region | str, locale: Locale | str, path: str, **extra: Any
    ) -> ApiResponse:
        r, params = _normalize(region, locale, "dynamic", self._track, extra)
        return self._executor.execute(
            region=r, path=path, params=params, client=self._client.sync_client
        )

    async def _dynamic_get_async(
        self, region: Region | str, locale: Locale | str, path: str, **extra: Any
    ) -> ApiResponse:
        r, params = _normalize(region, locale, "dynamic", self._track, extra)
        return await self._executor.execute_async(
            region=r, path=path, params=params, client=self._client.async_client
        )

    # ------------------------------------------------------------------
    # Achievement
    # ------------------------------------------------------------------

    def get_achievement_categories_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of Classic achievement categories."""
        return self._static_get(region, locale, "/data/wow/achievement-category/index")

    async def get_achievement_categories_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of Classic achievement categories."""
        return await self._static_get_async(region, locale, "/data/wow/achievement-category/index")

    def get_achievement_category(
        self, *, region: Region | str, locale: Locale | str, category_id: int
    ) -> ApiResponse:
        """Get a Classic achievement category by ID."""
        return self._static_get(
            region, locale, f"/data/wow/achievement-category/{category_id}"
        )

    async def get_achievement_category_async(
        self, *, region: Region | str, locale: Locale | str, category_id: int
    ) -> ApiResponse:
        """Get a Classic achievement category by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/achievement-category/{category_id}"
        )

    def get_achievements_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of Classic achievements."""
        return self._static_get(region, locale, "/data/wow/achievement/index")

    async def get_achievements_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of Classic achievements."""
        return await self._static_get_async(region, locale, "/data/wow/achievement/index")

    def get_achievement(
        self, *, region: Region | str, locale: Locale | str, achievement_id: int
    ) -> ApiResponse:
        """Get a Classic achievement by ID."""
        return self._static_get(region, locale, f"/data/wow/achievement/{achievement_id}")

    async def get_achievement_async(
        self, *, region: Region | str, locale: Locale | str, achievement_id: int
    ) -> ApiResponse:
        """Get a Classic achievement by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/achievement/{achievement_id}"
        )

    def get_achievement_media(
        self, *, region: Region | str, locale: Locale | str, achievement_id: int
    ) -> ApiResponse:
        """Get media for a Classic achievement."""
        return self._static_get(region, locale, f"/data/wow/media/achievement/{achievement_id}")

    async def get_achievement_media_async(
        self, *, region: Region | str, locale: Locale | str, achievement_id: int
    ) -> ApiResponse:
        """Get media for a Classic achievement."""
        return await self._static_get_async(
            region, locale, f"/data/wow/media/achievement/{achievement_id}"
        )

    # ------------------------------------------------------------------
    # Item / Item Class / Item Subclass / Media
    # ------------------------------------------------------------------

    def get_item_classes_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of Classic item classes."""
        return self._static_get(region, locale, "/data/wow/item-class/index")

    async def get_item_classes_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of Classic item classes."""
        return await self._static_get_async(region, locale, "/data/wow/item-class/index")

    def get_item_class(
        self, *, region: Region | str, locale: Locale | str, class_id: int
    ) -> ApiResponse:
        """Get a Classic item class by ID."""
        return self._static_get(region, locale, f"/data/wow/item-class/{class_id}")

    async def get_item_class_async(
        self, *, region: Region | str, locale: Locale | str, class_id: int
    ) -> ApiResponse:
        """Get a Classic item class by ID."""
        return await self._static_get_async(region, locale, f"/data/wow/item-class/{class_id}")

    def get_item_subclass(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        class_id: int,
        subclass_id: int,
    ) -> ApiResponse:
        """Get a Classic item subclass."""
        return self._static_get(
            region,
            locale,
            f"/data/wow/item-class/{class_id}/item-subclass/{subclass_id}",
        )

    async def get_item_subclass_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        class_id: int,
        subclass_id: int,
    ) -> ApiResponse:
        """Get a Classic item subclass."""
        return await self._static_get_async(
            region,
            locale,
            f"/data/wow/item-class/{class_id}/item-subclass/{subclass_id}",
        )

    def get_item(
        self, *, region: Region | str, locale: Locale | str, item_id: int
    ) -> ApiResponse:
        """Get a Classic item by ID."""
        return self._static_get(region, locale, f"/data/wow/item/{item_id}")

    async def get_item_async(
        self, *, region: Region | str, locale: Locale | str, item_id: int
    ) -> ApiResponse:
        """Get a Classic item by ID."""
        return await self._static_get_async(region, locale, f"/data/wow/item/{item_id}")

    def get_item_media(
        self, *, region: Region | str, locale: Locale | str, item_id: int
    ) -> ApiResponse:
        """Get media for a Classic item."""
        return self._static_get(region, locale, f"/data/wow/media/item/{item_id}")

    async def get_item_media_async(
        self, *, region: Region | str, locale: Locale | str, item_id: int
    ) -> ApiResponse:
        """Get media for a Classic item."""
        return await self._static_get_async(region, locale, f"/data/wow/media/item/{item_id}")

    def search_item(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for Classic items."""
        return self._static_get(region, locale, "/data/wow/search/item", **filters)

    async def search_item_async(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for Classic items."""
        return await self._static_get_async(region, locale, "/data/wow/search/item", **filters)

    # ------------------------------------------------------------------
    # Media search
    # ------------------------------------------------------------------

    def search_media(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for Classic media."""
        return self._static_get(region, locale, "/data/wow/search/media", **filters)

    async def search_media_async(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for Classic media."""
        return await self._static_get_async(region, locale, "/data/wow/search/media", **filters)

    # ------------------------------------------------------------------
    # Playable Class / Race / Creature / Guild Crest
    # ------------------------------------------------------------------

    def get_playable_classes_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of Classic playable classes."""
        return self._static_get(region, locale, "/data/wow/playable-class/index")

    async def get_playable_classes_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of Classic playable classes."""
        return await self._static_get_async(region, locale, "/data/wow/playable-class/index")

    def get_playable_class(
        self, *, region: Region | str, locale: Locale | str, class_id: int
    ) -> ApiResponse:
        """Get a Classic playable class by ID."""
        return self._static_get(region, locale, f"/data/wow/playable-class/{class_id}")

    async def get_playable_class_async(
        self, *, region: Region | str, locale: Locale | str, class_id: int
    ) -> ApiResponse:
        """Get a Classic playable class by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/playable-class/{class_id}"
        )

    def get_playable_races_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of Classic playable races."""
        return self._static_get(region, locale, "/data/wow/playable-race/index")

    async def get_playable_races_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of Classic playable races."""
        return await self._static_get_async(region, locale, "/data/wow/playable-race/index")

    def get_playable_race(
        self, *, region: Region | str, locale: Locale | str, race_id: int
    ) -> ApiResponse:
        """Get a Classic playable race by ID."""
        return self._static_get(region, locale, f"/data/wow/playable-race/{race_id}")

    async def get_playable_race_async(
        self, *, region: Region | str, locale: Locale | str, race_id: int
    ) -> ApiResponse:
        """Get a Classic playable race by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/playable-race/{race_id}"
        )

    def get_creature_families_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of Classic creature families."""
        return self._static_get(region, locale, "/data/wow/creature-family/index")

    async def get_creature_families_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of Classic creature families."""
        return await self._static_get_async(region, locale, "/data/wow/creature-family/index")

    def get_creature_family(
        self, *, region: Region | str, locale: Locale | str, creature_family_id: int
    ) -> ApiResponse:
        """Get a Classic creature family by ID."""
        return self._static_get(
            region, locale, f"/data/wow/creature-family/{creature_family_id}"
        )

    async def get_creature_family_async(
        self, *, region: Region | str, locale: Locale | str, creature_family_id: int
    ) -> ApiResponse:
        """Get a Classic creature family by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/creature-family/{creature_family_id}"
        )

    def get_creature_types_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of Classic creature types."""
        return self._static_get(region, locale, "/data/wow/creature-type/index")

    async def get_creature_types_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of Classic creature types."""
        return await self._static_get_async(region, locale, "/data/wow/creature-type/index")

    def get_creature_type(
        self, *, region: Region | str, locale: Locale | str, creature_type_id: int
    ) -> ApiResponse:
        """Get a Classic creature type by ID."""
        return self._static_get(
            region, locale, f"/data/wow/creature-type/{creature_type_id}"
        )

    async def get_creature_type_async(
        self, *, region: Region | str, locale: Locale | str, creature_type_id: int
    ) -> ApiResponse:
        """Get a Classic creature type by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/creature-type/{creature_type_id}"
        )

    def get_creature(
        self, *, region: Region | str, locale: Locale | str, creature_id: int
    ) -> ApiResponse:
        """Get a Classic creature by ID."""
        return self._static_get(region, locale, f"/data/wow/creature/{creature_id}")

    async def get_creature_async(
        self, *, region: Region | str, locale: Locale | str, creature_id: int
    ) -> ApiResponse:
        """Get a Classic creature by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/creature/{creature_id}"
        )

    def search_creature(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for Classic creatures."""
        return self._static_get(region, locale, "/data/wow/search/creature", **filters)

    async def search_creature_async(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for Classic creatures."""
        return await self._static_get_async(
            region, locale, "/data/wow/search/creature", **filters
        )

    def get_creature_display_media(
        self, *, region: Region | str, locale: Locale | str, creature_display_id: int
    ) -> ApiResponse:
        """Get display media for a Classic creature."""
        return self._static_get(
            region, locale, f"/data/wow/media/creature-display/{creature_display_id}"
        )

    async def get_creature_display_media_async(
        self, *, region: Region | str, locale: Locale | str, creature_display_id: int
    ) -> ApiResponse:
        """Get display media for a Classic creature."""
        return await self._static_get_async(
            region, locale, f"/data/wow/media/creature-display/{creature_display_id}"
        )

    def get_creature_family_media(
        self, *, region: Region | str, locale: Locale | str, creature_family_id: int
    ) -> ApiResponse:
        """Get media for a Classic creature family."""
        return self._static_get(
            region, locale, f"/data/wow/media/creature-family/{creature_family_id}"
        )

    async def get_creature_family_media_async(
        self, *, region: Region | str, locale: Locale | str, creature_family_id: int
    ) -> ApiResponse:
        """Get media for a Classic creature family."""
        return await self._static_get_async(
            region, locale, f"/data/wow/media/creature-family/{creature_family_id}"
        )

    def get_guild_crest_components_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of Classic guild crest components."""
        return self._static_get(region, locale, "/data/wow/guild-crest/index")

    async def get_guild_crest_components_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of Classic guild crest components."""
        return await self._static_get_async(region, locale, "/data/wow/guild-crest/index")

    def get_guild_crest_border_media(
        self, *, region: Region | str, locale: Locale | str, border_id: int
    ) -> ApiResponse:
        """Get media for a Classic guild crest border."""
        return self._static_get(
            region, locale, f"/data/wow/media/guild-crest/border/{border_id}"
        )

    async def get_guild_crest_border_media_async(
        self, *, region: Region | str, locale: Locale | str, border_id: int
    ) -> ApiResponse:
        """Get media for a Classic guild crest border."""
        return await self._static_get_async(
            region, locale, f"/data/wow/media/guild-crest/border/{border_id}"
        )

    def get_guild_crest_emblem_media(
        self, *, region: Region | str, locale: Locale | str, emblem_id: int
    ) -> ApiResponse:
        """Get media for a Classic guild crest emblem."""
        return self._static_get(
            region, locale, f"/data/wow/media/guild-crest/emblem/{emblem_id}"
        )

    async def get_guild_crest_emblem_media_async(
        self, *, region: Region | str, locale: Locale | str, emblem_id: int
    ) -> ApiResponse:
        """Get media for a Classic guild crest emblem."""
        return await self._static_get_async(
            region, locale, f"/data/wow/media/guild-crest/emblem/{emblem_id}"
        )

    # ------------------------------------------------------------------
    # Power Type / Playable Specialization / Region
    # ------------------------------------------------------------------

    def get_power_types_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of Classic power types."""
        return self._static_get(region, locale, "/data/wow/power-type/index")

    async def get_power_types_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of Classic power types."""
        return await self._static_get_async(region, locale, "/data/wow/power-type/index")

    def get_power_type(
        self, *, region: Region | str, locale: Locale | str, power_type_id: int
    ) -> ApiResponse:
        """Get a Classic power type by ID."""
        return self._static_get(region, locale, f"/data/wow/power-type/{power_type_id}")

    async def get_power_type_async(
        self, *, region: Region | str, locale: Locale | str, power_type_id: int
    ) -> ApiResponse:
        """Get a Classic power type by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/power-type/{power_type_id}"
        )

    def get_regions_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of Classic regions."""
        return self._dynamic_get(region, locale, "/data/wow/region/index")

    async def get_regions_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of Classic regions."""
        return await self._dynamic_get_async(region, locale, "/data/wow/region/index")

    def get_region(
        self, *, region: Region | str, locale: Locale | str, region_id: int
    ) -> ApiResponse:
        """Get a Classic region by ID."""
        return self._dynamic_get(region, locale, f"/data/wow/region/{region_id}")

    async def get_region_async(
        self, *, region: Region | str, locale: Locale | str, region_id: int
    ) -> ApiResponse:
        """Get a Classic region by ID."""
        return await self._dynamic_get_async(region, locale, f"/data/wow/region/{region_id}")

    # ------------------------------------------------------------------
    # Realm / Connected Realm
    # ------------------------------------------------------------------

    def get_connected_realms_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of Classic connected realms."""
        return self._dynamic_get(region, locale, "/data/wow/connected-realm/index")

    async def get_connected_realms_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of Classic connected realms."""
        return await self._dynamic_get_async(region, locale, "/data/wow/connected-realm/index")

    def get_connected_realm(
        self, *, region: Region | str, locale: Locale | str, connected_realm_id: int
    ) -> ApiResponse:
        """Get a Classic connected realm by ID."""
        return self._dynamic_get(
            region, locale, f"/data/wow/connected-realm/{connected_realm_id}"
        )

    async def get_connected_realm_async(
        self, *, region: Region | str, locale: Locale | str, connected_realm_id: int
    ) -> ApiResponse:
        """Get a Classic connected realm by ID."""
        return await self._dynamic_get_async(
            region, locale, f"/data/wow/connected-realm/{connected_realm_id}"
        )

    def search_connected_realm(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for Classic connected realms."""
        return self._dynamic_get(
            region, locale, "/data/wow/search/connected-realm", **filters
        )

    async def search_connected_realm_async(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for Classic connected realms."""
        return await self._dynamic_get_async(
            region, locale, "/data/wow/search/connected-realm", **filters
        )

    def get_realms_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of Classic realms."""
        return self._dynamic_get(region, locale, "/data/wow/realm/index")

    async def get_realms_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of Classic realms."""
        return await self._dynamic_get_async(region, locale, "/data/wow/realm/index")

    def get_realm(
        self, *, region: Region | str, locale: Locale | str, realm_slug: str
    ) -> ApiResponse:
        """Get a Classic realm by slug."""
        return self._dynamic_get(region, locale, f"/data/wow/realm/{realm_slug.lower()}")

    async def get_realm_async(
        self, *, region: Region | str, locale: Locale | str, realm_slug: str
    ) -> ApiResponse:
        """Get a Classic realm by slug."""
        return await self._dynamic_get_async(
            region, locale, f"/data/wow/realm/{realm_slug.lower()}"
        )

    def search_realm(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for Classic realms."""
        return self._dynamic_get(region, locale, "/data/wow/search/realm", **filters)

    async def search_realm_async(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for Classic realms."""
        return await self._dynamic_get_async(
            region, locale, "/data/wow/search/realm", **filters
        )

    # ------------------------------------------------------------------
    # Auctions — Classic has multi-house hierarchy
    # ------------------------------------------------------------------

    def get_auctions_index(
        self, *, region: Region | str, locale: Locale | str, connected_realm_id: int
    ) -> ApiResponse:
        """Get the index of auction houses for a Classic connected realm."""
        return self._dynamic_get(
            region, locale, f"/data/wow/connected-realm/{connected_realm_id}/auctions/index"
        )

    async def get_auctions_index_async(
        self, *, region: Region | str, locale: Locale | str, connected_realm_id: int
    ) -> ApiResponse:
        """Get the index of auction houses for a Classic connected realm."""
        return await self._dynamic_get_async(
            region, locale, f"/data/wow/connected-realm/{connected_realm_id}/auctions/index"
        )

    def get_auctions(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        connected_realm_id: int,
        auction_house_id: int,
    ) -> ApiResponse:
        """Get a specific Classic auction house's data."""
        return self._dynamic_get(
            region,
            locale,
            f"/data/wow/connected-realm/{connected_realm_id}/auctions/{auction_house_id}",
        )

    async def get_auctions_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        connected_realm_id: int,
        auction_house_id: int,
    ) -> ApiResponse:
        """Get a specific Classic auction house's data."""
        return await self._dynamic_get_async(
            region,
            locale,
            f"/data/wow/connected-realm/{connected_realm_id}/auctions/{auction_house_id}",
        )

    # ------------------------------------------------------------------
    # PvP Region hierarchy (Classic-only) / PvP Season / Leaderboard
    # ------------------------------------------------------------------

    def get_pvp_region_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get the index of Classic PvP regions."""
        return self._dynamic_get(region, locale, "/data/wow/pvp-region/index")

    async def get_pvp_region_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get the index of Classic PvP regions."""
        return await self._dynamic_get_async(region, locale, "/data/wow/pvp-region/index")

    def get_pvp_regional_seasons_index(
        self, *, region: Region | str, locale: Locale | str, pvp_region_id: int
    ) -> ApiResponse:
        """Get the index of PvP seasons for a Classic PvP region."""
        return self._dynamic_get(
            region, locale, f"/data/wow/pvp-region/{pvp_region_id}/pvp-season/index"
        )

    async def get_pvp_regional_seasons_index_async(
        self, *, region: Region | str, locale: Locale | str, pvp_region_id: int
    ) -> ApiResponse:
        """Get the index of PvP seasons for a Classic PvP region."""
        return await self._dynamic_get_async(
            region, locale, f"/data/wow/pvp-region/{pvp_region_id}/pvp-season/index"
        )

    def get_pvp_regional_season(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        pvp_region_id: int,
        pvp_season_id: int,
    ) -> ApiResponse:
        """Get a Classic PvP season in a specific PvP region."""
        return self._dynamic_get(
            region,
            locale,
            f"/data/wow/pvp-region/{pvp_region_id}/pvp-season/{pvp_season_id}",
        )

    async def get_pvp_regional_season_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        pvp_region_id: int,
        pvp_season_id: int,
    ) -> ApiResponse:
        """Get a Classic PvP season in a specific PvP region."""
        return await self._dynamic_get_async(
            region,
            locale,
            f"/data/wow/pvp-region/{pvp_region_id}/pvp-season/{pvp_season_id}",
        )

    def get_pvp_regional_leaderboards_index(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        pvp_region_id: int,
        pvp_season_id: int,
    ) -> ApiResponse:
        """Get the leaderboards index for a Classic regional PvP season."""
        return self._dynamic_get(
            region,
            locale,
            f"/data/wow/pvp-region/{pvp_region_id}/pvp-season/{pvp_season_id}"
            "/pvp-leaderboard/index",
        )

    async def get_pvp_regional_leaderboards_index_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        pvp_region_id: int,
        pvp_season_id: int,
    ) -> ApiResponse:
        """Get the leaderboards index for a Classic regional PvP season."""
        return await self._dynamic_get_async(
            region,
            locale,
            f"/data/wow/pvp-region/{pvp_region_id}/pvp-season/{pvp_season_id}"
            "/pvp-leaderboard/index",
        )

    def get_pvp_regional_leaderboard(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        pvp_region_id: int,
        pvp_season_id: int,
        pvp_bracket: str,
    ) -> ApiResponse:
        """Get a Classic PvP leaderboard for a bracket in a regional season."""
        return self._dynamic_get(
            region,
            locale,
            f"/data/wow/pvp-region/{pvp_region_id}/pvp-season/{pvp_season_id}"
            f"/pvp-leaderboard/{pvp_bracket}",
        )

    async def get_pvp_regional_leaderboard_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        pvp_region_id: int,
        pvp_season_id: int,
        pvp_bracket: str,
    ) -> ApiResponse:
        """Get a Classic PvP leaderboard for a bracket in a regional season."""
        return await self._dynamic_get_async(
            region,
            locale,
            f"/data/wow/pvp-region/{pvp_region_id}/pvp-season/{pvp_season_id}"
            f"/pvp-leaderboard/{pvp_bracket}",
        )

    def get_pvp_regional_rewards_index(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        pvp_region_id: int,
        pvp_season_id: int,
    ) -> ApiResponse:
        """Get the rewards index for a Classic regional PvP season."""
        return self._dynamic_get(
            region,
            locale,
            f"/data/wow/pvp-region/{pvp_region_id}/pvp-season/{pvp_season_id}"
            "/pvp-reward/index",
        )

    async def get_pvp_regional_rewards_index_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        pvp_region_id: int,
        pvp_season_id: int,
    ) -> ApiResponse:
        """Get the rewards index for a Classic regional PvP season."""
        return await self._dynamic_get_async(
            region,
            locale,
            f"/data/wow/pvp-region/{pvp_region_id}/pvp-season/{pvp_season_id}"
            "/pvp-reward/index",
        )


class WowClassicProfile:
    """Classic Profile endpoints for a specific Classic track."""

    def __init__(
        self,
        client: BaseClient,
        executor: RequestExecutor,
        track: ClassicTrack = ClassicTrack.progression,
    ):
        self._client = client
        self._executor = executor
        self._track = track

    def _profile_get(
        self, region: Region | str, locale: Locale | str, path: str, **extra: Any
    ) -> ApiResponse:
        r, params = _normalize(region, locale, "profile", self._track, extra)
        return self._executor.execute(
            region=r, path=path, params=params, client=self._client.sync_client
        )

    async def _profile_get_async(
        self, region: Region | str, locale: Locale | str, path: str, **extra: Any
    ) -> ApiResponse:
        r, params = _normalize(region, locale, "profile", self._track, extra)
        return await self._executor.execute_async(
            region=r, path=path, params=params, client=self._client.async_client
        )

    def get_character_profile_summary(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a Classic character profile summary."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}",
        )

    async def get_character_profile_summary_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a Classic character profile summary."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}",
        )


class WowClassic:
    """Facade for Classic Game Data + Profile on a specific track."""

    def __init__(
        self,
        client: BaseClient,
        executor: RequestExecutor,
        track: ClassicTrack = ClassicTrack.progression,
    ):
        self.game_data = WowClassicGameData(client, executor, track=track)
        self.profile = WowClassicProfile(client, executor, track=track)
        self.track = track


# ----------------------------------------------------------------------
# Module-level helper
# ----------------------------------------------------------------------


def _normalize(
    region: Region | str,
    locale: Locale | str,
    namespace_type: str,
    track: ClassicTrack,
    extra: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    r = region.value if isinstance(region, Region) else region
    l = locale.value if isinstance(locale, Locale) else locale
    return r, {
        "namespace": f"{namespace_type}-{track.value}-{r}",
        "locale": l,
        **extra,
    }
