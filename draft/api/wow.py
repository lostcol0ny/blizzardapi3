"""World of Warcraft API facade.

Composes the WoW retail and Classic sub-APIs. Each sub-API module owns
its own endpoint methods directly, so there's no dynamic binding, no
setattr loop, and no stubs to keep in sync.
"""

from __future__ import annotations

from draft.api.wow_classic import WowClassic
from draft.api.wow_game_data import WowGameData
from draft.api.wow_profile import WowProfile
from draft.core.client import BaseClient
from draft.core.executor import RequestExecutor
from blizzardapi3.types import ClassicTrack


class WowAPI:
    """Access point for WoW retail and Classic APIs.

    Retail::

        api.wow.game_data.get_achievement(...)
        api.wow.profile.get_character_profile_summary(...)

    Classic (per-track sub-facade; default is Progression / MoP Classic)::

        api.wow.classic.game_data.get_achievement(...)
        api.wow.classic_era.game_data.get_achievement(...)   # Era / Classic 1x
    """

    def __init__(self, client: BaseClient):
        executor = RequestExecutor(client.token_manager)
        self.game_data = WowGameData(client, executor)
        self.profile = WowProfile(client, executor)
        self.classic = WowClassic(client, executor, track=ClassicTrack.progression)
        self.classic_era = WowClassic(client, executor, track=ClassicTrack.era)
