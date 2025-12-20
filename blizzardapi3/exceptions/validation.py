"""Parameter validation exceptions."""

from dataclasses import dataclass
from typing import Any, Optional

from .base import BlizzardAPIError


@dataclass(slots=True)
class ValidationError(BlizzardAPIError):
    """Base class for validation errors.

    Attributes:
        field: The field that failed validation
        invalid_value: The invalid value that was provided
    """

    field: Optional[str] = None
    invalid_value: Optional[Any] = None

    def __str__(self) -> str:
        """Format validation error message."""
        parts = [f"ValidationError: {self.message}"]

        if self.field:
            parts.append(f"Field: {self.field}")

        if self.invalid_value is not None:
            parts.append(f"Invalid value: {self.invalid_value}")

        return " | ".join(parts)


@dataclass(slots=True)
class InvalidRegionError(ValidationError):
    """Invalid region specified.

    Attributes:
        valid_regions: List of valid region codes
    """

    valid_regions: Optional[list[str]] = None

    def __str__(self) -> str:
        """Format invalid region error."""
        msg = ValidationError.__str__(self)
        if self.valid_regions:
            msg += f" | Valid regions: {', '.join(self.valid_regions)}"
        return msg


@dataclass(slots=True)
class InvalidLocaleError(ValidationError):
    """Invalid locale specified.

    Attributes:
        valid_locales: List of valid locale codes
    """

    valid_locales: Optional[list[str]] = None

    def __str__(self) -> str:
        """Format invalid locale error."""
        msg = ValidationError.__str__(self)
        if self.valid_locales:
            msg += f" | Valid locales: {', '.join(self.valid_locales)}"
        return msg


@dataclass(slots=True)
class MissingParameterError(ValidationError):
    """Required parameter is missing.

    Attributes:
        required_params: List of all required parameters
    """

    required_params: Optional[list[str]] = None

    def __str__(self) -> str:
        """Format missing parameter error."""
        msg = ValidationError.__str__(self)
        if self.required_params:
            msg += f" | Required: {', '.join(self.required_params)}"
        return msg
