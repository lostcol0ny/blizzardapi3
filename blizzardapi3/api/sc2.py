"""StarCraft 2 API — direct endpoint methods.

SC2 has no namespace concept; every endpoint is just region + locale +
optional path params. The ``game_data`` half of the old split held a
single endpoint (league data), so keeping two modules was pure
overhead — everything lives in one ``SC2API`` class.
"""

from __future__ import annotations

from typing import Any

from ..core.client import BaseClient
from ..core.executor import ApiResponse, RequestExecutor
from ..types import Locale, Region


class SC2API:
    """StarCraft 2 endpoints (profile, ladder, league, legacy)."""

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
    # Profile API
    # ------------------------------------------------------------------

    def get_static_profile(
        self, *, region: Region | str, locale: Locale | str, region_id: int
    ) -> ApiResponse:
        """Get static profile data for a StarCraft 2 region."""
        return self._get(region, locale, f"/sc2/static/profile/{region_id}")

    async def get_static_profile_async(
        self, *, region: Region | str, locale: Locale | str, region_id: int
    ) -> ApiResponse:
        """Get static profile data for a StarCraft 2 region."""
        return await self._get_async(region, locale, f"/sc2/static/profile/{region_id}")

    def get_metadata_profile(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        region_id: int,
        realm_id: int,
        profile_id: int,
    ) -> ApiResponse:
        """Get metadata for a StarCraft 2 profile."""
        return self._get(
            region,
            locale,
            f"/sc2/metadata/profile/{region_id}/{realm_id}/{profile_id}",
        )

    async def get_metadata_profile_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        region_id: int,
        realm_id: int,
        profile_id: int,
    ) -> ApiResponse:
        """Get metadata for a StarCraft 2 profile."""
        return await self._get_async(
            region,
            locale,
            f"/sc2/metadata/profile/{region_id}/{realm_id}/{profile_id}",
        )

    def get_profile(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        region_id: int,
        realm_id: int,
        profile_id: int,
    ) -> ApiResponse:
        """Get a StarCraft 2 profile."""
        return self._get(
            region, locale, f"/sc2/profile/{region_id}/{realm_id}/{profile_id}"
        )

    async def get_profile_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        region_id: int,
        realm_id: int,
        profile_id: int,
    ) -> ApiResponse:
        """Get a StarCraft 2 profile."""
        return await self._get_async(
            region, locale, f"/sc2/profile/{region_id}/{realm_id}/{profile_id}"
        )

    def get_profile_ladder_summary(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        region_id: int,
        realm_id: int,
        profile_id: int,
    ) -> ApiResponse:
        """Get ladder summary for a StarCraft 2 profile."""
        return self._get(
            region,
            locale,
            f"/sc2/profile/{region_id}/{realm_id}/{profile_id}/ladder/summary",
        )

    async def get_profile_ladder_summary_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        region_id: int,
        realm_id: int,
        profile_id: int,
    ) -> ApiResponse:
        """Get ladder summary for a StarCraft 2 profile."""
        return await self._get_async(
            region,
            locale,
            f"/sc2/profile/{region_id}/{realm_id}/{profile_id}/ladder/summary",
        )

    def get_profile_ladder(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        region_id: int,
        realm_id: int,
        profile_id: int,
        ladder_id: int,
    ) -> ApiResponse:
        """Get a ladder for a StarCraft 2 profile."""
        return self._get(
            region,
            locale,
            f"/sc2/profile/{region_id}/{realm_id}/{profile_id}/ladder/{ladder_id}",
        )

    async def get_profile_ladder_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        region_id: int,
        realm_id: int,
        profile_id: int,
        ladder_id: int,
    ) -> ApiResponse:
        """Get a ladder for a StarCraft 2 profile."""
        return await self._get_async(
            region,
            locale,
            f"/sc2/profile/{region_id}/{realm_id}/{profile_id}/ladder/{ladder_id}",
        )

    # ------------------------------------------------------------------
    # Ladder API
    # ------------------------------------------------------------------

    def get_grandmaster_leaderboard(
        self, *, region: Region | str, locale: Locale | str, region_id: int
    ) -> ApiResponse:
        """Get grandmaster leaderboard for a region."""
        return self._get(region, locale, f"/sc2/ladder/grandmaster/{region_id}")

    async def get_grandmaster_leaderboard_async(
        self, *, region: Region | str, locale: Locale | str, region_id: int
    ) -> ApiResponse:
        """Get grandmaster leaderboard for a region."""
        return await self._get_async(
            region, locale, f"/sc2/ladder/grandmaster/{region_id}"
        )

    def get_season(
        self, *, region: Region | str, locale: Locale | str, region_id: int
    ) -> ApiResponse:
        """Get current ladder season data for a region."""
        return self._get(region, locale, f"/sc2/ladder/season/{region_id}")

    async def get_season_async(
        self, *, region: Region | str, locale: Locale | str, region_id: int
    ) -> ApiResponse:
        """Get current ladder season data for a region."""
        return await self._get_async(region, locale, f"/sc2/ladder/season/{region_id}")

    # ------------------------------------------------------------------
    # Account / Player API
    # ------------------------------------------------------------------

    def get_player(
        self, *, region: Region | str, locale: Locale | str, account_id: int
    ) -> ApiResponse:
        """Get a StarCraft 2 player by account ID."""
        return self._get(region, locale, f"/sc2/player/{account_id}")

    async def get_player_async(
        self, *, region: Region | str, locale: Locale | str, account_id: int
    ) -> ApiResponse:
        """Get a StarCraft 2 player by account ID."""
        return await self._get_async(region, locale, f"/sc2/player/{account_id}")

    # ------------------------------------------------------------------
    # Legacy API
    # ------------------------------------------------------------------

    def get_legacy_profile(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        region_id: int,
        realm_id: int,
        profile_id: int,
    ) -> ApiResponse:
        """Get legacy profile data."""
        return self._get(
            region,
            locale,
            f"/sc2/legacy/profile/{region_id}/{realm_id}/{profile_id}",
        )

    async def get_legacy_profile_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        region_id: int,
        realm_id: int,
        profile_id: int,
    ) -> ApiResponse:
        """Get legacy profile data."""
        return await self._get_async(
            region,
            locale,
            f"/sc2/legacy/profile/{region_id}/{realm_id}/{profile_id}",
        )

    def get_legacy_profile_ladders(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        region_id: int,
        realm_id: int,
        profile_id: int,
    ) -> ApiResponse:
        """Get legacy profile ladder data."""
        return self._get(
            region,
            locale,
            f"/sc2/legacy/profile/{region_id}/{realm_id}/{profile_id}/ladders",
        )

    async def get_legacy_profile_ladders_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        region_id: int,
        realm_id: int,
        profile_id: int,
    ) -> ApiResponse:
        """Get legacy profile ladder data."""
        return await self._get_async(
            region,
            locale,
            f"/sc2/legacy/profile/{region_id}/{realm_id}/{profile_id}/ladders",
        )

    def get_legacy_profile_matches(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        region_id: int,
        realm_id: int,
        profile_id: int,
    ) -> ApiResponse:
        """Get legacy profile match history."""
        return self._get(
            region,
            locale,
            f"/sc2/legacy/profile/{region_id}/{realm_id}/{profile_id}/matches",
        )

    async def get_legacy_profile_matches_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        region_id: int,
        realm_id: int,
        profile_id: int,
    ) -> ApiResponse:
        """Get legacy profile match history."""
        return await self._get_async(
            region,
            locale,
            f"/sc2/legacy/profile/{region_id}/{realm_id}/{profile_id}/matches",
        )

    def get_legacy_ladder(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        region_id: int,
        ladder_id: int,
    ) -> ApiResponse:
        """Get legacy ladder data."""
        return self._get(
            region, locale, f"/sc2/legacy/ladder/{region_id}/{ladder_id}"
        )

    async def get_legacy_ladder_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        region_id: int,
        ladder_id: int,
    ) -> ApiResponse:
        """Get legacy ladder data."""
        return await self._get_async(
            region, locale, f"/sc2/legacy/ladder/{region_id}/{ladder_id}"
        )

    def get_legacy_achievements(
        self, *, region: Region | str, locale: Locale | str, region_id: int
    ) -> ApiResponse:
        """Get legacy achievements data."""
        return self._get(region, locale, f"/sc2/legacy/data/achievements/{region_id}")

    async def get_legacy_achievements_async(
        self, *, region: Region | str, locale: Locale | str, region_id: int
    ) -> ApiResponse:
        """Get legacy achievements data."""
        return await self._get_async(
            region, locale, f"/sc2/legacy/data/achievements/{region_id}"
        )

    def get_legacy_rewards(
        self, *, region: Region | str, locale: Locale | str, region_id: int
    ) -> ApiResponse:
        """Get legacy rewards data."""
        return self._get(region, locale, f"/sc2/legacy/data/rewards/{region_id}")

    async def get_legacy_rewards_async(
        self, *, region: Region | str, locale: Locale | str, region_id: int
    ) -> ApiResponse:
        """Get legacy rewards data."""
        return await self._get_async(
            region, locale, f"/sc2/legacy/data/rewards/{region_id}"
        )

    # ------------------------------------------------------------------
    # League API (formerly game_data split — a single endpoint)
    # ------------------------------------------------------------------

    def get_league_data(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        season_id: int,
        queue_id: int,
        team_type: int,
        league_id: int,
    ) -> ApiResponse:
        """Get league data for a specific season, queue, team type, and league."""
        return self._get(
            region,
            locale,
            f"/data/sc2/league/{season_id}/{queue_id}/{team_type}/{league_id}",
        )

    async def get_league_data_async(
        self,
        *,
        region: Region | str,
        locale: Locale | str,
        season_id: int,
        queue_id: int,
        team_type: int,
        league_id: int,
    ) -> ApiResponse:
        """Get league data for a specific season, queue, team type, and league."""
        return await self._get_async(
            region,
            locale,
            f"/data/sc2/league/{season_id}/{queue_id}/{team_type}/{league_id}",
        )
