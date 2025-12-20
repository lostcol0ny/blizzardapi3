"""Tests for endpoint registry."""

import pytest

from blizzardapi3.core import EndpointRegistry


def test_registry_initialization():
    """Test registry initializes correctly."""
    registry = EndpointRegistry()
    assert registry is not None
    assert isinstance(registry.configs, dict)


def test_registry_loads_wow_config():
    """Test registry loads WoW config."""
    registry = EndpointRegistry()
    config = registry.get_config("wow", "game_data")
    assert config is not None
    assert config.game == "wow"
    assert config.api_type == "game_data"
    assert config.version == "3.0"


def test_get_endpoints():
    """Test getting endpoints from registry."""
    registry = EndpointRegistry()
    endpoints = registry.get_endpoints("wow", "game_data")
    assert len(endpoints) > 0

    # Check for specific endpoints we defined
    method_names = [e.method_name for e in endpoints]
    assert "get_achievement" in method_names
    assert "get_decor" in method_names
    assert "search_decor" in method_names


def test_resolve_pattern():
    """Test pattern resolution."""
    registry = EndpointRegistry()
    endpoints = registry.get_endpoints("wow", "game_data")

    # Get achievement endpoint
    achievement_endpoint = next(e for e in endpoints if e.method_name == "get_achievement")
    pattern = registry.resolve_pattern("wow", "game_data", achievement_endpoint)

    assert pattern.path_template == "/data/wow/{resource}/{id}"
    assert "region" in pattern.params
    assert "locale" in pattern.params


def test_pattern_templates():
    """Test pattern templates are loaded correctly."""
    registry = EndpointRegistry()
    config = registry.get_config("wow", "game_data")

    assert "simple_index" in config.pattern_templates
    assert "get_by_id" in config.pattern_templates
    assert "search" in config.pattern_templates

    # Test search pattern accepts kwargs
    search_pattern = config.pattern_templates["search"]
    assert search_pattern.accepts_kwargs is True


def test_list_available_configs():
    """Test listing available configs."""
    registry = EndpointRegistry()
    configs = registry.list_available_configs()
    assert "wow_game_data" in configs


def test_invalid_config():
    """Test accessing non-existent config raises error."""
    registry = EndpointRegistry()
    with pytest.raises(KeyError):
        registry.get_config("invalid", "config")
