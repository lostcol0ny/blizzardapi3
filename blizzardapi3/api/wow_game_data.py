"""World of Warcraft Game Data API — direct endpoint methods (retail).

Classic is intentionally out of scope here — see :mod:`.wow_classic`.
"""

from __future__ import annotations

from typing import Any

from ..core.client import BaseClient
from ..core.executor import ApiResponse, RequestExecutor
from ..types import Locale, Region


class WowGameData:
    """WoW Game Data endpoints (retail).

    Each endpoint has a paired ``name`` / ``name_async`` variant. Use the
    sync form inside ``with BlizzardAPI(...)`` and the async form inside
    ``async with BlizzardAPI(...)``.
    """

    def __init__(self, client: BaseClient, executor: RequestExecutor):
        self._client = client
        self._executor = executor

    # ------------------------------------------------------------------
    # Shared helpers — these four cover every endpoint in the module.
    # ------------------------------------------------------------------

    def _static_get(
        self, region: Region | str, locale: Locale | str, path: str, **extra: Any
    ) -> ApiResponse:
        r, params = _normalize(region, locale, namespace_type="static", extra=extra)
        return self._executor.execute(
            region=r, path=path, params=params, client=self._client.sync_client
        )

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
        return self._executor.execute(
            region=r, path=path, params=params, client=self._client.sync_client
        )

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

    def get_achievement_categories_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of achievement categories."""
        return self._static_get(region, locale, "/data/wow/achievement-category/index")

    async def get_achievement_categories_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of achievement categories."""
        return await self._static_get_async(region, locale, "/data/wow/achievement-category/index")

    def get_achievement_category(
        self, *, region: Region | str, locale: Locale | str, category_id: int
    ) -> ApiResponse:
        """Get an achievement category by ID."""
        return self._static_get(
            region, locale, f"/data/wow/achievement-category/{category_id}"
        )

    async def get_achievement_category_async(
        self, *, region: Region | str, locale: Locale | str, category_id: int
    ) -> ApiResponse:
        """Get an achievement category by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/achievement-category/{category_id}"
        )

    def get_achievements_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
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
        return await self._static_get_async(
            region, locale, f"/data/wow/achievement/{achievement_id}"
        )

    def get_achievement_media(
        self, *, region: Region | str, locale: Locale | str, achievement_id: int
    ) -> ApiResponse:
        """Get media for an achievement."""
        return self._static_get(region, locale, f"/data/wow/media/achievement/{achievement_id}")

    async def get_achievement_media_async(
        self, *, region: Region | str, locale: Locale | str, achievement_id: int
    ) -> ApiResponse:
        """Get media for an achievement."""
        return await self._static_get_async(
            region, locale, f"/data/wow/media/achievement/{achievement_id}"
        )

    # ------------------------------------------------------------------
    # Auctions
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

    def get_commodities(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get commodity auction data."""
        return self._dynamic_get(region, locale, "/data/wow/auctions/commodities")

    async def get_commodities_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get commodity auction data."""
        return await self._dynamic_get_async(region, locale, "/data/wow/auctions/commodities")

    # ------------------------------------------------------------------
    # Azerite Essence
    # ------------------------------------------------------------------

    def get_azerite_essences_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of azerite essences."""
        return self._static_get(region, locale, "/data/wow/azerite-essence/index")

    async def get_azerite_essences_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of azerite essences."""
        return await self._static_get_async(region, locale, "/data/wow/azerite-essence/index")

    def get_azerite_essence(
        self, *, region: Region | str, locale: Locale | str, essence_id: int
    ) -> ApiResponse:
        """Get an azerite essence by ID."""
        return self._static_get(region, locale, f"/data/wow/azerite-essence/{essence_id}")

    async def get_azerite_essence_async(
        self, *, region: Region | str, locale: Locale | str, essence_id: int
    ) -> ApiResponse:
        """Get an azerite essence by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/azerite-essence/{essence_id}"
        )

    def search_azerite_essence(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for azerite essences."""
        return self._static_get(region, locale, "/data/wow/search/azerite-essence", **filters)

    async def search_azerite_essence_async(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for azerite essences."""
        return await self._static_get_async(
            region, locale, "/data/wow/search/azerite-essence", **filters
        )

    def get_azerite_essence_media(
        self, *, region: Region | str, locale: Locale | str, essence_id: int
    ) -> ApiResponse:
        """Get media for an azerite essence."""
        return self._static_get(
            region, locale, f"/data/wow/media/azerite-essence/{essence_id}"
        )

    async def get_azerite_essence_media_async(
        self, *, region: Region | str, locale: Locale | str, essence_id: int
    ) -> ApiResponse:
        """Get media for an azerite essence."""
        return await self._static_get_async(
            region, locale, f"/data/wow/media/azerite-essence/{essence_id}"
        )

    # ------------------------------------------------------------------
    # Connected Realm
    # ------------------------------------------------------------------

    def get_connected_realms_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of connected realms."""
        return self._dynamic_get(region, locale, "/data/wow/connected-realm/index")

    async def get_connected_realms_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of connected realms."""
        return await self._dynamic_get_async(region, locale, "/data/wow/connected-realm/index")

    def get_connected_realm(
        self, *, region: Region | str, locale: Locale | str, connected_realm_id: int
    ) -> ApiResponse:
        """Get a connected realm by ID."""
        return self._dynamic_get(
            region, locale, f"/data/wow/connected-realm/{connected_realm_id}"
        )

    async def get_connected_realm_async(
        self, *, region: Region | str, locale: Locale | str, connected_realm_id: int
    ) -> ApiResponse:
        """Get a connected realm by ID."""
        return await self._dynamic_get_async(
            region, locale, f"/data/wow/connected-realm/{connected_realm_id}"
        )

    def search_connected_realm(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for connected realms."""
        return self._dynamic_get(region, locale, "/data/wow/search/connected-realm", **filters)

    async def search_connected_realm_async(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for connected realms."""
        return await self._dynamic_get_async(
            region, locale, "/data/wow/search/connected-realm", **filters
        )

    # ------------------------------------------------------------------
    # Covenant
    # ------------------------------------------------------------------

    def get_covenant_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of covenants."""
        return self._static_get(region, locale, "/data/wow/covenant/index")

    async def get_covenant_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of covenants."""
        return await self._static_get_async(region, locale, "/data/wow/covenant/index")

    def get_covenant(
        self, *, region: Region | str, locale: Locale | str, covenant_id: int
    ) -> ApiResponse:
        """Get a covenant by ID."""
        return self._static_get(region, locale, f"/data/wow/covenant/{covenant_id}")

    async def get_covenant_async(
        self, *, region: Region | str, locale: Locale | str, covenant_id: int
    ) -> ApiResponse:
        """Get a covenant by ID."""
        return await self._static_get_async(region, locale, f"/data/wow/covenant/{covenant_id}")

    def get_covenant_media(
        self, *, region: Region | str, locale: Locale | str, covenant_id: int
    ) -> ApiResponse:
        """Get media for a covenant."""
        return self._static_get(region, locale, f"/data/wow/media/covenant/{covenant_id}")

    async def get_covenant_media_async(
        self, *, region: Region | str, locale: Locale | str, covenant_id: int
    ) -> ApiResponse:
        """Get media for a covenant."""
        return await self._static_get_async(
            region, locale, f"/data/wow/media/covenant/{covenant_id}"
        )

    def get_soulbind_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of soulbinds."""
        return self._static_get(region, locale, "/data/wow/covenant/soulbind/index")

    async def get_soulbind_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of soulbinds."""
        return await self._static_get_async(region, locale, "/data/wow/covenant/soulbind/index")

    def get_soulbind(
        self, *, region: Region | str, locale: Locale | str, soulbind_id: int
    ) -> ApiResponse:
        """Get a soulbind by ID."""
        return self._static_get(region, locale, f"/data/wow/covenant/soulbind/{soulbind_id}")

    async def get_soulbind_async(
        self, *, region: Region | str, locale: Locale | str, soulbind_id: int
    ) -> ApiResponse:
        """Get a soulbind by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/covenant/soulbind/{soulbind_id}"
        )

    def get_conduit_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of conduits."""
        return self._static_get(region, locale, "/data/wow/covenant/conduit/index")

    async def get_conduit_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of conduits."""
        return await self._static_get_async(region, locale, "/data/wow/covenant/conduit/index")

    def get_conduit(
        self, *, region: Region | str, locale: Locale | str, conduit_id: int
    ) -> ApiResponse:
        """Get a conduit by ID."""
        return self._static_get(region, locale, f"/data/wow/covenant/conduit/{conduit_id}")

    async def get_conduit_async(
        self, *, region: Region | str, locale: Locale | str, conduit_id: int
    ) -> ApiResponse:
        """Get a conduit by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/covenant/conduit/{conduit_id}"
        )

    # ------------------------------------------------------------------
    # Creature
    # ------------------------------------------------------------------

    def get_creature_families_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of creature families."""
        return self._static_get(region, locale, "/data/wow/creature-family/index")

    async def get_creature_families_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of creature families."""
        return await self._static_get_async(region, locale, "/data/wow/creature-family/index")

    def get_creature_family(
        self, *, region: Region | str, locale: Locale | str, creature_family_id: int
    ) -> ApiResponse:
        """Get a creature family by ID."""
        return self._static_get(
            region, locale, f"/data/wow/creature-family/{creature_family_id}"
        )

    async def get_creature_family_async(
        self, *, region: Region | str, locale: Locale | str, creature_family_id: int
    ) -> ApiResponse:
        """Get a creature family by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/creature-family/{creature_family_id}"
        )

    def get_creature_family_media(
        self, *, region: Region | str, locale: Locale | str, creature_family_id: int
    ) -> ApiResponse:
        """Get media for a creature family."""
        return self._static_get(
            region, locale, f"/data/wow/media/creature-family/{creature_family_id}"
        )

    async def get_creature_family_media_async(
        self, *, region: Region | str, locale: Locale | str, creature_family_id: int
    ) -> ApiResponse:
        """Get media for a creature family."""
        return await self._static_get_async(
            region, locale, f"/data/wow/media/creature-family/{creature_family_id}"
        )

    def get_creature_types_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of creature types."""
        return self._static_get(region, locale, "/data/wow/creature-type/index")

    async def get_creature_types_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of creature types."""
        return await self._static_get_async(region, locale, "/data/wow/creature-type/index")

    def get_creature_type(
        self, *, region: Region | str, locale: Locale | str, creature_type_id: int
    ) -> ApiResponse:
        """Get a creature type by ID."""
        return self._static_get(
            region, locale, f"/data/wow/creature-type/{creature_type_id}"
        )

    async def get_creature_type_async(
        self, *, region: Region | str, locale: Locale | str, creature_type_id: int
    ) -> ApiResponse:
        """Get a creature type by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/creature-type/{creature_type_id}"
        )

    def get_creature(
        self, *, region: Region | str, locale: Locale | str, creature_id: int
    ) -> ApiResponse:
        """Get a creature by ID."""
        return self._static_get(region, locale, f"/data/wow/creature/{creature_id}")

    async def get_creature_async(
        self, *, region: Region | str, locale: Locale | str, creature_id: int
    ) -> ApiResponse:
        """Get a creature by ID."""
        return await self._static_get_async(region, locale, f"/data/wow/creature/{creature_id}")

    def search_creature(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for creatures."""
        return self._static_get(region, locale, "/data/wow/search/creature", **filters)

    async def search_creature_async(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for creatures."""
        return await self._static_get_async(
            region, locale, "/data/wow/search/creature", **filters
        )

    def get_creature_display_media(
        self, *, region: Region | str, locale: Locale | str, creature_display_id: int
    ) -> ApiResponse:
        """Get display media for a creature."""
        return self._static_get(
            region, locale, f"/data/wow/media/creature-display/{creature_display_id}"
        )

    async def get_creature_display_media_async(
        self, *, region: Region | str, locale: Locale | str, creature_display_id: int
    ) -> ApiResponse:
        """Get display media for a creature."""
        return await self._static_get_async(
            region, locale, f"/data/wow/media/creature-display/{creature_display_id}"
        )

    # ------------------------------------------------------------------
    # Guild Crest
    # ------------------------------------------------------------------

    def get_guild_crest_components_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of guild crest components."""
        return self._static_get(region, locale, "/data/wow/guild-crest/index")

    async def get_guild_crest_components_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of guild crest components."""
        return await self._static_get_async(region, locale, "/data/wow/guild-crest/index")

    def get_guild_crest_border_media(
        self, *, region: Region | str, locale: Locale | str, border_id: int
    ) -> ApiResponse:
        """Get media for a guild crest border."""
        return self._static_get(
            region, locale, f"/data/wow/media/guild-crest/border/{border_id}"
        )

    async def get_guild_crest_border_media_async(
        self, *, region: Region | str, locale: Locale | str, border_id: int
    ) -> ApiResponse:
        """Get media for a guild crest border."""
        return await self._static_get_async(
            region, locale, f"/data/wow/media/guild-crest/border/{border_id}"
        )

    def get_guild_crest_emblem_media(
        self, *, region: Region | str, locale: Locale | str, emblem_id: int
    ) -> ApiResponse:
        """Get media for a guild crest emblem."""
        return self._static_get(
            region, locale, f"/data/wow/media/guild-crest/emblem/{emblem_id}"
        )

    async def get_guild_crest_emblem_media_async(
        self, *, region: Region | str, locale: Locale | str, emblem_id: int
    ) -> ApiResponse:
        """Get media for a guild crest emblem."""
        return await self._static_get_async(
            region, locale, f"/data/wow/media/guild-crest/emblem/{emblem_id}"
        )

    # ------------------------------------------------------------------
    # Heirloom
    # ------------------------------------------------------------------

    def get_heirloom_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of heirlooms."""
        return self._static_get(region, locale, "/data/wow/heirloom/index")

    async def get_heirloom_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of heirlooms."""
        return await self._static_get_async(region, locale, "/data/wow/heirloom/index")

    def get_heirloom(
        self, *, region: Region | str, locale: Locale | str, heirloom_id: int
    ) -> ApiResponse:
        """Get an heirloom by ID."""
        return self._static_get(region, locale, f"/data/wow/heirloom/{heirloom_id}")

    async def get_heirloom_async(
        self, *, region: Region | str, locale: Locale | str, heirloom_id: int
    ) -> ApiResponse:
        """Get an heirloom by ID."""
        return await self._static_get_async(region, locale, f"/data/wow/heirloom/{heirloom_id}")

    # ------------------------------------------------------------------
    # Housing (Decor / Fixture / Fixture Hook / Room) — new in Midnight
    # ------------------------------------------------------------------

    def get_decor_index(self, *, region: Region | str, locale: Locale | str) -> ApiResponse:
        """Get an index of decor items."""
        return self._static_get(region, locale, "/data/wow/decor/index")

    async def get_decor_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of decor items."""
        return await self._static_get_async(region, locale, "/data/wow/decor/index")

    def get_decor(
        self, *, region: Region | str, locale: Locale | str, decor_id: int
    ) -> ApiResponse:
        """Get a decor item by ID."""
        return self._static_get(region, locale, f"/data/wow/decor/{decor_id}")

    async def get_decor_async(
        self, *, region: Region | str, locale: Locale | str, decor_id: int
    ) -> ApiResponse:
        """Get a decor item by ID."""
        return await self._static_get_async(region, locale, f"/data/wow/decor/{decor_id}")

    def search_decor(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for decor items."""
        return self._static_get(region, locale, "/data/wow/search/decor", **filters)

    async def search_decor_async(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for decor items."""
        return await self._static_get_async(region, locale, "/data/wow/search/decor", **filters)

    def get_fixture_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of fixtures."""
        return self._static_get(region, locale, "/data/wow/fixture/index")

    async def get_fixture_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of fixtures."""
        return await self._static_get_async(region, locale, "/data/wow/fixture/index")

    def get_fixture(
        self, *, region: Region | str, locale: Locale | str, fixture_id: int
    ) -> ApiResponse:
        """Get a fixture by ID."""
        return self._static_get(region, locale, f"/data/wow/fixture/{fixture_id}")

    async def get_fixture_async(
        self, *, region: Region | str, locale: Locale | str, fixture_id: int
    ) -> ApiResponse:
        """Get a fixture by ID."""
        return await self._static_get_async(region, locale, f"/data/wow/fixture/{fixture_id}")

    def search_fixture(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for fixtures."""
        return self._static_get(region, locale, "/data/wow/search/fixture", **filters)

    async def search_fixture_async(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for fixtures."""
        return await self._static_get_async(
            region, locale, "/data/wow/search/fixture", **filters
        )

    def get_fixture_hook_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of fixture hooks."""
        return self._static_get(region, locale, "/data/wow/fixture-hook/index")

    async def get_fixture_hook_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of fixture hooks."""
        return await self._static_get_async(region, locale, "/data/wow/fixture-hook/index")

    def get_fixture_hook(
        self, *, region: Region | str, locale: Locale | str, fixture_hook_id: int
    ) -> ApiResponse:
        """Get a fixture hook by ID."""
        return self._static_get(region, locale, f"/data/wow/fixture-hook/{fixture_hook_id}")

    async def get_fixture_hook_async(
        self, *, region: Region | str, locale: Locale | str, fixture_hook_id: int
    ) -> ApiResponse:
        """Get a fixture hook by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/fixture-hook/{fixture_hook_id}"
        )

    def search_fixture_hook(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for fixture hooks."""
        return self._static_get(region, locale, "/data/wow/search/fixture-hook", **filters)

    async def search_fixture_hook_async(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for fixture hooks."""
        return await self._static_get_async(
            region, locale, "/data/wow/search/fixture-hook", **filters
        )

    def get_room_index(self, *, region: Region | str, locale: Locale | str) -> ApiResponse:
        """Get an index of rooms."""
        return self._static_get(region, locale, "/data/wow/room/index")

    async def get_room_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of rooms."""
        return await self._static_get_async(region, locale, "/data/wow/room/index")

    def get_room(
        self, *, region: Region | str, locale: Locale | str, room_id: int
    ) -> ApiResponse:
        """Get a room by ID."""
        return self._static_get(region, locale, f"/data/wow/room/{room_id}")

    async def get_room_async(
        self, *, region: Region | str, locale: Locale | str, room_id: int
    ) -> ApiResponse:
        """Get a room by ID."""
        return await self._static_get_async(region, locale, f"/data/wow/room/{room_id}")

    def search_room(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for rooms."""
        return self._static_get(region, locale, "/data/wow/search/room", **filters)

    async def search_room_async(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for rooms."""
        return await self._static_get_async(region, locale, "/data/wow/search/room", **filters)

    # ------------------------------------------------------------------
    # Item Appearance — new in Midnight
    # ------------------------------------------------------------------

    def get_item_appearance(
        self, *, region: Region | str, locale: Locale | str, appearance_id: int
    ) -> ApiResponse:
        """Get an item appearance by ID."""
        return self._static_get(
            region, locale, f"/data/wow/item-appearance/{appearance_id}"
        )

    async def get_item_appearance_async(
        self, *, region: Region | str, locale: Locale | str, appearance_id: int
    ) -> ApiResponse:
        """Get an item appearance by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/item-appearance/{appearance_id}"
        )

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
    # Neighborhood Map — new in Midnight
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

    # ------------------------------------------------------------------
    # Item
    # ------------------------------------------------------------------

    def get_item_classes_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of item classes."""
        return self._static_get(region, locale, "/data/wow/item-class/index")

    async def get_item_classes_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of item classes."""
        return await self._static_get_async(region, locale, "/data/wow/item-class/index")

    def get_item_class(
        self, *, region: Region | str, locale: Locale | str, class_id: int
    ) -> ApiResponse:
        """Get an item class by ID."""
        return self._static_get(region, locale, f"/data/wow/item-class/{class_id}")

    async def get_item_class_async(
        self, *, region: Region | str, locale: Locale | str, class_id: int
    ) -> ApiResponse:
        """Get an item class by ID."""
        return await self._static_get_async(region, locale, f"/data/wow/item-class/{class_id}")

    def get_item_sets_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of item sets."""
        return self._static_get(region, locale, "/data/wow/item-set/index")

    async def get_item_sets_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of item sets."""
        return await self._static_get_async(region, locale, "/data/wow/item-set/index")

    def get_item_set(
        self, *, region: Region | str, locale: Locale | str, set_id: int
    ) -> ApiResponse:
        """Get an item set by ID."""
        return self._static_get(region, locale, f"/data/wow/item-set/{set_id}")

    async def get_item_set_async(
        self, *, region: Region | str, locale: Locale | str, set_id: int
    ) -> ApiResponse:
        """Get an item set by ID."""
        return await self._static_get_async(region, locale, f"/data/wow/item-set/{set_id}")

    def get_item_subclass(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        class_id: int,
        subclass_id: int,
    ) -> ApiResponse:
        """Get an item subclass."""
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
        """Get an item subclass."""
        return await self._static_get_async(
            region,
            locale,
            f"/data/wow/item-class/{class_id}/item-subclass/{subclass_id}",
        )

    def get_item(
        self, *, region: Region | str, locale: Locale | str, item_id: int
    ) -> ApiResponse:
        """Get an item by ID."""
        return self._static_get(region, locale, f"/data/wow/item/{item_id}")

    async def get_item_async(
        self, *, region: Region | str, locale: Locale | str, item_id: int
    ) -> ApiResponse:
        """Get an item by ID."""
        return await self._static_get_async(region, locale, f"/data/wow/item/{item_id}")

    def get_item_media(
        self, *, region: Region | str, locale: Locale | str, item_id: int
    ) -> ApiResponse:
        """Get media for an item."""
        return self._static_get(region, locale, f"/data/wow/media/item/{item_id}")

    async def get_item_media_async(
        self, *, region: Region | str, locale: Locale | str, item_id: int
    ) -> ApiResponse:
        """Get media for an item."""
        return await self._static_get_async(region, locale, f"/data/wow/media/item/{item_id}")

    def search_item(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for items."""
        return self._static_get(region, locale, "/data/wow/search/item", **filters)

    async def search_item_async(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for items."""
        return await self._static_get_async(region, locale, "/data/wow/search/item", **filters)

    # ------------------------------------------------------------------
    # Journal
    # ------------------------------------------------------------------

    def get_journal_expansions_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of journal expansions."""
        return self._static_get(region, locale, "/data/wow/journal-expansion/index")

    async def get_journal_expansions_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of journal expansions."""
        return await self._static_get_async(region, locale, "/data/wow/journal-expansion/index")

    def get_journal_expansion(
        self, *, region: Region | str, locale: Locale | str, expansion_id: int
    ) -> ApiResponse:
        """Get a journal expansion by ID."""
        return self._static_get(
            region, locale, f"/data/wow/journal-expansion/{expansion_id}"
        )

    async def get_journal_expansion_async(
        self, *, region: Region | str, locale: Locale | str, expansion_id: int
    ) -> ApiResponse:
        """Get a journal expansion by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/journal-expansion/{expansion_id}"
        )

    def get_journal_encounters_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of journal encounters."""
        return self._static_get(region, locale, "/data/wow/journal-encounter/index")

    async def get_journal_encounters_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of journal encounters."""
        return await self._static_get_async(region, locale, "/data/wow/journal-encounter/index")

    def get_journal_encounter(
        self, *, region: Region | str, locale: Locale | str, encounter_id: int
    ) -> ApiResponse:
        """Get a journal encounter by ID."""
        return self._static_get(
            region, locale, f"/data/wow/journal-encounter/{encounter_id}"
        )

    async def get_journal_encounter_async(
        self, *, region: Region | str, locale: Locale | str, encounter_id: int
    ) -> ApiResponse:
        """Get a journal encounter by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/journal-encounter/{encounter_id}"
        )

    def search_journal_encounter(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for journal encounters."""
        return self._static_get(region, locale, "/data/wow/search/journal-encounter", **filters)

    async def search_journal_encounter_async(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for journal encounters."""
        return await self._static_get_async(
            region, locale, "/data/wow/search/journal-encounter", **filters
        )

    def get_journal_instances_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of journal instances."""
        return self._static_get(region, locale, "/data/wow/journal-instance/index")

    async def get_journal_instances_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of journal instances."""
        return await self._static_get_async(region, locale, "/data/wow/journal-instance/index")

    def get_journal_instance(
        self, *, region: Region | str, locale: Locale | str, instance_id: int
    ) -> ApiResponse:
        """Get a journal instance by ID."""
        return self._static_get(
            region, locale, f"/data/wow/journal-instance/{instance_id}"
        )

    async def get_journal_instance_async(
        self, *, region: Region | str, locale: Locale | str, instance_id: int
    ) -> ApiResponse:
        """Get a journal instance by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/journal-instance/{instance_id}"
        )

    def get_journal_instance_media(
        self, *, region: Region | str, locale: Locale | str, instance_id: int
    ) -> ApiResponse:
        """Get media for a journal instance."""
        return self._static_get(
            region, locale, f"/data/wow/media/journal-instance/{instance_id}"
        )

    async def get_journal_instance_media_async(
        self, *, region: Region | str, locale: Locale | str, instance_id: int
    ) -> ApiResponse:
        """Get media for a journal instance."""
        return await self._static_get_async(
            region, locale, f"/data/wow/media/journal-instance/{instance_id}"
        )

    # ------------------------------------------------------------------
    # Media search
    # ------------------------------------------------------------------

    def search_media(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for media."""
        return self._static_get(region, locale, "/data/wow/search/media", **filters)

    async def search_media_async(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for media."""
        return await self._static_get_async(region, locale, "/data/wow/search/media", **filters)

    # ------------------------------------------------------------------
    # Modified Crafting
    # ------------------------------------------------------------------

    def get_modified_crafting_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get the modified crafting index."""
        return self._static_get(region, locale, "/data/wow/modified-crafting/index")

    async def get_modified_crafting_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get the modified crafting index."""
        return await self._static_get_async(region, locale, "/data/wow/modified-crafting/index")

    def get_modified_crafting_category_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of modified crafting categories."""
        return self._static_get(region, locale, "/data/wow/modified-crafting/category/index")

    async def get_modified_crafting_category_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of modified crafting categories."""
        return await self._static_get_async(
            region, locale, "/data/wow/modified-crafting/category/index"
        )

    def get_modified_crafting_category(
        self, *, region: Region | str, locale: Locale | str, category_id: int
    ) -> ApiResponse:
        """Get a modified crafting category by ID."""
        return self._static_get(
            region, locale, f"/data/wow/modified-crafting/category/{category_id}"
        )

    async def get_modified_crafting_category_async(
        self, *, region: Region | str, locale: Locale | str, category_id: int
    ) -> ApiResponse:
        """Get a modified crafting category by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/modified-crafting/category/{category_id}"
        )

    def get_modified_crafting_reagent_slot_type_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of modified crafting reagent slot types."""
        return self._static_get(
            region, locale, "/data/wow/modified-crafting/reagent-slot-type/index"
        )

    async def get_modified_crafting_reagent_slot_type_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of modified crafting reagent slot types."""
        return await self._static_get_async(
            region, locale, "/data/wow/modified-crafting/reagent-slot-type/index"
        )

    def get_modified_crafting_reagent_slot_type(
        self, *, region: Region | str, locale: Locale | str, slot_type_id: int
    ) -> ApiResponse:
        """Get a modified crafting reagent slot type by ID."""
        return self._static_get(
            region,
            locale,
            f"/data/wow/modified-crafting/reagent-slot-type/{slot_type_id}",
        )

    async def get_modified_crafting_reagent_slot_type_async(
        self, *, region: Region | str, locale: Locale | str, slot_type_id: int
    ) -> ApiResponse:
        """Get a modified crafting reagent slot type by ID."""
        return await self._static_get_async(
            region,
            locale,
            f"/data/wow/modified-crafting/reagent-slot-type/{slot_type_id}",
        )

    # ------------------------------------------------------------------
    # Mount
    # ------------------------------------------------------------------

    def get_mounts_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of mounts."""
        return self._static_get(region, locale, "/data/wow/mount/index")

    async def get_mounts_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of mounts."""
        return await self._static_get_async(region, locale, "/data/wow/mount/index")

    def get_mount(
        self, *, region: Region | str, locale: Locale | str, mount_id: int
    ) -> ApiResponse:
        """Get a mount by ID."""
        return self._static_get(region, locale, f"/data/wow/mount/{mount_id}")

    async def get_mount_async(
        self, *, region: Region | str, locale: Locale | str, mount_id: int
    ) -> ApiResponse:
        """Get a mount by ID."""
        return await self._static_get_async(region, locale, f"/data/wow/mount/{mount_id}")

    def search_mount(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for mounts."""
        return self._static_get(region, locale, "/data/wow/search/mount", **filters)

    async def search_mount_async(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for mounts."""
        return await self._static_get_async(region, locale, "/data/wow/search/mount", **filters)

    # ------------------------------------------------------------------
    # Mythic Keystone Affix
    # ------------------------------------------------------------------

    def get_mythic_keystone_affixes_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of mythic keystone affixes."""
        return self._static_get(region, locale, "/data/wow/keystone-affix/index")

    async def get_mythic_keystone_affixes_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of mythic keystone affixes."""
        return await self._static_get_async(region, locale, "/data/wow/keystone-affix/index")

    def get_mythic_keystone_affix(
        self, *, region: Region | str, locale: Locale | str, affix_id: int
    ) -> ApiResponse:
        """Get a mythic keystone affix by ID."""
        return self._static_get(region, locale, f"/data/wow/keystone-affix/{affix_id}")

    async def get_mythic_keystone_affix_async(
        self, *, region: Region | str, locale: Locale | str, affix_id: int
    ) -> ApiResponse:
        """Get a mythic keystone affix by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/keystone-affix/{affix_id}"
        )

    def get_mythic_keystone_affix_media(
        self, *, region: Region | str, locale: Locale | str, affix_id: int
    ) -> ApiResponse:
        """Get media for a mythic keystone affix."""
        return self._static_get(
            region, locale, f"/data/wow/media/keystone-affix/{affix_id}"
        )

    async def get_mythic_keystone_affix_media_async(
        self, *, region: Region | str, locale: Locale | str, affix_id: int
    ) -> ApiResponse:
        """Get media for a mythic keystone affix."""
        return await self._static_get_async(
            region, locale, f"/data/wow/media/keystone-affix/{affix_id}"
        )

    # ------------------------------------------------------------------
    # Mythic Keystone Dungeon / Index / Period / Season
    # ------------------------------------------------------------------

    def get_mythic_keystone_dungeons_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of mythic keystone dungeons."""
        return self._static_get(
            region, locale, "/data/wow/mythic-keystone/dungeon/index"
        )

    async def get_mythic_keystone_dungeons_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of mythic keystone dungeons."""
        return await self._static_get_async(
            region, locale, "/data/wow/mythic-keystone/dungeon/index"
        )

    def get_mythic_keystone_dungeon(
        self, *, region: Region | str, locale: Locale | str, dungeon_id: int
    ) -> ApiResponse:
        """Get a mythic keystone dungeon by ID."""
        return self._static_get(
            region, locale, f"/data/wow/mythic-keystone/dungeon/{dungeon_id}"
        )

    async def get_mythic_keystone_dungeon_async(
        self, *, region: Region | str, locale: Locale | str, dungeon_id: int
    ) -> ApiResponse:
        """Get a mythic keystone dungeon by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/mythic-keystone/dungeon/{dungeon_id}"
        )

    def get_mythic_keystone_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get the mythic keystone index."""
        return self._dynamic_get(region, locale, "/data/wow/mythic-keystone/index")

    async def get_mythic_keystone_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get the mythic keystone index."""
        return await self._dynamic_get_async(region, locale, "/data/wow/mythic-keystone/index")

    def get_mythic_keystone_periods_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of mythic keystone periods."""
        return self._static_get(region, locale, "/data/wow/mythic-keystone/period/index")

    async def get_mythic_keystone_periods_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of mythic keystone periods."""
        return await self._static_get_async(
            region, locale, "/data/wow/mythic-keystone/period/index"
        )

    def get_mythic_keystone_period(
        self, *, region: Region | str, locale: Locale | str, period_id: int
    ) -> ApiResponse:
        """Get a mythic keystone period by ID."""
        return self._static_get(
            region, locale, f"/data/wow/mythic-keystone/period/{period_id}"
        )

    async def get_mythic_keystone_period_async(
        self, *, region: Region | str, locale: Locale | str, period_id: int
    ) -> ApiResponse:
        """Get a mythic keystone period by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/mythic-keystone/period/{period_id}"
        )

    def get_mythic_keystone_seasons_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of mythic keystone seasons."""
        return self._static_get(region, locale, "/data/wow/mythic-keystone/season/index")

    async def get_mythic_keystone_seasons_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of mythic keystone seasons."""
        return await self._static_get_async(
            region, locale, "/data/wow/mythic-keystone/season/index"
        )

    def get_mythic_keystone_season(
        self, *, region: Region | str, locale: Locale | str, season_id: int
    ) -> ApiResponse:
        """Get a mythic keystone season by ID."""
        return self._static_get(
            region, locale, f"/data/wow/mythic-keystone/season/{season_id}"
        )

    async def get_mythic_keystone_season_async(
        self, *, region: Region | str, locale: Locale | str, season_id: int
    ) -> ApiResponse:
        """Get a mythic keystone season by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/mythic-keystone/season/{season_id}"
        )

    # ------------------------------------------------------------------
    # Mythic Keystone Leaderboard
    # ------------------------------------------------------------------

    def get_mythic_keystone_leaderboards_index(
        self, *, region: Region | str, locale: Locale | str, connected_realm_id: int
    ) -> ApiResponse:
        """Get an index of mythic keystone leaderboards for a connected realm."""
        return self._dynamic_get(
            region,
            locale,
            f"/data/wow/connected-realm/{connected_realm_id}/mythic-leaderboard/index",
        )

    async def get_mythic_keystone_leaderboards_index_async(
        self, *, region: Region | str, locale: Locale | str, connected_realm_id: int
    ) -> ApiResponse:
        """Get an index of mythic keystone leaderboards for a connected realm."""
        return await self._dynamic_get_async(
            region,
            locale,
            f"/data/wow/connected-realm/{connected_realm_id}/mythic-leaderboard/index",
        )

    def get_mythic_keystone_leaderboard(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        connected_realm_id: int,
        dungeon_id: int,
        period_id: int,
    ) -> ApiResponse:
        """Get a mythic keystone leaderboard."""
        return self._dynamic_get(
            region,
            locale,
            f"/data/wow/connected-realm/{connected_realm_id}"
            f"/mythic-leaderboard/{dungeon_id}/period/{period_id}",
        )

    async def get_mythic_keystone_leaderboard_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        connected_realm_id: int,
        dungeon_id: int,
        period_id: int,
    ) -> ApiResponse:
        """Get a mythic keystone leaderboard."""
        return await self._dynamic_get_async(
            region,
            locale,
            f"/data/wow/connected-realm/{connected_realm_id}"
            f"/mythic-leaderboard/{dungeon_id}/period/{period_id}",
        )

    # ------------------------------------------------------------------
    # Mythic Raid Leaderboard
    # ------------------------------------------------------------------

    def get_mythic_raid_leaderboard(
        self, *, region: Region | str, locale: Locale | str, raid: str, faction: str
    ) -> ApiResponse:
        """Get the mythic raid hall of fame leaderboard."""
        return self._dynamic_get(
            region, locale, f"/data/wow/leaderboard/hall-of-fame/{raid}/{faction}"
        )

    async def get_mythic_raid_leaderboard_async(
        self, *, region: Region | str, locale: Locale | str, raid: str, faction: str
    ) -> ApiResponse:
        """Get the mythic raid hall of fame leaderboard."""
        return await self._dynamic_get_async(
            region, locale, f"/data/wow/leaderboard/hall-of-fame/{raid}/{faction}"
        )

    # ------------------------------------------------------------------
    # Pet
    # ------------------------------------------------------------------

    def get_pets_index(self, *, region: Region | str, locale: Locale | str) -> ApiResponse:
        """Get an index of battle pets."""
        return self._static_get(region, locale, "/data/wow/pet/index")

    async def get_pets_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of battle pets."""
        return await self._static_get_async(region, locale, "/data/wow/pet/index")

    def get_pet(
        self, *, region: Region | str, locale: Locale | str, pet_id: int
    ) -> ApiResponse:
        """Get a battle pet by ID."""
        return self._static_get(region, locale, f"/data/wow/pet/{pet_id}")

    async def get_pet_async(
        self, *, region: Region | str, locale: Locale | str, pet_id: int
    ) -> ApiResponse:
        """Get a battle pet by ID."""
        return await self._static_get_async(region, locale, f"/data/wow/pet/{pet_id}")

    def get_pet_media(
        self, *, region: Region | str, locale: Locale | str, pet_id: int
    ) -> ApiResponse:
        """Get media for a battle pet."""
        return self._static_get(region, locale, f"/data/wow/media/pet/{pet_id}")

    async def get_pet_media_async(
        self, *, region: Region | str, locale: Locale | str, pet_id: int
    ) -> ApiResponse:
        """Get media for a battle pet."""
        return await self._static_get_async(region, locale, f"/data/wow/media/pet/{pet_id}")

    def get_pet_abilities_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of pet abilities."""
        return self._static_get(region, locale, "/data/wow/pet-ability/index")

    async def get_pet_abilities_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of pet abilities."""
        return await self._static_get_async(region, locale, "/data/wow/pet-ability/index")

    def get_pet_ability(
        self, *, region: Region | str, locale: Locale | str, ability_id: int
    ) -> ApiResponse:
        """Get a pet ability by ID."""
        return self._static_get(region, locale, f"/data/wow/pet-ability/{ability_id}")

    async def get_pet_ability_async(
        self, *, region: Region | str, locale: Locale | str, ability_id: int
    ) -> ApiResponse:
        """Get a pet ability by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/pet-ability/{ability_id}"
        )

    def get_pet_ability_media(
        self, *, region: Region | str, locale: Locale | str, ability_id: int
    ) -> ApiResponse:
        """Get media for a pet ability."""
        return self._static_get(
            region, locale, f"/data/wow/media/pet-ability/{ability_id}"
        )

    async def get_pet_ability_media_async(
        self, *, region: Region | str, locale: Locale | str, ability_id: int
    ) -> ApiResponse:
        """Get media for a pet ability."""
        return await self._static_get_async(
            region, locale, f"/data/wow/media/pet-ability/{ability_id}"
        )

    # ------------------------------------------------------------------
    # Playable Class / Race / Specialization
    # ------------------------------------------------------------------

    def get_playable_classes_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of playable classes."""
        return self._static_get(region, locale, "/data/wow/playable-class/index")

    async def get_playable_classes_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of playable classes."""
        return await self._static_get_async(region, locale, "/data/wow/playable-class/index")

    def get_playable_class(
        self, *, region: Region | str, locale: Locale | str, class_id: int
    ) -> ApiResponse:
        """Get a playable class by ID."""
        return self._static_get(region, locale, f"/data/wow/playable-class/{class_id}")

    async def get_playable_class_async(
        self, *, region: Region | str, locale: Locale | str, class_id: int
    ) -> ApiResponse:
        """Get a playable class by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/playable-class/{class_id}"
        )

    def get_playable_class_media(
        self, *, region: Region | str, locale: Locale | str, class_id: int
    ) -> ApiResponse:
        """Get media for a playable class."""
        return self._static_get(
            region, locale, f"/data/wow/media/playable-class/{class_id}"
        )

    async def get_playable_class_media_async(
        self, *, region: Region | str, locale: Locale | str, class_id: int
    ) -> ApiResponse:
        """Get media for a playable class."""
        return await self._static_get_async(
            region, locale, f"/data/wow/media/playable-class/{class_id}"
        )

    def get_pvp_talent_slots(
        self, *, region: Region | str, locale: Locale | str, class_id: int
    ) -> ApiResponse:
        """Get PvP talent slots for a playable class."""
        return self._static_get(
            region, locale, f"/data/wow/playable-class/{class_id}/pvp-talent-slots"
        )

    async def get_pvp_talent_slots_async(
        self, *, region: Region | str, locale: Locale | str, class_id: int
    ) -> ApiResponse:
        """Get PvP talent slots for a playable class."""
        return await self._static_get_async(
            region, locale, f"/data/wow/playable-class/{class_id}/pvp-talent-slots"
        )

    def get_playable_races_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of playable races."""
        return self._static_get(region, locale, "/data/wow/playable-race/index")

    async def get_playable_races_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of playable races."""
        return await self._static_get_async(region, locale, "/data/wow/playable-race/index")

    def get_playable_race(
        self, *, region: Region | str, locale: Locale | str, race_id: int
    ) -> ApiResponse:
        """Get a playable race by ID."""
        return self._static_get(region, locale, f"/data/wow/playable-race/{race_id}")

    async def get_playable_race_async(
        self, *, region: Region | str, locale: Locale | str, race_id: int
    ) -> ApiResponse:
        """Get a playable race by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/playable-race/{race_id}"
        )

    def get_playable_specializations_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of playable specializations."""
        return self._static_get(region, locale, "/data/wow/playable-specialization/index")

    async def get_playable_specializations_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of playable specializations."""
        return await self._static_get_async(
            region, locale, "/data/wow/playable-specialization/index"
        )

    def get_playable_specialization(
        self, *, region: Region | str, locale: Locale | str, spec_id: int
    ) -> ApiResponse:
        """Get a playable specialization by ID."""
        return self._static_get(
            region, locale, f"/data/wow/playable-specialization/{spec_id}"
        )

    async def get_playable_specialization_async(
        self, *, region: Region | str, locale: Locale | str, spec_id: int
    ) -> ApiResponse:
        """Get a playable specialization by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/playable-specialization/{spec_id}"
        )

    def get_playable_specialization_media(
        self, *, region: Region | str, locale: Locale | str, spec_id: int
    ) -> ApiResponse:
        """Get media for a playable specialization."""
        return self._static_get(
            region, locale, f"/data/wow/media/playable-specialization/{spec_id}"
        )

    async def get_playable_specialization_media_async(
        self, *, region: Region | str, locale: Locale | str, spec_id: int
    ) -> ApiResponse:
        """Get media for a playable specialization."""
        return await self._static_get_async(
            region, locale, f"/data/wow/media/playable-specialization/{spec_id}"
        )

    # ------------------------------------------------------------------
    # Power Type
    # ------------------------------------------------------------------

    def get_power_types_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of power types."""
        return self._static_get(region, locale, "/data/wow/power-type/index")

    async def get_power_types_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of power types."""
        return await self._static_get_async(region, locale, "/data/wow/power-type/index")

    def get_power_type(
        self, *, region: Region | str, locale: Locale | str, power_type_id: int
    ) -> ApiResponse:
        """Get a power type by ID."""
        return self._static_get(region, locale, f"/data/wow/power-type/{power_type_id}")

    async def get_power_type_async(
        self, *, region: Region | str, locale: Locale | str, power_type_id: int
    ) -> ApiResponse:
        """Get a power type by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/power-type/{power_type_id}"
        )

    # ------------------------------------------------------------------
    # Profession / Recipe
    # ------------------------------------------------------------------

    def get_professions_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of professions."""
        return self._static_get(region, locale, "/data/wow/profession/index")

    async def get_professions_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of professions."""
        return await self._static_get_async(region, locale, "/data/wow/profession/index")

    def get_profession(
        self, *, region: Region | str, locale: Locale | str, profession_id: int
    ) -> ApiResponse:
        """Get a profession by ID."""
        return self._static_get(region, locale, f"/data/wow/profession/{profession_id}")

    async def get_profession_async(
        self, *, region: Region | str, locale: Locale | str, profession_id: int
    ) -> ApiResponse:
        """Get a profession by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/profession/{profession_id}"
        )

    def get_profession_media(
        self, *, region: Region | str, locale: Locale | str, profession_id: int
    ) -> ApiResponse:
        """Get media for a profession."""
        return self._static_get(
            region, locale, f"/data/wow/media/profession/{profession_id}"
        )

    async def get_profession_media_async(
        self, *, region: Region | str, locale: Locale | str, profession_id: int
    ) -> ApiResponse:
        """Get media for a profession."""
        return await self._static_get_async(
            region, locale, f"/data/wow/media/profession/{profession_id}"
        )

    def get_profession_skill_tier(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        profession_id: int,
        skill_tier_id: int,
    ) -> ApiResponse:
        """Get a profession skill tier."""
        return self._static_get(
            region,
            locale,
            f"/data/wow/profession/{profession_id}/skill-tier/{skill_tier_id}",
        )

    async def get_profession_skill_tier_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        profession_id: int,
        skill_tier_id: int,
    ) -> ApiResponse:
        """Get a profession skill tier."""
        return await self._static_get_async(
            region,
            locale,
            f"/data/wow/profession/{profession_id}/skill-tier/{skill_tier_id}",
        )

    def get_recipe(
        self, *, region: Region | str, locale: Locale | str, recipe_id: int
    ) -> ApiResponse:
        """Get a recipe by ID."""
        return self._static_get(region, locale, f"/data/wow/recipe/{recipe_id}")

    async def get_recipe_async(
        self, *, region: Region | str, locale: Locale | str, recipe_id: int
    ) -> ApiResponse:
        """Get a recipe by ID."""
        return await self._static_get_async(region, locale, f"/data/wow/recipe/{recipe_id}")

    def get_recipe_media(
        self, *, region: Region | str, locale: Locale | str, recipe_id: int
    ) -> ApiResponse:
        """Get media for a recipe."""
        return self._static_get(region, locale, f"/data/wow/media/recipe/{recipe_id}")

    async def get_recipe_media_async(
        self, *, region: Region | str, locale: Locale | str, recipe_id: int
    ) -> ApiResponse:
        """Get media for a recipe."""
        return await self._static_get_async(
            region, locale, f"/data/wow/media/recipe/{recipe_id}"
        )

    # ------------------------------------------------------------------
    # PvP Season / Leaderboard / Reward
    # ------------------------------------------------------------------

    def get_pvp_seasons_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of PvP seasons."""
        return self._dynamic_get(region, locale, "/data/wow/pvp-season/index")

    async def get_pvp_seasons_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of PvP seasons."""
        return await self._dynamic_get_async(region, locale, "/data/wow/pvp-season/index")

    def get_pvp_season(
        self, *, region: Region | str, locale: Locale | str, season_id: int
    ) -> ApiResponse:
        """Get a PvP season by ID."""
        return self._dynamic_get(region, locale, f"/data/wow/pvp-season/{season_id}")

    async def get_pvp_season_async(
        self, *, region: Region | str, locale: Locale | str, season_id: int
    ) -> ApiResponse:
        """Get a PvP season by ID."""
        return await self._dynamic_get_async(
            region, locale, f"/data/wow/pvp-season/{season_id}"
        )

    def get_pvp_leaderboards_index(
        self, *, region: Region | str, locale: Locale | str, season_id: int
    ) -> ApiResponse:
        """Get an index of PvP leaderboards for a season."""
        return self._dynamic_get(
            region, locale, f"/data/wow/pvp-season/{season_id}/pvp-leaderboard/index"
        )

    async def get_pvp_leaderboards_index_async(
        self, *, region: Region | str, locale: Locale | str, season_id: int
    ) -> ApiResponse:
        """Get an index of PvP leaderboards for a season."""
        return await self._dynamic_get_async(
            region, locale, f"/data/wow/pvp-season/{season_id}/pvp-leaderboard/index"
        )

    def get_pvp_leaderboard(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        season_id: int,
        bracket: str,
    ) -> ApiResponse:
        """Get a PvP leaderboard for a bracket."""
        return self._dynamic_get(
            region, locale, f"/data/wow/pvp-season/{season_id}/pvp-leaderboard/{bracket}"
        )

    async def get_pvp_leaderboard_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        season_id: int,
        bracket: str,
    ) -> ApiResponse:
        """Get a PvP leaderboard for a bracket."""
        return await self._dynamic_get_async(
            region, locale, f"/data/wow/pvp-season/{season_id}/pvp-leaderboard/{bracket}"
        )

    def get_pvp_rewards_index(
        self, *, region: Region | str, locale: Locale | str, season_id: int
    ) -> ApiResponse:
        """Get an index of PvP rewards for a season."""
        return self._dynamic_get(
            region, locale, f"/data/wow/pvp-season/{season_id}/pvp-reward/index"
        )

    async def get_pvp_rewards_index_async(
        self, *, region: Region | str, locale: Locale | str, season_id: int
    ) -> ApiResponse:
        """Get an index of PvP rewards for a season."""
        return await self._dynamic_get_async(
            region, locale, f"/data/wow/pvp-season/{season_id}/pvp-reward/index"
        )

    # ------------------------------------------------------------------
    # PvP Tier
    # ------------------------------------------------------------------

    def get_pvp_tiers_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of PvP tiers."""
        return self._static_get(region, locale, "/data/wow/pvp-tier/index")

    async def get_pvp_tiers_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of PvP tiers."""
        return await self._static_get_async(region, locale, "/data/wow/pvp-tier/index")

    def get_pvp_tier(
        self, *, region: Region | str, locale: Locale | str, tier_id: int
    ) -> ApiResponse:
        """Get a PvP tier by ID."""
        return self._static_get(region, locale, f"/data/wow/pvp-tier/{tier_id}")

    async def get_pvp_tier_async(
        self, *, region: Region | str, locale: Locale | str, tier_id: int
    ) -> ApiResponse:
        """Get a PvP tier by ID."""
        return await self._static_get_async(region, locale, f"/data/wow/pvp-tier/{tier_id}")

    def get_pvp_tier_media(
        self, *, region: Region | str, locale: Locale | str, tier_id: int
    ) -> ApiResponse:
        """Get media for a PvP tier."""
        return self._static_get(region, locale, f"/data/wow/media/pvp-tier/{tier_id}")

    async def get_pvp_tier_media_async(
        self, *, region: Region | str, locale: Locale | str, tier_id: int
    ) -> ApiResponse:
        """Get media for a PvP tier."""
        return await self._static_get_async(
            region, locale, f"/data/wow/media/pvp-tier/{tier_id}"
        )

    # ------------------------------------------------------------------
    # Quest
    # ------------------------------------------------------------------

    def get_quests_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of quests."""
        return self._static_get(region, locale, "/data/wow/quest/index")

    async def get_quests_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of quests."""
        return await self._static_get_async(region, locale, "/data/wow/quest/index")

    def get_quest(
        self, *, region: Region | str, locale: Locale | str, quest_id: int
    ) -> ApiResponse:
        """Get a quest by ID."""
        return self._static_get(region, locale, f"/data/wow/quest/{quest_id}")

    async def get_quest_async(
        self, *, region: Region | str, locale: Locale | str, quest_id: int
    ) -> ApiResponse:
        """Get a quest by ID."""
        return await self._static_get_async(region, locale, f"/data/wow/quest/{quest_id}")

    def get_quest_categories_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of quest categories."""
        return self._static_get(region, locale, "/data/wow/quest/category/index")

    async def get_quest_categories_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of quest categories."""
        return await self._static_get_async(region, locale, "/data/wow/quest/category/index")

    def get_quest_category(
        self, *, region: Region | str, locale: Locale | str, category_id: int
    ) -> ApiResponse:
        """Get a quest category by ID."""
        return self._static_get(region, locale, f"/data/wow/quest/category/{category_id}")

    async def get_quest_category_async(
        self, *, region: Region | str, locale: Locale | str, category_id: int
    ) -> ApiResponse:
        """Get a quest category by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/quest/category/{category_id}"
        )

    def get_quest_areas_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of quest areas."""
        return self._static_get(region, locale, "/data/wow/quest/area/index")

    async def get_quest_areas_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of quest areas."""
        return await self._static_get_async(region, locale, "/data/wow/quest/area/index")

    def get_quest_area(
        self, *, region: Region | str, locale: Locale | str, area_id: int
    ) -> ApiResponse:
        """Get a quest area by ID."""
        return self._static_get(region, locale, f"/data/wow/quest/area/{area_id}")

    async def get_quest_area_async(
        self, *, region: Region | str, locale: Locale | str, area_id: int
    ) -> ApiResponse:
        """Get a quest area by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/quest/area/{area_id}"
        )

    def get_quest_types_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of quest types."""
        return self._static_get(region, locale, "/data/wow/quest/type/index")

    async def get_quest_types_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of quest types."""
        return await self._static_get_async(region, locale, "/data/wow/quest/type/index")

    def get_quest_type(
        self, *, region: Region | str, locale: Locale | str, type_id: int
    ) -> ApiResponse:
        """Get a quest type by ID."""
        return self._static_get(region, locale, f"/data/wow/quest/type/{type_id}")

    async def get_quest_type_async(
        self, *, region: Region | str, locale: Locale | str, type_id: int
    ) -> ApiResponse:
        """Get a quest type by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/quest/type/{type_id}"
        )

    # ------------------------------------------------------------------
    # Realm / Region
    # ------------------------------------------------------------------

    def get_realms_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of realms."""
        return self._dynamic_get(region, locale, "/data/wow/realm/index")

    async def get_realms_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of realms."""
        return await self._dynamic_get_async(region, locale, "/data/wow/realm/index")

    def get_realm(
        self, *, region: Region | str, locale: Locale | str, realm_slug: str
    ) -> ApiResponse:
        """Get a realm by slug."""
        return self._dynamic_get(region, locale, f"/data/wow/realm/{realm_slug.lower()}")

    async def get_realm_async(
        self, *, region: Region | str, locale: Locale | str, realm_slug: str
    ) -> ApiResponse:
        """Get a realm by slug."""
        return await self._dynamic_get_async(
            region, locale, f"/data/wow/realm/{realm_slug.lower()}"
        )

    def search_realm(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for realms."""
        return self._dynamic_get(region, locale, "/data/wow/search/realm", **filters)

    async def search_realm_async(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for realms."""
        return await self._dynamic_get_async(
            region, locale, "/data/wow/search/realm", **filters
        )

    def get_regions_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of regions."""
        return self._dynamic_get(region, locale, "/data/wow/region/index")

    async def get_regions_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of regions."""
        return await self._dynamic_get_async(region, locale, "/data/wow/region/index")

    def get_region(
        self, *, region: Region | str, locale: Locale | str, region_id: int
    ) -> ApiResponse:
        """Get a region by ID."""
        return self._dynamic_get(region, locale, f"/data/wow/region/{region_id}")

    async def get_region_async(
        self, *, region: Region | str, locale: Locale | str, region_id: int
    ) -> ApiResponse:
        """Get a region by ID."""
        return await self._dynamic_get_async(region, locale, f"/data/wow/region/{region_id}")

    # ------------------------------------------------------------------
    # Reputation
    # ------------------------------------------------------------------

    def get_reputation_factions_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of reputation factions."""
        return self._static_get(region, locale, "/data/wow/reputation-faction/index")

    async def get_reputation_factions_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of reputation factions."""
        return await self._static_get_async(region, locale, "/data/wow/reputation-faction/index")

    def get_reputation_faction(
        self, *, region: Region | str, locale: Locale | str, faction_id: int
    ) -> ApiResponse:
        """Get a reputation faction by ID."""
        return self._static_get(
            region, locale, f"/data/wow/reputation-faction/{faction_id}"
        )

    async def get_reputation_faction_async(
        self, *, region: Region | str, locale: Locale | str, faction_id: int
    ) -> ApiResponse:
        """Get a reputation faction by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/reputation-faction/{faction_id}"
        )

    def get_reputation_tiers_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of reputation tiers."""
        return self._static_get(region, locale, "/data/wow/reputation-tiers/index")

    async def get_reputation_tiers_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of reputation tiers."""
        return await self._static_get_async(region, locale, "/data/wow/reputation-tiers/index")

    def get_reputation_tiers(
        self, *, region: Region | str, locale: Locale | str, tiers_id: int
    ) -> ApiResponse:
        """Get reputation tiers by ID."""
        return self._static_get(region, locale, f"/data/wow/reputation-tiers/{tiers_id}")

    async def get_reputation_tiers_async(
        self, *, region: Region | str, locale: Locale | str, tiers_id: int
    ) -> ApiResponse:
        """Get reputation tiers by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/reputation-tiers/{tiers_id}"
        )

    # ------------------------------------------------------------------
    # Spell
    # ------------------------------------------------------------------

    def get_spell(
        self, *, region: Region | str, locale: Locale | str, spell_id: int
    ) -> ApiResponse:
        """Get a spell by ID."""
        return self._static_get(region, locale, f"/data/wow/spell/{spell_id}")

    async def get_spell_async(
        self, *, region: Region | str, locale: Locale | str, spell_id: int
    ) -> ApiResponse:
        """Get a spell by ID."""
        return await self._static_get_async(region, locale, f"/data/wow/spell/{spell_id}")

    def get_spell_media(
        self, *, region: Region | str, locale: Locale | str, spell_id: int
    ) -> ApiResponse:
        """Get media for a spell."""
        return self._static_get(region, locale, f"/data/wow/media/spell/{spell_id}")

    async def get_spell_media_async(
        self, *, region: Region | str, locale: Locale | str, spell_id: int
    ) -> ApiResponse:
        """Get media for a spell."""
        return await self._static_get_async(region, locale, f"/data/wow/media/spell/{spell_id}")

    def search_spell(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for spells."""
        return self._static_get(region, locale, "/data/wow/search/spell", **filters)

    async def search_spell_async(
        self, *, region: Region | str, locale: Locale | str, **filters: Any
    ) -> ApiResponse:
        """Search for spells."""
        return await self._static_get_async(region, locale, "/data/wow/search/spell", **filters)

    # ------------------------------------------------------------------
    # Talent / PvP Talent / Talent Tree
    # ------------------------------------------------------------------

    def get_talents_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of talents."""
        return self._static_get(region, locale, "/data/wow/talent/index")

    async def get_talents_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of talents."""
        return await self._static_get_async(region, locale, "/data/wow/talent/index")

    def get_talent(
        self, *, region: Region | str, locale: Locale | str, talent_id: int
    ) -> ApiResponse:
        """Get a talent by ID."""
        return self._static_get(region, locale, f"/data/wow/talent/{talent_id}")

    async def get_talent_async(
        self, *, region: Region | str, locale: Locale | str, talent_id: int
    ) -> ApiResponse:
        """Get a talent by ID."""
        return await self._static_get_async(region, locale, f"/data/wow/talent/{talent_id}")

    def get_pvp_talents_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of PvP talents."""
        return self._static_get(region, locale, "/data/wow/pvp-talent/index")

    async def get_pvp_talents_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of PvP talents."""
        return await self._static_get_async(region, locale, "/data/wow/pvp-talent/index")

    def get_pvp_talent(
        self, *, region: Region | str, locale: Locale | str, talent_id: int
    ) -> ApiResponse:
        """Get a PvP talent by ID."""
        return self._static_get(region, locale, f"/data/wow/pvp-talent/{talent_id}")

    async def get_pvp_talent_async(
        self, *, region: Region | str, locale: Locale | str, talent_id: int
    ) -> ApiResponse:
        """Get a PvP talent by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/pvp-talent/{talent_id}"
        )

    def get_talent_tree_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of talent trees."""
        return self._static_get(region, locale, "/data/wow/talent-tree/index")

    async def get_talent_tree_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of talent trees."""
        return await self._static_get_async(region, locale, "/data/wow/talent-tree/index")

    def get_talent_tree(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        tree_id: int,
        spec_id: int,
    ) -> ApiResponse:
        """Get a talent tree for a specialization."""
        return self._static_get(
            region,
            locale,
            f"/data/wow/talent-tree/{tree_id}/playable-specialization/{spec_id}",
        )

    async def get_talent_tree_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        tree_id: int,
        spec_id: int,
    ) -> ApiResponse:
        """Get a talent tree for a specialization."""
        return await self._static_get_async(
            region,
            locale,
            f"/data/wow/talent-tree/{tree_id}/playable-specialization/{spec_id}",
        )

    def get_talent_tree_nodes(
        self, *, region: Region | str, locale: Locale | str, tree_id: int
    ) -> ApiResponse:
        """Get talent tree nodes."""
        return self._static_get(region, locale, f"/data/wow/talent-tree/{tree_id}")

    async def get_talent_tree_nodes_async(
        self, *, region: Region | str, locale: Locale | str, tree_id: int
    ) -> ApiResponse:
        """Get talent tree nodes."""
        return await self._static_get_async(
            region, locale, f"/data/wow/talent-tree/{tree_id}"
        )

    # ------------------------------------------------------------------
    # Tech Talent
    # ------------------------------------------------------------------

    def get_tech_talent_tree_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of tech talent trees."""
        return self._static_get(region, locale, "/data/wow/tech-talent-tree/index")

    async def get_tech_talent_tree_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of tech talent trees."""
        return await self._static_get_async(region, locale, "/data/wow/tech-talent-tree/index")

    def get_tech_talent_tree(
        self, *, region: Region | str, locale: Locale | str, tree_id: int
    ) -> ApiResponse:
        """Get a tech talent tree by ID."""
        return self._static_get(region, locale, f"/data/wow/tech-talent-tree/{tree_id}")

    async def get_tech_talent_tree_async(
        self, *, region: Region | str, locale: Locale | str, tree_id: int
    ) -> ApiResponse:
        """Get a tech talent tree by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/tech-talent-tree/{tree_id}"
        )

    def get_tech_talent_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of tech talents."""
        return self._static_get(region, locale, "/data/wow/tech-talent/index")

    async def get_tech_talent_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of tech talents."""
        return await self._static_get_async(region, locale, "/data/wow/tech-talent/index")

    def get_tech_talent(
        self, *, region: Region | str, locale: Locale | str, talent_id: int
    ) -> ApiResponse:
        """Get a tech talent by ID."""
        return self._static_get(region, locale, f"/data/wow/tech-talent/{talent_id}")

    async def get_tech_talent_async(
        self, *, region: Region | str, locale: Locale | str, talent_id: int
    ) -> ApiResponse:
        """Get a tech talent by ID."""
        return await self._static_get_async(
            region, locale, f"/data/wow/tech-talent/{talent_id}"
        )

    def get_tech_talent_media(
        self, *, region: Region | str, locale: Locale | str, talent_id: int
    ) -> ApiResponse:
        """Get media for a tech talent."""
        return self._static_get(
            region, locale, f"/data/wow/media/tech-talent/{talent_id}"
        )

    async def get_tech_talent_media_async(
        self, *, region: Region | str, locale: Locale | str, talent_id: int
    ) -> ApiResponse:
        """Get media for a tech talent."""
        return await self._static_get_async(
            region, locale, f"/data/wow/media/tech-talent/{talent_id}"
        )

    # ------------------------------------------------------------------
    # Title / Toy / Token
    # ------------------------------------------------------------------

    def get_titles_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of titles."""
        return self._static_get(region, locale, "/data/wow/title/index")

    async def get_titles_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of titles."""
        return await self._static_get_async(region, locale, "/data/wow/title/index")

    def get_title(
        self, *, region: Region | str, locale: Locale | str, title_id: int
    ) -> ApiResponse:
        """Get a title by ID."""
        return self._static_get(region, locale, f"/data/wow/title/{title_id}")

    async def get_title_async(
        self, *, region: Region | str, locale: Locale | str, title_id: int
    ) -> ApiResponse:
        """Get a title by ID."""
        return await self._static_get_async(region, locale, f"/data/wow/title/{title_id}")

    def get_toy_index(self, *, region: Region | str, locale: Locale | str) -> ApiResponse:
        """Get an index of toys."""
        return self._static_get(region, locale, "/data/wow/toy/index")

    async def get_toy_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get an index of toys."""
        return await self._static_get_async(region, locale, "/data/wow/toy/index")

    def get_toy(
        self, *, region: Region | str, locale: Locale | str, toy_id: int
    ) -> ApiResponse:
        """Get a toy by ID."""
        return self._static_get(region, locale, f"/data/wow/toy/{toy_id}")

    async def get_toy_async(
        self, *, region: Region | str, locale: Locale | str, toy_id: int
    ) -> ApiResponse:
        """Get a toy by ID."""
        return await self._static_get_async(region, locale, f"/data/wow/toy/{toy_id}")

    def get_token_index(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get the WoW token index."""
        return self._dynamic_get(region, locale, "/data/wow/token/index")

    async def get_token_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get the WoW token index."""
        return await self._dynamic_get_async(region, locale, "/data/wow/token/index")


# ----------------------------------------------------------------------
# Module-level helper
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
