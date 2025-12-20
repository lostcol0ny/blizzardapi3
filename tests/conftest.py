"""Pytest configuration and shared fixtures."""

import pytest

from blizzardapi3 import BlizzardAPI


@pytest.fixture
def mock_credentials():
    """Mock API credentials for testing."""
    return {"client_id": "test_client_id", "client_secret": "test_client_secret"}


@pytest.fixture
def api_client(mock_credentials):
    """Create API client for testing."""
    return BlizzardAPI(**mock_credentials)


@pytest.fixture
def mock_token_response():
    """Mock OAuth token response."""
    return {"access_token": "test_token_12345", "token_type": "bearer", "expires_in": 86400}


@pytest.fixture
def mock_achievement_response():
    """Mock achievement API response."""
    return {
        "_links": {"self": {"href": "https://us.api.blizzard.com/data/wow/achievement/6"}},
        "id": 6,
        "category": {"key": {"href": "..."}, "name": "Quests", "id": 96},
        "name": {"en_US": "Level 10", "es_MX": "Nivel 10"},
        "description": {"en_US": "Reach level 10.", "es_MX": "Alcanza el nivel 10."},
        "points": 10,
        "is_account_wide": True,
        "criteria": {"id": 5, "description": "Reach level 10.", "amount": 10},
        "media": {"key": {"href": "..."}, "id": 6},
        "display_order": 1,
    }


@pytest.fixture
def mock_search_response():
    """Mock search API response."""
    return {
        "_links": {"self": {"href": "https://us.api.blizzard.com/data/wow/search/decor"}},
        "results": [
            {
                "key": {"href": "https://us.api.blizzard.com/data/wow/decor/80"},
                "data": {
                    "name": {"en_US": "Ornate Stonework Fireplace"},
                    "id": 80,
                    "item": {"name": {"en_US": "Ornate Stonework Fireplace"}, "id": 235994},
                },
            }
        ],
        "page": 1,
        "pageSize": 100,
        "maxPageSize": 100,
        "pageCount": 1,
    }
