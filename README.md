# BlizzardAPI v3

A modern, config-driven Python wrapper for the Blizzard API with full async support, response caching, automatic retries, and comprehensive error handling.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Accessing Response Headers](#accessing-response-headers)
- [Using Search Endpoints](#using-search-endpoints)
- [Error Handling](#error-handling)
- [Comprehensive Examples](#comprehensive-examples)
- [Supported Games](#supported-games)
- [Documentation](#documentation)
- [Development](#development)
- [Architecture](#architecture)

## Features

- 🚀 **Async/Await Support** - First-class async support with both sync and async methods
- 🔒 **Type Hints** - Ships `py.typed`; responses are dict-like with full IDE autocomplete
- 📝 **Config-Driven** - YAML-defined endpoints, easy to extend
- 🎯 **Better Errors** - Specific exception types with detailed context
- ⚡ **Response Caching** - On by default; honors `Cache-Control` so repeat calls skip the network
- 🔁 **Automatic Retries** - Transient 429/5xx failures retried with `Retry-After` and full-jitter backoff
- 🧵 **Concurrent Fan-Out** - `api.gather()` runs many async calls with a bounded concurrency cap
- 📊 **Response Headers** - Access HTTP headers for caching, rate limits, and metadata
- 🎮 **Complete Coverage** - Supports WoW, Diablo 3, Hearthstone, and StarCraft 2

## Installation

```bash
pip install blizzardapi3
```

> **Version stability:** BlizzardAPI v3 is under active development and is not yet considered stable. Breaking changes may land between minor versions as internal patterns are refined. For production use, pin to an exact version and review the [release notes](https://github.com/lostcol0ny/blizzardapi3/releases) before upgrading:
>
> ```bash
> pip install blizzardapi3==4.1.0
> ```

## Quick Start

### Synchronous Usage

```python
from blizzardapi3 import BlizzardAPI

# Use context manager for proper cleanup
with BlizzardAPI(client_id="your_id", client_secret="your_secret") as api:
    # Get WoW achievement
    achievement = api.wow.game_data.get_achievement(
        region="us",
        locale="en_US",
        achievement_id=6
    )
    print(achievement["name"]["en_US"])
```

### Asynchronous Usage

```python
import asyncio
from blizzardapi3 import BlizzardAPI

async def main():
    async with BlizzardAPI(client_id="your_id", client_secret="your_secret") as api:
        # Async methods end with _async
        achievement = await api.wow.game_data.get_achievement_async(
            region="us",
            locale="en_US",
            achievement_id=6
        )
        print(achievement["name"]["en_US"])

asyncio.run(main())
```

## Configuration

`BlizzardAPI` accepts a few keyword options that tune caching and reliability. All are optional and chosen so the defaults are safe for most users.

```python
api = BlizzardAPI(
    client_id="your_id",
    client_secret="your_secret",
    cache=True,        # response cache (default on)
    cache_ttl=None,    # seconds to cache responses that send no Cache-Control
    max_retries=2,     # automatic retries on transient 429/5xx failures
)
```

| Option | Default | Behavior |
| --- | --- | --- |
| `cache` | `True` | Caches responses according to their `Cache-Control` header. Static game data (`max-age=86400`) is served from memory until it expires; profile data, which sends no cache directive, is not cached. Set `cache=False` to disable. |
| `cache_ttl` | `None` | Caches responses that carry *no* `Cache-Control` (e.g. character profiles) for this many seconds — a deliberate staleness-for-speed trade you opt into. A server `no-store` / `private` is always honored regardless. |
| `max_retries` | `2` | Bounds automatic retries on transient failures (HTTP 429 and 5xx), honoring `Retry-After` and otherwise backing off with full jitter. Set to `0` to disable and surface the error immediately. |

## Accessing Response Headers

All API responses include HTTP headers that provide useful metadata. The response object behaves like a dict for data access while also exposing headers:

```python
from blizzardapi3 import BlizzardAPI

with BlizzardAPI(client_id, client_secret) as api:
    result = api.wow.game_data.get_achievement(
        region="us",
        locale="en_US",
        achievement_id=6
    )

    # Access data (unchanged - full backwards compatibility)
    print(result["name"])
    print(result.get("points"))

    # Access response headers
    print(result.headers.get("Last-Modified"))
    print(result.headers.get("Cache-Control"))
    print(result.status_code)

    # List all headers
    for name, value in result.headers.items():
        print(f"{name}: {value}")
```

### Useful Headers

| Header | Description |
|--------|-------------|
| `Last-Modified` | When the data was last updated by Blizzard |
| `Cache-Control` | Caching policy (e.g., `max-age=86400` = 24 hours) |
| `Battlenet-Namespace` | The namespace/version of the data |
| `blizzard-token-expires` | When the OAuth token expires |

## Using Search Endpoints

BlizzardAPI v3 provides powerful search functionality for various game resources. Search methods accept flexible keyword arguments for filtering and pagination.

### Basic Search

```python
from blizzardapi3 import BlizzardAPI, Region, Locale

with BlizzardAPI(client_id, client_secret) as api:
    # Search for decor items containing "wall"
    results = api.wow.game_data.search_decor(
        region=Region.US,
        locale=Locale.EN_US,
        **{"name.en_US": "wall"}
    )

    print(f"Found {len(results['results'])} items")
    for item in results['results']:
        data = item['data']
        print(f"{data['name']['en_US']} (ID: {data['id']})")
```

### Pagination and Ordering

```python
with BlizzardAPI(client_id, client_secret) as api:
    # Get first page, ordered by ID
    results = api.wow.game_data.search_decor(
        region=Region.US,
        locale=Locale.EN_US,
        orderby="id",
        _page=1
    )

    print(f"Page {results['page']} of {results['pageCount']}")
    print(f"Results per page: {results['pageSize']}")
```

### Advanced Filtering

Search endpoints support locale-specific filtering using dot notation:

```python
with BlizzardAPI(client_id, client_secret) as api:
    # Search with multiple filters
    results = api.wow.game_data.search_decor(
        region=Region.US,
        locale=Locale.EN_US,
        **{
            "name.en_US": "mirror",
            "orderby": "id:desc",
            "_page": 1
        }
    )
```

### Available Search Methods

#### World of Warcraft Game Data

- `search_azerite_essence()` - Search azerite essences
- `search_covenant()` - Search covenants
- `search_creature()` - Search creatures
- `search_decor()` - Search housing decor items
- `search_item()` - Search items
- `search_media()` - Search media assets
- `search_mount()` - Search mounts
- `search_pet()` - Search battle pets
- `search_profession()` - Search professions
- `search_spell()` - Search spells

### Common Search Parameters

| Parameter       | Description              | Example              |
| --------------- | ------------------------ | -------------------- |
| `name.{locale}` | Filter by localized name | `name.en_US: "wall"` |
| `orderby`       | Sort results             | `"id"`, `"id:desc"`  |
| `_page`         | Page number (1-indexed)  | `1`, `2`, `3`        |

### Search Response Structure

```python
{
    "page": 1,
    "pageSize": 100,
    "maxPageSize": 100,
    "pageCount": 10,
    "results": [
        {
            "key": {"href": "..."},
            "data": {
                "id": 534,
                "name": {"en_US": "Plain Interior Wall"},
                # ... additional fields
            }
        }
    ]
}
```

## Error Handling

```python
from blizzardapi3 import BlizzardAPI
from blizzardapi3.exceptions import NotFoundError, RateLimitError

with BlizzardAPI(client_id, client_secret) as api:
    try:
        data = api.wow.game_data.get_achievement(
            region="us",
            locale="en_US",
            achievement_id=999999
        )
    except NotFoundError:
        print("Achievement not found")
    except RateLimitError as e:
        print(f"Rate limited. Retry after {e.retry_after} seconds")
```

## Comprehensive Examples

### Character Profile Information

```python
from blizzardapi3 import BlizzardAPI, Region, Locale

with BlizzardAPI(client_id, client_secret) as api:
    # Get character appearance
    appearance = api.wow.profile.get_character_appearance_summary(
        region=Region.US,
        locale=Locale.EN_US,
        realm_slug="illidan",
        character_name="beyloc"
    )

    print(f"Character: {appearance['character']['name']}")
    print(f"Race: {appearance['playable_race']['name']}")
    print(f"Class: {appearance['playable_class']['name']}")
    print(f"Spec: {appearance['active_spec']['name']}")

    # Get character equipment
    equipment = api.wow.profile.get_character_equipment_summary(
        region=Region.US,
        locale=Locale.EN_US,
        realm_slug="illidan",
        character_name="beyloc"
    )

    for item in equipment['equipped_items']:
        print(f"{item['slot']['name']}: {item['name']}")
```

### Building a Decor Browser

```python
from blizzardapi3 import BlizzardAPI, Region, Locale

def search_decor_by_name(api, search_term, page=1):
    """Search for decor items by name with pagination."""
    results = api.wow.game_data.search_decor(
        region=Region.US,
        locale=Locale.EN_US,
        **{
            "name.en_US": search_term,
            "orderby": "id",
            "_page": page
        }
    )

    items = []
    for result in results['results']:
        data = result['data']
        items.append({
            'id': data['id'],
            'name': data['name']['en_US'],
            'href': result['key']['href']
        })

    return {
        'items': items,
        'page': results['page'],
        'total_pages': results['pageCount'],
        'has_more': results['page'] < results['pageCount']
    }

with BlizzardAPI(client_id, client_secret) as api:
    # Search for walls
    result = search_decor_by_name(api, "wall", page=1)

    for item in result['items']:
        print(f"{item['name']} (ID: {item['id']})")

    if result['has_more']:
        print(f"\nShowing page {result['page']} of {result['total_pages']}")
```

### Item Search with Filtering

```python
with BlizzardAPI(client_id, client_secret) as api:
    # Search for epic quality items
    items = api.wow.game_data.search_item(
        region=Region.US,
        locale=Locale.EN_US,
        **{
            "name.en_US": "sword",
            "orderby": "id:desc",
            "_page": 1
        }
    )

    for result in items['results'][:10]:
        item = result['data']
        print(f"{item['name']['en_US']} (ID: {item['id']})")
```

### Async Batch Operations

```python
import asyncio
from blizzardapi3 import BlizzardAPI, Region, Locale

async def get_multiple_achievements(api, achievement_ids):
    """Fetch multiple achievements concurrently with a bounded concurrency cap."""
    tasks = [
        api.wow.game_data.get_achievement_async(
            region=Region.US,
            locale=Locale.EN_US,
            achievement_id=aid
        )
        for aid in achievement_ids
    ]
    # api.gather caps in-flight requests (default 10) so a large batch
    # doesn't overrun Blizzard's rate limiter. Results keep input order.
    return await api.gather(*tasks, max_concurrency=10)

async def main():
    async with BlizzardAPI(client_id, client_secret) as api:
        achievement_ids = [6, 7, 8, 9, 10]
        achievements = await get_multiple_achievements(api, achievement_ids)

        for ach in achievements:
            print(f"{ach['name']} - {ach['points']} points")

asyncio.run(main())
```

### Guild Information

```python
with BlizzardAPI(client_id, client_secret) as api:
    # Get guild roster
    roster = api.wow.profile.get_guild_roster(
        region=Region.US,
        locale=Locale.EN_US,
        realm_slug="illidan",
        name_slug="your-guild-name"
    )

    for member in roster['members']:
        char = member['character']
        print(f"{char['name']} - Level {char['level']} {char.get('playable_class', {}).get('name', 'Unknown')}")
```

### Diablo 3 Examples

```python
from blizzardapi3 import BlizzardAPI, Region, Locale

with BlizzardAPI(client_id, client_secret) as api:
    # Get D3 season index
    seasons = api.d3.game_data.get_season_index(
        region=Region.US,
        locale=Locale.EN_US
    )
    print(f"Current season: {seasons['current_season']}")

    # Get a player's career profile
    profile = api.d3.community.get_career(
        region=Region.US,
        locale=Locale.EN_US,
        battle_tag="BattleTag-1234"
    )
    print(f"Paragon level: {profile['paragonLevel']}")

    # Get item type index
    item_types = api.d3.game_data.get_item_type_index(
        region=Region.US,
        locale=Locale.EN_US
    )
```

### Hearthstone Examples

```python
from blizzardapi3 import BlizzardAPI, Region, Locale

with BlizzardAPI(client_id, client_secret) as api:
    # Search for cards
    cards = api.hearthstone.game_data.search_cards(
        region=Region.US,
        locale=Locale.EN_US,
        **{"class": "mage", "manaCost": 3}
    )
    for card in cards['cards'][:5]:
        print(f"{card['name']} - {card['manaCost']} mana")

    # Get card backs
    card_backs = api.hearthstone.game_data.search_card_backs(
        region=Region.US,
        locale=Locale.EN_US
    )

    # Get metadata
    metadata = api.hearthstone.game_data.get_metadata(
        region=Region.US,
        locale=Locale.EN_US
    )
```

### StarCraft 2 Examples

```python
from blizzardapi3 import BlizzardAPI, Region, Locale

with BlizzardAPI(client_id, client_secret) as api:
    # Get league data
    league = api.sc2.game_data.get_league_data(
        region=Region.US,
        locale=Locale.EN_US,
        season_id=44,
        queue_id=201,
        team_type="0",
        league_id=6
    )

    # Get static profile data
    static = api.sc2.community.get_static_profile(
        region=Region.US,
        locale=Locale.EN_US,
        region_id=1
    )

    # Get grandmaster leaderboard
    gm_ladder = api.sc2.community.get_grandmaster_leaderboard(
        region=Region.US,
        locale=Locale.EN_US,
        region_id=1
    )
```

## Supported Games

- **World of Warcraft** - Game Data & Profile APIs (~290 endpoints)
  - Game Data: Achievements, Items, Mounts, Pets, Auctions, Housing/Decor, and more
  - Profile: Characters, Guilds, Mythic+, PvP, Collections, Equipment
- **Diablo 3** - Community & Game Data APIs (39 endpoints)
  - Game Data: Items, item types, seasons, eras
  - Community: Career profiles, heroes, items, followers
- **Hearthstone** - Game Data API (12 endpoints)
  - Cards, card backs, decks, metadata search
- **StarCraft 2** - Community & Game Data APIs (22 endpoints)
  - Game Data: League data
  - Community: Profiles, ladders, grandmaster leaderboards

**Total: 363 endpoints** (726 methods including async variants)

## Documentation

### Core Documentation

- **[Search Guide](docs/SEARCH_GUIDE.md)** - Comprehensive guide to using search endpoints with real-world examples
- **[Search Quick Reference](docs/SEARCH_QUICK_REFERENCE.md)** - Quick reference for all search methods and parameters
- **[OAuth Guide](docs/OAUTH_GUIDE.md)** - Complete guide to OAuth authorization code flow for user-specific endpoints

### Additional Resources

- [Blizzard API Official Documentation](https://develop.battle.net/documentation)
- [GitHub Repository](https://github.com/lostcol0ny/blizzardapi3)
- [Issue Tracker](https://github.com/lostcol0ny/blizzardapi3/issues)

## Development

```bash
# Clone the repository
git clone https://github.com/lostcol0ny/blizzardapi3.git
cd blizzardapi3

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
ruff check .

# Regenerate stub files for IDE autocomplete (after modifying YAML configs)
python scripts/generate_stubs.py
```

### IDE Autocomplete

BlizzardAPI uses `.pyi` stub files to provide full IDE autocomplete for all dynamically generated API methods. If you modify the YAML endpoint configurations, run the stub generator to update the type hints:

```bash
python scripts/generate_stubs.py
```

This generates stub files in `blizzardapi3/api/` for each game API.

## Architecture

BlizzardAPI v3 uses a config-driven architecture:

- **YAML Endpoint Definitions** - All API endpoints defined in YAML configs
- **Dynamic Method Generation** - Methods generated at runtime from configs
- **Pydantic Models** - Type-safe response models
- **Custom Exceptions** - Detailed error hierarchy
- **Single Session** - Efficient session management with proper cleanup
