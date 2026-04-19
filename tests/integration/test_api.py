"""End-to-end tests for the public BlizzardAPI surface.

These are "integration" only in the sense that they wire the full facade
(BlizzardAPI → sub-API → executor → httpx client) together. No real
HTTP is made — ``httpx.MockTransport`` intercepts every request.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable

import httpx
import pytest

from blizzardapi3 import ApiResponse, BlizzardAPI, ClassicTrack, Locale, Region


# ---------------------------------------------------------------------------
# Transport helper
# ---------------------------------------------------------------------------


@dataclass
class _Recorder:
    requests: list[httpx.Request]


def _install_mock_transport(
    api: BlizzardAPI,
    *,
    handler: Callable[[httpx.Request], httpx.Response],
) -> _Recorder:
    """Replace the sync + async httpx sessions on ``api`` with a mock transport.

    Also primes the token manager so tests don't have to stub an OAuth
    response — auth is covered separately in ``test_auth.py``.
    """
    rec = _Recorder(requests=[])

    def wrapped(request: httpx.Request) -> httpx.Response:
        rec.requests.append(request)
        return handler(request)

    transport = httpx.MockTransport(wrapped)
    api._sync_client = httpx.Client(transport=transport)
    api._async_client = httpx.AsyncClient(transport=transport)
    api.token_manager._token = "primed-token"
    api.token_manager._expires_at = time.time() + 86400
    return rec


# ---------------------------------------------------------------------------
# Facade wiring
# ---------------------------------------------------------------------------


def test_api_initialization(mock_credentials):
    api = BlizzardAPI(**mock_credentials)
    assert api.client_id == "test_client_id"
    assert api.client_secret == "test_client_secret"
    assert api.default_region == Region.US
    assert api.default_locale == Locale.EN_US


def test_sub_apis_are_wired(api_client):
    assert hasattr(api_client, "wow")
    assert hasattr(api_client.wow, "game_data")
    assert hasattr(api_client.wow, "profile")
    assert hasattr(api_client.wow, "classic")
    assert hasattr(api_client.wow, "classic_era")
    assert hasattr(api_client, "d3")
    assert hasattr(api_client, "sc2")
    assert hasattr(api_client, "hearthstone")


def test_classic_tracks(api_client):
    assert api_client.wow.classic.track == ClassicTrack.progression
    assert api_client.wow.classic_era.track == ClassicTrack.era


def test_context_manager_closes_sessions(mock_credentials):
    api = BlizzardAPI(**mock_credentials)
    with api:
        _ = api.sync_client  # force session creation
    assert api._sync_client is None or api._sync_client.is_closed


def test_paired_async_methods_exist(api_client):
    for name in ("get_achievement", "search_decor", "get_connected_realm"):
        assert hasattr(api_client.wow.game_data, name)
        assert hasattr(api_client.wow.game_data, f"{name}_async")


# ---------------------------------------------------------------------------
# Sync retail call — verifies URL, namespace, locale, auth header
# ---------------------------------------------------------------------------


def test_sync_retail_call_builds_expected_request(api_client, mock_achievement_response):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert str(request.url).startswith("https://us.api.blizzard.com/data/wow/achievement/6")
        assert request.url.params["namespace"] == "static-us"
        assert request.url.params["locale"] == "en_US"
        assert request.headers["authorization"] == "Bearer primed-token"
        return httpx.Response(200, json=mock_achievement_response, headers={"X-Custom": "yes"})

    rec = _install_mock_transport(api_client, handler=handler)

    with api_client:
        result = api_client.wow.game_data.get_achievement(region="us", locale="en_US", achievement_id=6)

    assert isinstance(result, ApiResponse)
    assert result["id"] == 6
    assert result.status_code == 200
    assert result.headers["x-custom"] == "yes"
    assert len(rec.requests) == 1


def test_search_method_forwards_kwargs_as_query_params(api_client, mock_search_response):
    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url).startswith("https://us.api.blizzard.com/data/wow/search/decor")
        assert request.url.params["orderby"] == "id"
        assert request.url.params["_page"] == "1"
        return httpx.Response(200, json=mock_search_response)

    _install_mock_transport(api_client, handler=handler)

    with api_client:
        result = api_client.wow.game_data.search_decor(
            region="us", locale="en_US", orderby="id", _page=1
        )

    assert "results" in result
    assert result["page"] == 1


# ---------------------------------------------------------------------------
# Async retail call
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_async_retail_call(api_client, mock_achievement_response):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=mock_achievement_response)

    _install_mock_transport(api_client, handler=handler)

    async with api_client:
        result = await api_client.wow.game_data.get_achievement_async(
            region="us", locale="en_US", achievement_id=6
        )

    assert result["id"] == 6


# ---------------------------------------------------------------------------
# Classic track → namespace token
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "track_attr, expected_namespace",
    [
        ("classic", "static-classic-us"),
        ("classic_era", "static-classic1x-us"),
    ],
)
def test_classic_namespace_tokens(api_client, track_attr, expected_namespace):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["namespace"] == expected_namespace
        return httpx.Response(200, json={"id": 6})

    _install_mock_transport(api_client, handler=handler)

    with api_client:
        sub = getattr(api_client.wow, track_attr)
        result = sub.game_data.get_achievement(region="us", locale="en_US", achievement_id=6)
    assert result["id"] == 6


# ---------------------------------------------------------------------------
# Profile endpoints that accept a user access token
# ---------------------------------------------------------------------------


def test_profile_access_token_overrides_oauth_bearer(api_client):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer user-token-xyz"
        assert "access_token" not in request.url.params
        return httpx.Response(200, json={"wow_accounts": []})

    _install_mock_transport(api_client, handler=handler)

    with api_client:
        result = api_client.wow.profile.get_account_profile_summary(
            region="us", locale="en_US", access_token="user-token-xyz"
        )
    assert "wow_accounts" in result


# ---------------------------------------------------------------------------
# Diablo 3 / SC2 / Hearthstone (no namespace, locale only)
# ---------------------------------------------------------------------------


def test_d3_endpoint_uses_no_namespace(api_client):
    def handler(request: httpx.Request) -> httpx.Response:
        assert "namespace" not in request.url.params
        assert request.url.params["locale"] == "en_US"
        assert request.url.path == "/d3/data/act"
        return httpx.Response(200, json={"acts": []})

    _install_mock_transport(api_client, handler=handler)

    with api_client:
        result = api_client.d3.get_act_index(region="us", locale="en_US")
    assert "acts" in result


def test_sc2_league_uses_fixed_path(api_client):
    """Regression: league endpoint must hit ``/data/sc2/league/...``, not ``/sc2/league/...``."""

    def handler(request: httpx.Request) -> httpx.Response:
        assert "/data/sc2/league/37/201/0/1" in str(request.url)
        return httpx.Response(200, json={"league_id": 1})

    _install_mock_transport(api_client, handler=handler)

    with api_client:
        result = api_client.sc2.get_league_data(
            region="us", locale="en_US", season_id=37, queue_id=201, team_type=0, league_id=1
        )
    assert result["league_id"] == 1


def test_hearthstone_search_forwards_filter_kwargs(api_client):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["class"] == "mage"
        assert request.url.params["manaCost"] == "7"
        return httpx.Response(200, json={"cards": []})

    _install_mock_transport(api_client, handler=handler)

    with api_client:
        # ``class`` is a keyword, so pass via ``**``
        result = api_client.hearthstone.search_cards(
            region="us", locale="en_US", **{"class": "mage", "manaCost": 7}
        )
    assert "cards" in result
