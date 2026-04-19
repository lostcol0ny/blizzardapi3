"""World of Warcraft Profile API — direct endpoint methods (retail).

Covers character-scoped endpoints (public data, app token), account-scoped
endpoints (require user OAuth token via ``access_token=``), and guild
endpoints (public data, path under ``/data/wow/guild/``).

Classic profile endpoints live in :mod:`.wow_classic`.
"""

from __future__ import annotations

from typing import Any

from ..core.client import BaseClient
from ..core.executor import ApiResponse, RequestExecutor
from ..types import Locale, Region


class WowProfile:
    """WoW Profile endpoints (retail).

    Character and guild methods use an app-level (client-credentials) token.
    ``get_account_*`` methods additionally require a user access token obtained
    via the Authorization Code flow; pass it as ``access_token=``.
    """

    def __init__(self, client: BaseClient, executor: RequestExecutor):
        self._client = client
        self._executor = executor

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def _profile_get(
        self,
        region: Region | str,
        locale: Locale | str,
        path: str,
        *,
        access_token: str | None = None,
        **extra: Any,
    ) -> ApiResponse:
        r, params = _normalize(region, locale, namespace_type="profile", extra=extra)
        if access_token is not None:
            params["access_token"] = access_token
        return self._executor.execute(
            region=r, path=path, params=params, client=self._client.sync_client
        )

    async def _profile_get_async(
        self,
        region: Region | str,
        locale: Locale | str,
        path: str,
        *,
        access_token: str | None = None,
        **extra: Any,
    ) -> ApiResponse:
        r, params = _normalize(region, locale, namespace_type="profile", extra=extra)
        if access_token is not None:
            params["access_token"] = access_token
        return await self._executor.execute_async(
            region=r, path=path, params=params, client=self._client.async_client
        )

    # ------------------------------------------------------------------
    # Account Profile (requires user access_token)
    # ------------------------------------------------------------------

    def get_account_profile_summary(
        self, *, region: Region | str, locale: Locale | str, access_token: str
    ) -> ApiResponse:
        """Get the authenticated account's WoW profile summary."""
        return self._profile_get(region, locale, "/profile/user/wow", access_token=access_token)

    async def get_account_profile_summary_async(
        self, *, region: Region | str, locale: Locale | str, access_token: str
    ) -> ApiResponse:
        """Get the authenticated account's WoW profile summary."""
        return await self._profile_get_async(
            region, locale, "/profile/user/wow", access_token=access_token
        )

    def get_protected_character_profile_summary(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        access_token: str,
        realm_id: int,
        character_id: int,
    ) -> ApiResponse:
        """Get a protected character profile summary."""
        return self._profile_get(
            region,
            locale,
            f"/profile/user/wow/protected-character/{realm_id}-{character_id}",
            access_token=access_token,
        )

    async def get_protected_character_profile_summary_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        access_token: str,
        realm_id: int,
        character_id: int,
    ) -> ApiResponse:
        """Get a protected character profile summary."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/user/wow/protected-character/{realm_id}-{character_id}",
            access_token=access_token,
        )

    def get_account_collections_index(
        self, *, region: Region | str, locale: Locale | str, access_token: str
    ) -> ApiResponse:
        """Get the authenticated account's collections index."""
        return self._profile_get(
            region, locale, "/profile/user/wow/collections", access_token=access_token
        )

    async def get_account_collections_index_async(
        self, *, region: Region | str, locale: Locale | str, access_token: str
    ) -> ApiResponse:
        """Get the authenticated account's collections index."""
        return await self._profile_get_async(
            region, locale, "/profile/user/wow/collections", access_token=access_token
        )

    def get_account_decor_collection_summary(
        self, *, region: Region | str, locale: Locale | str, access_token: str
    ) -> ApiResponse:
        """Get the authenticated account's decor collection."""
        return self._profile_get(
            region, locale, "/profile/user/wow/collections/decor", access_token=access_token
        )

    async def get_account_decor_collection_summary_async(
        self, *, region: Region | str, locale: Locale | str, access_token: str
    ) -> ApiResponse:
        """Get the authenticated account's decor collection."""
        return await self._profile_get_async(
            region, locale, "/profile/user/wow/collections/decor", access_token=access_token
        )

    def get_account_mounts_collection_summary(
        self, *, region: Region | str, locale: Locale | str, access_token: str
    ) -> ApiResponse:
        """Get the authenticated account's mounts collection."""
        return self._profile_get(
            region, locale, "/profile/user/wow/collections/mounts", access_token=access_token
        )

    async def get_account_mounts_collection_summary_async(
        self, *, region: Region | str, locale: Locale | str, access_token: str
    ) -> ApiResponse:
        """Get the authenticated account's mounts collection."""
        return await self._profile_get_async(
            region, locale, "/profile/user/wow/collections/mounts", access_token=access_token
        )

    def get_account_pets_collection_summary(
        self, *, region: Region | str, locale: Locale | str, access_token: str
    ) -> ApiResponse:
        """Get the authenticated account's battle pets collection."""
        return self._profile_get(
            region, locale, "/profile/user/wow/collections/pets", access_token=access_token
        )

    async def get_account_pets_collection_summary_async(
        self, *, region: Region | str, locale: Locale | str, access_token: str
    ) -> ApiResponse:
        """Get the authenticated account's battle pets collection."""
        return await self._profile_get_async(
            region, locale, "/profile/user/wow/collections/pets", access_token=access_token
        )

    def get_account_heirlooms_collection_summary(
        self, *, region: Region | str, locale: Locale | str, access_token: str
    ) -> ApiResponse:
        """Get the authenticated account's heirlooms collection."""
        return self._profile_get(
            region, locale, "/profile/user/wow/collections/heirlooms", access_token=access_token
        )

    async def get_account_heirlooms_collection_summary_async(
        self, *, region: Region | str, locale: Locale | str, access_token: str
    ) -> ApiResponse:
        """Get the authenticated account's heirlooms collection."""
        return await self._profile_get_async(
            region, locale, "/profile/user/wow/collections/heirlooms", access_token=access_token
        )

    def get_account_toys_collection_summary(
        self, *, region: Region | str, locale: Locale | str, access_token: str
    ) -> ApiResponse:
        """Get the authenticated account's toys collection."""
        return self._profile_get(
            region, locale, "/profile/user/wow/collections/toys", access_token=access_token
        )

    async def get_account_toys_collection_summary_async(
        self, *, region: Region | str, locale: Locale | str, access_token: str
    ) -> ApiResponse:
        """Get the authenticated account's toys collection."""
        return await self._profile_get_async(
            region, locale, "/profile/user/wow/collections/toys", access_token=access_token
        )

    def get_account_transmog_collection_summary(
        self, *, region: Region | str, locale: Locale | str, access_token: str
    ) -> ApiResponse:
        """Get the authenticated account's transmog collection."""
        return self._profile_get(
            region, locale, "/profile/user/wow/collections/transmogs", access_token=access_token
        )

    async def get_account_transmog_collection_summary_async(
        self, *, region: Region | str, locale: Locale | str, access_token: str
    ) -> ApiResponse:
        """Get the authenticated account's transmog collection."""
        return await self._profile_get_async(
            region, locale, "/profile/user/wow/collections/transmogs", access_token=access_token
        )

    # ------------------------------------------------------------------
    # Character Profile
    # ------------------------------------------------------------------

    def get_character_profile_summary(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character profile summary."""
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
        """Get a character profile summary."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}",
        )

    def get_character_profile_status(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character profile status."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}/status",
        )

    async def get_character_profile_status_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character profile status."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}/status",
        )

    # ------------------------------------------------------------------
    # Character Achievements
    # ------------------------------------------------------------------

    def get_character_achievements_summary(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's achievements summary."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}/achievements",
        )

    async def get_character_achievements_summary_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's achievements summary."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}/achievements",
        )

    def get_character_achievement_statistics(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's achievement statistics."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}"
            "/achievements/statistics",
        )

    async def get_character_achievement_statistics_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's achievement statistics."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}"
            "/achievements/statistics",
        )

    # ------------------------------------------------------------------
    # Character Appearance
    # ------------------------------------------------------------------

    def get_character_appearance_summary(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's appearance summary."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}/appearance",
        )

    async def get_character_appearance_summary_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's appearance summary."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}/appearance",
        )

    # ------------------------------------------------------------------
    # Character Collections
    # ------------------------------------------------------------------

    def get_character_collections_index(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's collections index."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}/collections",
        )

    async def get_character_collections_index_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's collections index."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}/collections",
        )

    def get_character_decor_collection(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's decor collection (new in Midnight)."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}"
            "/collections/decor",
        )

    async def get_character_decor_collection_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's decor collection (new in Midnight)."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}"
            "/collections/decor",
        )

    def get_character_mounts_collection_summary(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's mounts collection."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}"
            "/collections/mounts",
        )

    async def get_character_mounts_collection_summary_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's mounts collection."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}"
            "/collections/mounts",
        )

    def get_character_pets_collection_summary(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's battle pets collection."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}"
            "/collections/pets",
        )

    async def get_character_pets_collection_summary_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's battle pets collection."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}"
            "/collections/pets",
        )

    def get_character_heirlooms_collection_summary(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's heirlooms collection."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}"
            "/collections/heirlooms",
        )

    async def get_character_heirlooms_collection_summary_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's heirlooms collection."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}"
            "/collections/heirlooms",
        )

    def get_character_toys_collection_summary(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's toys collection."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}"
            "/collections/toys",
        )

    async def get_character_toys_collection_summary_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's toys collection."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}"
            "/collections/toys",
        )

    def get_character_transmog_collection_summary(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's transmog collection."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}"
            "/collections/transmogs",
        )

    async def get_character_transmog_collection_summary_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's transmog collection."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}"
            "/collections/transmogs",
        )

    # ------------------------------------------------------------------
    # Character Encounters
    # ------------------------------------------------------------------

    def get_character_encounters_summary(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's encounters summary."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}/encounters",
        )

    async def get_character_encounters_summary_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's encounters summary."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}/encounters",
        )

    def get_character_dungeons(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's dungeon encounters."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}"
            "/encounters/dungeons",
        )

    async def get_character_dungeons_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's dungeon encounters."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}"
            "/encounters/dungeons",
        )

    def get_character_raids(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's raid encounters."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}"
            "/encounters/raids",
        )

    async def get_character_raids_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's raid encounters."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}"
            "/encounters/raids",
        )

    # ------------------------------------------------------------------
    # Character Equipment / Hunter Pets / Media
    # ------------------------------------------------------------------

    def get_character_equipment_summary(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's equipment summary."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}/equipment",
        )

    async def get_character_equipment_summary_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's equipment summary."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}/equipment",
        )

    def get_character_hunter_pets_summary(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's hunter pets summary."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}/hunter-pets",
        )

    async def get_character_hunter_pets_summary_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's hunter pets summary."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}/hunter-pets",
        )

    def get_character_media_summary(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's media (avatar, portrait, etc.)."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}"
            "/character-media",
        )

    async def get_character_media_summary_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's media (avatar, portrait, etc.)."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}"
            "/character-media",
        )

    # ------------------------------------------------------------------
    # Character Mythic Keystone Profile
    # ------------------------------------------------------------------

    def get_character_mythic_keystone_profile_index(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's mythic keystone profile index."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}"
            "/mythic-keystone-profile",
        )

    async def get_character_mythic_keystone_profile_index_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's mythic keystone profile index."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}"
            "/mythic-keystone-profile",
        )

    def get_character_mythic_keystone_season_details(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
        season_id: int,
    ) -> ApiResponse:
        """Get a character's mythic keystone season details."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}"
            f"/mythic-keystone-profile/season/{season_id}",
        )

    async def get_character_mythic_keystone_season_details_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
        season_id: int,
    ) -> ApiResponse:
        """Get a character's mythic keystone season details."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}"
            f"/mythic-keystone-profile/season/{season_id}",
        )

    # ------------------------------------------------------------------
    # Character Professions / PvP / Quests / Reputations / Soulbinds /
    # Specializations / Statistics / Titles
    # ------------------------------------------------------------------

    def get_character_professions_summary(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's professions summary."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}/professions",
        )

    async def get_character_professions_summary_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's professions summary."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}/professions",
        )

    def get_character_pvp_bracket_statistics(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
        pvp_bracket: str,
    ) -> ApiResponse:
        """Get a character's PvP bracket statistics."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}"
            f"/pvp-bracket/{pvp_bracket}",
        )

    async def get_character_pvp_bracket_statistics_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
        pvp_bracket: str,
    ) -> ApiResponse:
        """Get a character's PvP bracket statistics."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}"
            f"/pvp-bracket/{pvp_bracket}",
        )

    def get_character_pvp_summary(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's PvP summary."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}/pvp-summary",
        )

    async def get_character_pvp_summary_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's PvP summary."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}/pvp-summary",
        )

    def get_character_quests(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's quests."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}/quests",
        )

    async def get_character_quests_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's quests."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}/quests",
        )

    def get_character_completed_quests(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's completed quests."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}"
            "/quests/completed",
        )

    async def get_character_completed_quests_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's completed quests."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}"
            "/quests/completed",
        )

    def get_character_reputations_summary(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's reputations summary."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}/reputations",
        )

    async def get_character_reputations_summary_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's reputations summary."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}/reputations",
        )

    def get_character_soulbinds(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's soulbinds."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}/soulbinds",
        )

    async def get_character_soulbinds_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's soulbinds."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}/soulbinds",
        )

    def get_character_specializations_summary(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's specializations summary."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}"
            "/specializations",
        )

    async def get_character_specializations_summary_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's specializations summary."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}"
            "/specializations",
        )

    def get_character_statistics_summary(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's statistics summary."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}/statistics",
        )

    async def get_character_statistics_summary_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's statistics summary."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}/statistics",
        )

    def get_character_titles_summary(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's titles summary."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}/titles",
        )

    async def get_character_titles_summary_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
    ) -> ApiResponse:
        """Get a character's titles summary."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}/titles",
        )

    # ------------------------------------------------------------------
    # Character House — new in Midnight
    # ------------------------------------------------------------------

    def get_character_house(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
        house_number: int,
    ) -> ApiResponse:
        """Get a character's house by house number (new in Midnight)."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}"
            f"/house/house-{house_number}",
        )

    async def get_character_house_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        character_name: str,
        house_number: int,
    ) -> ApiResponse:
        """Get a character's house by house number (new in Midnight)."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}"
            f"/house/house-{house_number}",
        )

    # ------------------------------------------------------------------
    # Guild (/data/wow/guild/ — profile namespace)
    # ------------------------------------------------------------------

    def get_guild(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        name_slug: str,
    ) -> ApiResponse:
        """Get a guild by realm and name slugs."""
        return self._profile_get(
            region, locale, f"/data/wow/guild/{realm_slug.lower()}/{name_slug.lower()}"
        )

    async def get_guild_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        name_slug: str,
    ) -> ApiResponse:
        """Get a guild by realm and name slugs."""
        return await self._profile_get_async(
            region, locale, f"/data/wow/guild/{realm_slug.lower()}/{name_slug.lower()}"
        )

    def get_guild_activity(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        name_slug: str,
    ) -> ApiResponse:
        """Get guild activity."""
        return self._profile_get(
            region,
            locale,
            f"/data/wow/guild/{realm_slug.lower()}/{name_slug.lower()}/activity",
        )

    async def get_guild_activity_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        name_slug: str,
    ) -> ApiResponse:
        """Get guild activity."""
        return await self._profile_get_async(
            region,
            locale,
            f"/data/wow/guild/{realm_slug.lower()}/{name_slug.lower()}/activity",
        )

    def get_guild_achievements(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        name_slug: str,
    ) -> ApiResponse:
        """Get guild achievements."""
        return self._profile_get(
            region,
            locale,
            f"/data/wow/guild/{realm_slug.lower()}/{name_slug.lower()}/achievements",
        )

    async def get_guild_achievements_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        name_slug: str,
    ) -> ApiResponse:
        """Get guild achievements."""
        return await self._profile_get_async(
            region,
            locale,
            f"/data/wow/guild/{realm_slug.lower()}/{name_slug.lower()}/achievements",
        )

    def get_guild_roster(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        name_slug: str,
    ) -> ApiResponse:
        """Get guild roster."""
        return self._profile_get(
            region,
            locale,
            f"/data/wow/guild/{realm_slug.lower()}/{name_slug.lower()}/roster",
        )

    async def get_guild_roster_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        realm_slug: str,
        name_slug: str,
    ) -> ApiResponse:
        """Get guild roster."""
        return await self._profile_get_async(
            region,
            locale,
            f"/data/wow/guild/{realm_slug.lower()}/{name_slug.lower()}/roster",
        )


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
    r = region.value if isinstance(region, Region) else region
    l = locale.value if isinstance(locale, Locale) else locale
    return r, {"namespace": f"{namespace_type}-{r}", "locale": l, **extra}
