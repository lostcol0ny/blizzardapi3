"""BlizzardAPI — modern Python wrapper for Blizzard's Battle.net API."""

__version__ = "4.0.4"

from .blizzard_api import BlizzardAPI
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
