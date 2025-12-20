"""Tests for exception hierarchy."""

import pytest

from blizzardapi3.exceptions import (
    BadRequestError,
    BlizzardAPIError,
    ForbiddenError,
    InvalidLocaleError,
    InvalidRegionError,
    MissingParameterError,
    NotFoundError,
    RateLimitError,
    ServerError,
    TokenError,
)


def test_base_exception():
    """Test base BlizzardAPIError."""
    error = BlizzardAPIError("Test error", status_code=500, request_url="https://example.com")
    assert str(error) == "BlizzardAPIError: Test error | Status: 500 | URL: https://example.com"
    assert error.message == "Test error"
    assert error.status_code == 500


def test_not_found_error():
    """Test NotFoundError."""
    error = NotFoundError("Resource not found", status_code=404, request_url="https://example.com/achievement/999")
    assert isinstance(error, BlizzardAPIError)
    assert error.status_code == 404


def test_rate_limit_error():
    """Test RateLimitError with retry_after."""
    error = RateLimitError("Rate limited", status_code=429, retry_after=60)
    assert "Retry after 60 seconds" in str(error)
    assert error.is_rate_limited is True
    assert error.should_retry is True


def test_server_error():
    """Test ServerError."""
    error = ServerError("Internal server error", status_code=500)
    assert error.should_retry is True


def test_token_error():
    """Test TokenError."""
    error = TokenError("Invalid token", token_type="bearer", expires_in=3600)
    assert "Token Type: bearer" in str(error)


def test_validation_error_with_field():
    """Test ValidationError with field information."""
    error = MissingParameterError(
        "Missing region", field="region", required_params=["region", "locale", "achievement_id"]
    )
    assert "region" in str(error)
    assert "Required:" in str(error)


def test_invalid_region_error():
    """Test InvalidRegionError."""
    error = InvalidRegionError("Invalid region", field="region", invalid_value="usa", valid_regions=["us", "eu", "kr"])
    assert "us, eu, kr" in str(error)


def test_invalid_locale_error():
    """Test InvalidLocaleError."""
    error = InvalidLocaleError(
        "Invalid locale", field="locale", invalid_value="en-US", valid_locales=["en_US", "es_MX"]
    )
    assert "en_US, es_MX" in str(error)


def test_request_error_retry_logic():
    """Test RequestError retry logic."""
    # Rate limit should retry
    rate_limit = RateLimitError("Rate limited", status_code=429)
    assert rate_limit.should_retry is True

    # Server errors should retry
    server_error = ServerError("Server error", status_code=503)
    assert server_error.should_retry is True

    # Not found should not retry
    not_found = NotFoundError("Not found", status_code=404)
    assert not_found.should_retry is False

    # Bad request should not retry
    bad_request = BadRequestError("Bad request", status_code=400)
    assert bad_request.should_retry is False
