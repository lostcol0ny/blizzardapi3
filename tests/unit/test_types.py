"""Tests for type enums."""

import pytest

from blizzardapi3.types import Locale, Region, get_default_locale


def test_region_enum():
    """Test Region enum values."""
    assert Region.US.value == "us"
    assert Region.EU.value == "eu"
    assert Region.KR.value == "kr"
    assert Region.TW.value == "tw"
    assert Region.CN.value == "cn"


def test_region_from_string():
    """Test creating Region from string."""
    region = Region("us")
    assert region == Region.US


def test_locale_enum():
    """Test Locale enum values."""
    assert Locale.EN_US.value == "en_US"
    assert Locale.ES_MX.value == "es_MX"
    assert Locale.FR_FR.value == "fr_FR"


def test_locale_from_string():
    """Test creating Locale from string."""
    locale = Locale("en_US")
    assert locale == Locale.EN_US


def test_get_default_locale():
    """Test getting default locale for regions."""
    assert get_default_locale(Region.US) == Locale.EN_US
    assert get_default_locale(Region.EU) == Locale.EN_GB
    assert get_default_locale(Region.KR) == Locale.KO_KR


def test_get_default_locale_from_string():
    """Test getting default locale from string region."""
    assert get_default_locale("us") == Locale.EN_US
    assert get_default_locale("eu") == Locale.EN_GB


def test_invalid_region_raises_error():
    """Test that invalid region raises ValueError."""
    with pytest.raises(ValueError, match="Invalid region"):
        get_default_locale("invalid")
