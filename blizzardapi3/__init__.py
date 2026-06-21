"""BlizzardAPI — modern Python wrapper for Blizzard's Battle.net API."""

__version__ = "4.1.0"

from .blizzard_api import BlizzardAPI
from .core.batch import gather_limited
from .core.cache import ResponseCache
from .core.executor import ApiResponse
from .exceptions import (
    AuthenticationError,
    BadRequestError,
    BlizzardAPIError,
    ForbiddenError,
    InvalidCredentialsError,
    InvalidLocaleError,
    InvalidRegionError,
    MissingParameterError,
    NotFoundError,
    RateLimitError,
    RequestError,
    ServerError,
    TokenError,
    TokenExpiredError,
    ValidationError,
)
from .types import ClassicTrack, Locale, Region

__all__ = [
    "__version__",
    # Core
    "BlizzardAPI",
    "ApiResponse",
    "ResponseCache",
    "gather_limited",
    # Types
    "ClassicTrack",
    "Locale",
    "Region",
    # Exceptions
    "AuthenticationError",
    "BadRequestError",
    "BlizzardAPIError",
    "ForbiddenError",
    "InvalidCredentialsError",
    "InvalidLocaleError",
    "InvalidRegionError",
    "MissingParameterError",
    "NotFoundError",
    "RateLimitError",
    "RequestError",
    "ServerError",
    "TokenError",
    "TokenExpiredError",
    "ValidationError",
]
