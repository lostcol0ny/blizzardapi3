"""Integration tests for BlizzardAPI."""

from unittest.mock import MagicMock, patch

import pytest

from blizzardapi3 import BlizzardAPI, Locale, Region


def test_api_initialization(mock_credentials):
    """Test API client initialization."""
    api = BlizzardAPI(**mock_credentials)
    assert api.client_id == "test_client_id"
    assert api.client_secret == "test_client_secret"
    assert api.default_region == Region.US
    assert api.default_locale == Locale.EN_US


def test_api_context_manager(mock_credentials):
    """Test API context manager."""
    with BlizzardAPI(**mock_credentials) as api:
        assert api is not None
    # Session should be closed after context


def test_wow_api_exists(api_client):
    """Test WoW API is accessible."""
    assert hasattr(api_client, "wow")
    assert hasattr(api_client.wow, "game_data")


def test_generated_methods_exist(api_client):
    """Test that methods are generated from config."""
    # Check sync methods
    assert hasattr(api_client.wow.game_data, "get_achievement")
    assert hasattr(api_client.wow.game_data, "get_decor")
    assert hasattr(api_client.wow.game_data, "search_decor")

    # Check async methods
    assert hasattr(api_client.wow.game_data, "get_achievement_async")
    assert hasattr(api_client.wow.game_data, "get_decor_async")
    assert hasattr(api_client.wow.game_data, "search_decor_async")


def test_method_has_docstring(api_client):
    """Test generated methods have docstrings."""
    method = api_client.wow.game_data.get_achievement
    assert method.__doc__ is not None
    assert "Get an achievement by ID" in method.__doc__
    assert "region" in method.__doc__
    assert "locale" in method.__doc__


@patch("requests.Session.post")
@patch("requests.Session.get")
def test_sync_api_call(mock_get, mock_post, api_client, mock_token_response, mock_achievement_response):
    """Test synchronous API call."""
    # Mock token fetch
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = mock_token_response

    # Mock API response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_achievement_response
    mock_get.return_value.headers = {"Content-Type": "application/json"}

    with api_client:
        result = api_client.wow.game_data.get_achievement(region="us", locale="en_US", achievement_id=6)

    assert result["id"] == 6
    assert result["name"]["en_US"] == "Level 10"
    mock_post.assert_called_once()  # Token fetch
    mock_get.assert_called_once()  # API call


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.post")
@patch("aiohttp.ClientSession.get")
async def test_async_api_call(mock_get, mock_post, api_client, mock_token_response, mock_achievement_response):
    """Test asynchronous API call."""
    # Mock token fetch
    mock_post_ctx = MagicMock()
    mock_post_ctx.__aenter__.return_value.status = 200
    mock_post_ctx.__aenter__.return_value.json.return_value = mock_token_response
    mock_post.return_value = mock_post_ctx

    # Mock API response
    mock_get_ctx = MagicMock()
    mock_get_ctx.__aenter__.return_value.status = 200
    mock_get_ctx.__aenter__.return_value.json.return_value = mock_achievement_response
    mock_get_ctx.__aenter__.return_value.headers = {"Content-Type": "application/json"}
    mock_get.return_value = mock_get_ctx

    async with api_client:
        result = await api_client.wow.game_data.get_achievement_async(region="us", locale="en_US", achievement_id=6)

    assert result["id"] == 6
    assert result["name"]["en_US"] == "Level 10"


@patch("requests.Session.post")
@patch("requests.Session.get")
def test_search_method(mock_get, mock_post, api_client, mock_token_response, mock_search_response):
    """Test search method with kwargs."""
    # Mock token fetch
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = mock_token_response

    # Mock search response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_search_response

    with api_client:
        result = api_client.wow.game_data.search_decor(
            region="us", locale="en_US", name_en_US="Fireplace", orderby="id", _page=1
        )

    assert "results" in result
    assert len(result["results"]) > 0
    assert result["page"] == 1


def test_missing_parameter_raises_error(api_client):
    """Test that missing required parameter raises error."""
    from blizzardapi3.exceptions import MissingParameterError

    with api_client:
        with pytest.raises(MissingParameterError):
            # Missing achievement_id
            api_client.wow.game_data.get_achievement(region="us", locale="en_US")
