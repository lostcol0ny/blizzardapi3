"""Top-level BlizzardAPI facade.

Composes the four game sub-APIs on top of the shared :class:`BaseClient`
(httpx sessions + token manager) and a single :class:`RequestExecutor`
that all sub-APIs share. Use as a context manager to guarantee cleanup
of the underlying httpx sessions::

    with BlizzardAPI(client_id, client_secret) as api:
        achievement = api.wow.game_data.get_achievement(
            region="us", locale="en_US", achievement_id=6
        )

    async with BlizzardAPI(client_id, client_secret) as api:
        achievement = await api.wow.game_data.get_achievement_async(
            region="us", locale="en_US", achievement_id=6
        )
"""

from __future__ import annotations

from .api.d3 import D3API
from .api.hearthstone import HearthstoneAPI
from .api.sc2 import SC2API
from .api.wow import WowAPI
from .core.client import BaseClient
from .core.executor import RequestExecutor


class BlizzardAPI(BaseClient):
    """Entry point for all Blizzard game APIs.

    Inherits session / token management from :class:`BaseClient` and
    composes four sub-APIs: ``wow``, ``d3``, ``sc2``, ``hearthstone``.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        region: str = "us",
        locale: str | None = None,
    ):
        super().__init__(client_id, client_secret, region=region, locale=locale)
        executor = RequestExecutor(self.token_manager)

        self.wow = WowAPI(self, executor)
        self.d3 = D3API(self, executor)
        self.sc2 = SC2API(self, executor)
        self.hearthstone = HearthstoneAPI(self, executor)
