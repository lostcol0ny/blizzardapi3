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
from .core.cache import ResponseCache
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
        cache: bool = True,
        cache_ttl: int | None = None,
        max_retries: int = 2,
    ):
        """Construct the API facade.

        ``cache`` (default on) enables a response cache that honors Blizzard's
        ``Cache-Control`` headers — static game data (``max-age=86400``) is
        served from memory until it expires; profile data, which sends no
        cache directive, is not cached. Set ``cache=False`` to disable.

        ``cache_ttl`` caches responses that carry *no* ``Cache-Control`` (e.g.
        character profiles) for that many seconds — a deliberate
        staleness-for-speed trade you opt into. An explicit ``no-store`` /
        ``private`` from the server is always honored regardless.

        ``max_retries`` bounds automatic retries on transient failures (HTTP
        429 and 5xx), honoring ``Retry-After`` and otherwise backing off with
        full jitter. Set to ``0`` to disable and surface the error immediately.
        """
        super().__init__(client_id, client_secret, region=region, locale=locale)
        self.cache = ResponseCache(default_ttl=cache_ttl) if cache else None
        executor = RequestExecutor(self.token_manager, cache=self.cache, max_retries=max_retries)

        self.wow = WowAPI(self, executor)
        self.d3 = D3API(self, executor)
        self.sc2 = SC2API(self, executor)
        self.hearthstone = HearthstoneAPI(self, executor)
