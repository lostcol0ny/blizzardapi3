"""World of Warcraft API facade.

Composes the WoW retail sub-APIs and the Classic sub-facades for each
release track. Each sub-API module owns its own endpoint methods
directly, so there's no dynamic binding and no stubs to keep in sync.
"""

from __future__ import annotations

from ..core.client import BaseClient
from ..core.executor import RequestExecutor
from ..types import ClassicTrack
from .wow_classic import WowClassic
from .wow_game_data import WowGameData
from .wow_profile import WowProfile


class WowAPI:
    """Access point for WoW retail and Classic APIs.

    Retail::

        api.wow.game_data.get_achievement(...)
        api.wow.profile.get_character_profile_summary(...)

    Classic (per-track sub-facade; default is Progression / MoP Classic)::

        api.wow.classic.game_data.get_achievement(...)
        api.wow.classic_era.game_data.get_achievement(...)  # Era / Classic 1x
    """

    def __init__(self, client: BaseClient, executor: RequestExecutor):
        self.game_data = WowGameData(client, executor)
        self.profile = WowProfile(client, executor)
        self.classic = WowClassic(client, executor, track=ClassicTrack.progression)
        self.classic_era = WowClassic(client, executor, track=ClassicTrack.era)
