"""World of Warcraft Profile API — direct endpoint methods.

Covers character-scoped endpoints (public data), account-scoped endpoints
(require user OAuth token), and guild endpoints (public data, path uses
``/data/wow/guild/``).

This draft shows ~8 representative endpoints; the production module would
expose all 31 documented entries.

Classic profile endpoints live in ``wow_classic.py`` — they share most
paths but differ in namespace token and access control.
"""

from __future__ import annotations

from typing import Any

from draft.core.client import BaseClient
from draft.core.executor import ApiResponse, RequestExecutor
from blizzardapi3.types import Locale, Region


class WowProfile:
    """WoW Profile endpoints (retail).

    Character and guild calls use an app-level (client-credentials) token.
    Account calls (methods prefixed ``get_account_*``) additionally require
    a user access_token obtained through the Authorization Code flow;
    callers pass it via ``access_token=...``.
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
        return self._executor.execute(region=r, path=path, params=params, client=self._client.sync_client)

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
    # Character Profile
    # ------------------------------------------------------------------

    def get_character_profile_summary(
        self, *, region: Region | str, locale: Locale | str, realm_slug: str, character_name: str
    ) -> ApiResponse:
        """Get a character profile summary."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}",
        )

    async def get_character_profile_summary_async(
        self, *, region: Region | str, locale: Locale | str, realm_slug: str, character_name: str
    ) -> ApiResponse:
        """Get a character profile summary."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}",
        )

    # ------------------------------------------------------------------
    # Character collections  (new: decor)
    # ------------------------------------------------------------------

    def get_character_decor_collection(
        self, *, region: Region | str, locale: Locale | str, realm_slug: str, character_name: str
    ) -> ApiResponse:
        """Get a character's decor collection (new in Midnight)."""
        return self._profile_get(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}/collections/decor",
        )

    async def get_character_decor_collection_async(
        self, *, region: Region | str, locale: Locale | str, realm_slug: str, character_name: str
    ) -> ApiResponse:
        """Get a character's decor collection (new in Midnight)."""
        return await self._profile_get_async(
            region,
            locale,
            f"/profile/wow/character/{realm_slug.lower()}/{character_name.lower()}/collections/decor",
        )

    # ------------------------------------------------------------------
    # Character house inspection  (new in Midnight)
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
    # Account profile  (requires user access_token)
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

    def get_account_decor_collection(
        self, *, region: Region | str, locale: Locale | str, access_token: str
    ) -> ApiResponse:
        """Get the authenticated account's decor collection."""
        return self._profile_get(
            region, locale, "/profile/user/wow/collections/decor", access_token=access_token
        )

    async def get_account_decor_collection_async(
        self, *, region: Region | str, locale: Locale | str, access_token: str
    ) -> ApiResponse:
        """Get the authenticated account's decor collection."""
        return await self._profile_get_async(
            region, locale, "/profile/user/wow/collections/decor", access_token=access_token
        )

    # ------------------------------------------------------------------
    # Guild  (lives under /data/wow/guild/, dynamic namespace)
    # ------------------------------------------------------------------

    def get_guild(
        self, *, region: Region | str, locale: Locale | str, realm_slug: str, name_slug: str
    ) -> ApiResponse:
        """Get a guild by realm and name slugs."""
        return self._dynamic_get(
            region, locale, f"/data/wow/guild/{realm_slug.lower()}/{name_slug.lower()}"
        )

    async def get_guild_async(
        self, *, region: Region | str, locale: Locale | str, realm_slug: str, name_slug: str
    ) -> ApiResponse:
        """Get a guild by realm and name slugs."""
        return await self._dynamic_get_async(
            region, locale, f"/data/wow/guild/{realm_slug.lower()}/{name_slug.lower()}"
        )


# ----------------------------------------------------------------------
# Module-level helper — shared with wow_game_data via convention, but
# kept local so each endpoint module is self-contained and testable.
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
