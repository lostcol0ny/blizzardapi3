"""Game-specific API facades."""

from .d3 import D3API
from .hearthstone import HearthstoneAPI
from .sc2 import SC2API
from .wow import WowAPI
from .wow_classic import WowClassic
from .wow_game_data import WowGameData
from .wow_profile import WowProfile

__all__ = [
    "D3API",
    "HearthstoneAPI",
    "SC2API",
    "WowAPI",
    "WowClassic",
    "WowGameData",
    "WowProfile",
]
