"""World of Warcraft Classic API — direct endpoint methods.

Classic is separated from retail because:
  1. Every Classic endpoint uses a different namespace token
     (``static-classic1x-us``, ``dynamic-classic-eu``, etc.), driven by the
     ``ClassicTrack`` the user is querying.
  2. Several Classic-only endpoints don't exist on retail (multi-house
     auctions, the ``pvp-region`` hierarchy).
  3. Burying this behind an ``is_classic: bool = False`` flag on every
     retail method — which is what the v3.0 factory did — silently produced
     the wrong namespace token for Era/Anniversary and made the Classic
     surface unreachable in practice. A dedicated class makes Classic
     callable and keeps the retail methods simpler.

Usage:
    classic = WowClassic(client, executor, track=ClassicTrack.era)
    data = classic.game_data.get_achievement(region="us", locale="en_US", achievement_id=1)
"""

from __future__ import annotations

from typing import Any

from draft.core.client import BaseClient
from draft.core.executor import ApiResponse, RequestExecutor
from blizzardapi3.types import ClassicTrack, Locale, Region


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

    def _static_get(
        self, region: Region | str, locale: Locale | str, path: str, **extra: Any
    ) -> ApiResponse:
        r, params = _normalize(region, locale, "static", self._track, extra)
        return self._executor.execute(region=r, path=path, params=params, client=self._client.sync_client)

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
        return self._executor.execute(region=r, path=path, params=params, client=self._client.sync_client)

    async def _dynamic_get_async(
        self, region: Region | str, locale: Locale | str, path: str, **extra: Any
    ) -> ApiResponse:
        r, params = _normalize(region, locale, "dynamic", self._track, extra)
        return await self._executor.execute_async(
            region=r, path=path, params=params, client=self._client.async_client
        )

    # ------------------------------------------------------------------
    # Shared with retail — shown here to demonstrate the pattern. The
    # production module would mirror ~44 retail endpoints that are also
    # available on Classic, plus the Classic-only endpoints below.
    # ------------------------------------------------------------------

    def get_achievement(
        self, *, region: Region | str, locale: Locale | str, achievement_id: int
    ) -> ApiResponse:
        """Get a Classic achievement by ID."""
        return self._static_get(region, locale, f"/data/wow/achievement/{achievement_id}")

    async def get_achievement_async(
        self, *, region: Region | str, locale: Locale | str, achievement_id: int
    ) -> ApiResponse:
        """Get a Classic achievement by ID."""
        return await self._static_get_async(region, locale, f"/data/wow/achievement/{achievement_id}")

    # ------------------------------------------------------------------
    # Classic-only: multi-house auctions
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
    # Classic-only: pvp-region hierarchy
    # ------------------------------------------------------------------

    def get_pvp_region_index(self, *, region: Region | str, locale: Locale | str) -> ApiResponse:
        """Get the index of Classic PvP regions."""
        return self._dynamic_get(region, locale, "/data/wow/pvp-region/index")

    async def get_pvp_region_index_async(
        self, *, region: Region | str, locale: Locale | str
    ) -> ApiResponse:
        """Get the index of Classic PvP regions."""
        return await self._dynamic_get_async(region, locale, "/data/wow/pvp-region/index")


class WowClassic:
    """Facade for Classic Game Data + Profile on a specific track."""

    def __init__(
        self,
        client: BaseClient,
        executor: RequestExecutor,
        track: ClassicTrack = ClassicTrack.progression,
    ):
        self.game_data = WowClassicGameData(client, executor, track=track)
        # self.profile = WowClassicProfile(client, executor, track=track)  # same shape


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
