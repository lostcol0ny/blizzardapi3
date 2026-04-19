"""Diablo 3 API — direct endpoint methods.

D3 has no namespace concept; every endpoint is just region + locale +
optional path params. The former split between ``D3GameDataAPI`` and
``D3CommunityAPI`` is collapsed here because Blizzard's docs had several
endpoints categorized inconsistently — a single class makes every
endpoint reachable without guessing which half it lives in.
"""

from __future__ import annotations

from typing import Any

from ..core.client import BaseClient
from ..core.executor import ApiResponse, RequestExecutor
from ..types import Locale, Region


class D3API:
    """Diablo 3 endpoints (profile, game data, leaderboards)."""

    def __init__(self, client: BaseClient, executor: RequestExecutor):
        self._client = client
        self._executor = executor

    # ------------------------------------------------------------------
    # Shared helpers — no namespace, just locale
    # ------------------------------------------------------------------

    def _get(self, region: Region | str, locale: Locale | str, path: str, **extra: Any) -> ApiResponse:
        r = region.value if isinstance(region, Region) else region
        loc = locale.value if isinstance(locale, Locale) else locale
        params: dict[str, Any] = {"locale": loc, **extra}
        return self._executor.execute(region=r, path=path, params=params, client=self._client.sync_client)

    async def _get_async(self, region: Region | str, locale: Locale | str, path: str, **extra: Any) -> ApiResponse:
        r = region.value if isinstance(region, Region) else region
        loc = locale.value if isinstance(locale, Locale) else locale
        params: dict[str, Any] = {"locale": loc, **extra}
        return await self._executor.execute_async(region=r, path=path, params=params, client=self._client.async_client)

    # ------------------------------------------------------------------
    # Profile (BattleTag is ``Name#1234`` — pass with the ``#``)
    # ------------------------------------------------------------------

    def get_account(self, *, region: Region | str, locale: Locale | str, battletag: str) -> ApiResponse:
        """Get a D3 account profile by BattleTag (``Name#1234``)."""
        return self._get(region, locale, f"/d3/profile/{battletag}/")

    async def get_account_async(self, *, region: Region | str, locale: Locale | str, battletag: str) -> ApiResponse:
        """Get a D3 account profile by BattleTag (``Name#1234``)."""
        return await self._get_async(region, locale, f"/d3/profile/{battletag}/")

    def get_hero(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        battletag: str,
        hero_id: int,
    ) -> ApiResponse:
        """Get a hero by BattleTag and hero ID."""
        return self._get(region, locale, f"/d3/profile/{battletag}/hero/{hero_id}")

    async def get_hero_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        battletag: str,
        hero_id: int,
    ) -> ApiResponse:
        """Get a hero by BattleTag and hero ID."""
        return await self._get_async(region, locale, f"/d3/profile/{battletag}/hero/{hero_id}")

    def get_hero_items(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        battletag: str,
        hero_id: int,
    ) -> ApiResponse:
        """Get items for a hero."""
        return self._get(region, locale, f"/d3/profile/{battletag}/hero/{hero_id}/items")

    async def get_hero_items_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        battletag: str,
        hero_id: int,
    ) -> ApiResponse:
        """Get items for a hero."""
        return await self._get_async(region, locale, f"/d3/profile/{battletag}/hero/{hero_id}/items")

    def get_hero_follower_items(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        battletag: str,
        hero_id: int,
    ) -> ApiResponse:
        """Get follower items for a hero."""
        return self._get(region, locale, f"/d3/profile/{battletag}/hero/{hero_id}/follower-items")

    async def get_hero_follower_items_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        battletag: str,
        hero_id: int,
    ) -> ApiResponse:
        """Get follower items for a hero."""
        return await self._get_async(region, locale, f"/d3/profile/{battletag}/hero/{hero_id}/follower-items")

    # ------------------------------------------------------------------
    # Act
    # ------------------------------------------------------------------

    def get_act_index(self, *, region: Region | str, locale: Locale | str) -> ApiResponse:
        """Get an index of D3 acts."""
        return self._get(region, locale, "/d3/data/act")

    async def get_act_index_async(self, *, region: Region | str, locale: Locale | str) -> ApiResponse:
        """Get an index of D3 acts."""
        return await self._get_async(region, locale, "/d3/data/act")

    def get_act(self, *, region: Region | str, locale: Locale | str, act_id: int) -> ApiResponse:
        """Get a D3 act by ID."""
        return self._get(region, locale, f"/d3/data/act/{act_id}")

    async def get_act_async(self, *, region: Region | str, locale: Locale | str, act_id: int) -> ApiResponse:
        """Get a D3 act by ID."""
        return await self._get_async(region, locale, f"/d3/data/act/{act_id}")

    # ------------------------------------------------------------------
    # Artisan / Recipe / Follower
    # ------------------------------------------------------------------

    def get_artisan(self, *, region: Region | str, locale: Locale | str, artisan_slug: str) -> ApiResponse:
        """Get a D3 artisan by slug."""
        return self._get(region, locale, f"/d3/data/artisan/{artisan_slug}")

    async def get_artisan_async(self, *, region: Region | str, locale: Locale | str, artisan_slug: str) -> ApiResponse:
        """Get a D3 artisan by slug."""
        return await self._get_async(region, locale, f"/d3/data/artisan/{artisan_slug}")

    def get_recipe(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        artisan_slug: str,
        recipe_slug: str,
    ) -> ApiResponse:
        """Get a D3 recipe for an artisan."""
        return self._get(region, locale, f"/d3/data/artisan/{artisan_slug}/recipe/{recipe_slug}")

    async def get_recipe_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        artisan_slug: str,
        recipe_slug: str,
    ) -> ApiResponse:
        """Get a D3 recipe for an artisan."""
        return await self._get_async(region, locale, f"/d3/data/artisan/{artisan_slug}/recipe/{recipe_slug}")

    def get_follower(self, *, region: Region | str, locale: Locale | str, follower_slug: str) -> ApiResponse:
        """Get a D3 follower by slug."""
        return self._get(region, locale, f"/d3/data/follower/{follower_slug}")

    async def get_follower_async(
        self, *, region: Region | str, locale: Locale | str, follower_slug: str
    ) -> ApiResponse:
        """Get a D3 follower by slug."""
        return await self._get_async(region, locale, f"/d3/data/follower/{follower_slug}")

    # ------------------------------------------------------------------
    # Character Class / Skill
    # ------------------------------------------------------------------

    def get_character_class(self, *, region: Region | str, locale: Locale | str, class_slug: str) -> ApiResponse:
        """Get a D3 character class by slug."""
        return self._get(region, locale, f"/d3/data/hero/{class_slug}")

    async def get_character_class_async(
        self, *, region: Region | str, locale: Locale | str, class_slug: str
    ) -> ApiResponse:
        """Get a D3 character class by slug."""
        return await self._get_async(region, locale, f"/d3/data/hero/{class_slug}")

    def get_api_skill(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        class_slug: str,
        skill_slug: str,
    ) -> ApiResponse:
        """Get a skill for a D3 character class."""
        return self._get(region, locale, f"/d3/data/hero/{class_slug}/skill/{skill_slug}")

    async def get_api_skill_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        class_slug: str,
        skill_slug: str,
    ) -> ApiResponse:
        """Get a skill for a D3 character class."""
        return await self._get_async(region, locale, f"/d3/data/hero/{class_slug}/skill/{skill_slug}")

    # ------------------------------------------------------------------
    # Item / Item Type
    # ------------------------------------------------------------------

    def get_item_type_index(self, *, region: Region | str, locale: Locale | str) -> ApiResponse:
        """Get an index of D3 item types."""
        return self._get(region, locale, "/d3/data/item-type")

    async def get_item_type_index_async(self, *, region: Region | str, locale: Locale | str) -> ApiResponse:
        """Get an index of D3 item types."""
        return await self._get_async(region, locale, "/d3/data/item-type")

    def get_item_type(self, *, region: Region | str, locale: Locale | str, item_type_slug: str) -> ApiResponse:
        """Get a D3 item type by slug."""
        return self._get(region, locale, f"/d3/data/item-type/{item_type_slug}")

    async def get_item_type_async(
        self, *, region: Region | str, locale: Locale | str, item_type_slug: str
    ) -> ApiResponse:
        """Get a D3 item type by slug."""
        return await self._get_async(region, locale, f"/d3/data/item-type/{item_type_slug}")

    def get_item(self, *, region: Region | str, locale: Locale | str, item_slug_and_id: str) -> ApiResponse:
        """Get a D3 item by combined slug and ID (``slug-12345``)."""
        return self._get(region, locale, f"/d3/data/item/{item_slug_and_id}")

    async def get_item_async(self, *, region: Region | str, locale: Locale | str, item_slug_and_id: str) -> ApiResponse:
        """Get a D3 item by combined slug and ID (``slug-12345``)."""
        return await self._get_async(region, locale, f"/d3/data/item/{item_slug_and_id}")

    # ------------------------------------------------------------------
    # Season / Era leaderboards
    # ------------------------------------------------------------------

    def get_season_index(self, *, region: Region | str, locale: Locale | str) -> ApiResponse:
        """Get an index of D3 seasons."""
        return self._get(region, locale, "/data/d3/season/")

    async def get_season_index_async(self, *, region: Region | str, locale: Locale | str) -> ApiResponse:
        """Get an index of D3 seasons."""
        return await self._get_async(region, locale, "/data/d3/season/")

    def get_season(self, *, region: Region | str, locale: Locale | str, season_id: int) -> ApiResponse:
        """Get a D3 season by ID."""
        return self._get(region, locale, f"/data/d3/season/{season_id}")

    async def get_season_async(self, *, region: Region | str, locale: Locale | str, season_id: int) -> ApiResponse:
        """Get a D3 season by ID."""
        return await self._get_async(region, locale, f"/data/d3/season/{season_id}")

    def get_season_leaderboard(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        season_id: int,
        leaderboard: str,
    ) -> ApiResponse:
        """Get a D3 season leaderboard."""
        return self._get(region, locale, f"/data/d3/season/{season_id}/leaderboard/{leaderboard}")

    async def get_season_leaderboard_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        season_id: int,
        leaderboard: str,
    ) -> ApiResponse:
        """Get a D3 season leaderboard."""
        return await self._get_async(region, locale, f"/data/d3/season/{season_id}/leaderboard/{leaderboard}")

    def get_era_index(self, *, region: Region | str, locale: Locale | str) -> ApiResponse:
        """Get an index of D3 eras."""
        return self._get(region, locale, "/data/d3/era/")

    async def get_era_index_async(self, *, region: Region | str, locale: Locale | str) -> ApiResponse:
        """Get an index of D3 eras."""
        return await self._get_async(region, locale, "/data/d3/era/")

    def get_era(self, *, region: Region | str, locale: Locale | str, era_id: int) -> ApiResponse:
        """Get a D3 era by ID."""
        return self._get(region, locale, f"/data/d3/era/{era_id}")

    async def get_era_async(self, *, region: Region | str, locale: Locale | str, era_id: int) -> ApiResponse:
        """Get a D3 era by ID."""
        return await self._get_async(region, locale, f"/data/d3/era/{era_id}")

    def get_era_leaderboard(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        era_id: int,
        leaderboard: str,
    ) -> ApiResponse:
        """Get a D3 era leaderboard."""
        return self._get(region, locale, f"/data/d3/era/{era_id}/leaderboard/{leaderboard}")

    async def get_era_leaderboard_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        era_id: int,
        leaderboard: str,
    ) -> ApiResponse:
        """Get a D3 era leaderboard."""
        return await self._get_async(region, locale, f"/data/d3/era/{era_id}/leaderboard/{leaderboard}")
