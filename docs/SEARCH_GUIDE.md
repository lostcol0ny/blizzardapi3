# Search Functionality Guide

This guide provides comprehensive documentation on using the search endpoints in BlizzardAPI v3.

## Table of Contents

- [Overview](#overview)
- [Basic Search](#basic-search)
- [Advanced Filtering](#advanced-filtering)
- [Pagination](#pagination)
- [Available Search Endpoints](#available-search-endpoints)
- [Real-World Examples](#real-world-examples)
- [Best Practices](#best-practices)

## Overview

BlizzardAPI v3 provides search functionality for various game resources. All search methods:
- Accept flexible keyword arguments for filtering
- Return paginated results
- Support locale-specific searching
- Allow custom ordering

## Basic Search

### Simple Name Search

```python
from blizzardapi3 import BlizzardAPI, Region, Locale

with BlizzardAPI(client_id, client_secret) as api:
    # Search for decor items by name
    results = api.wow.game_data.search_decor(
        region=Region.US,
        locale=Locale.EN_US,
        **{"name.en_US": "wall"}
    )

    for result in results['results']:
        item = result['data']
        print(f"{item['name']['en_US']} (ID: {item['id']})")
```

**Why use `**{...}`?**

The double asterisk (`**`) unpacks a dictionary as keyword arguments. This is necessary because Blizzard's search API uses dot notation for field names (e.g., `name.en_US`), which aren't valid Python identifiers.

## Advanced Filtering

### Multiple Filters

Combine multiple search criteria:

```python
results = api.wow.game_data.search_item(
    region=Region.US,
    locale=Locale.EN_US,
    **{
        "name.en_US": "sword",
        "orderby": "id:desc"
    }
)
```

### Locale-Specific Searches

Search in different locales:

```python
# Search in Spanish
results_es = api.wow.game_data.search_decor(
    region=Region.EU,
    locale=Locale.ES_ES,
    **{"name.es_ES": "espejo"}  # "mirror" in Spanish
)

# Search in German
results_de = api.wow.game_data.search_mount(
    region=Region.EU,
    locale=Locale.DE_DE,
    **{"name.de_DE": "drache"}  # "dragon" in German
)
```

## Pagination

### Understanding Pagination

Search results are paginated with a default page size of 100 items.

```python
results = api.wow.game_data.search_decor(
    region=Region.US,
    locale=Locale.EN_US,
    orderby="id",
    _page=1
)

print(f"Current page: {results['page']}")
print(f"Total pages: {results['pageCount']}")
print(f"Results per page: {results['pageSize']}")
print(f"Max page size: {results['maxPageSize']}")
```

### Iterating Through Pages

```python
def get_all_results(api, search_term):
    """Get all pages of search results."""
    all_items = []
    page = 1

    while True:
        results = api.wow.game_data.search_decor(
            region=Region.US,
            locale=Locale.EN_US,
            **{
                "name.en_US": search_term,
                "orderby": "id",
                "_page": page
            }
        )

        # Extract items from current page
        for result in results['results']:
            all_items.append(result['data'])

        # Check if there are more pages
        if page >= results['pageCount']:
            break

        page += 1

    return all_items

# Usage
with BlizzardAPI(client_id, client_secret) as api:
    all_walls = get_all_results(api, "wall")
    print(f"Found {len(all_walls)} total items")
```

## Available Search Endpoints

### World of Warcraft - Game Data

| Method | Description | Example Search |
|--------|-------------|----------------|
| `search_azerite_essence()` | Search azerite essences | `name.en_US: "essence"` |
| `search_covenant()` | Search covenants | `name.en_US: "kyrian"` |
| `search_creature()` | Search creatures | `name.en_US: "dragon"` |
| `search_decor()` | Search housing decor | `name.en_US: "wall"` |
| `search_item()` | Search items | `name.en_US: "sword"` |
| `search_media()` | Search media assets | - |
| `search_mount()` | Search mounts | `name.en_US: "horse"` |
| `search_pet()` | Search battle pets | `name.en_US: "cat"` |
| `search_profession()` | Search professions | `name.en_US: "blacksmithing"` |
| `search_spell()` | Search spells | `name.en_US: "fireball"` |

## Real-World Examples

### Example 1: Decor Browser Application

Build a paginated decor item browser:

```python
from blizzardapi3 import BlizzardAPI, Region, Locale

class DecorBrowser:
    def __init__(self, client_id, client_secret):
        self.api = BlizzardAPI(client_id, client_secret)
        self.current_page = 1
        self.search_term = ""

    def __enter__(self):
        self.api.__enter__()
        return self

    def __exit__(self, *args):
        self.api.__exit__(*args)

    def search(self, term, page=1):
        """Search for decor items with pagination."""
        self.search_term = term
        self.current_page = page

        results = self.api.wow.game_data.search_decor(
            region=Region.US,
            locale=Locale.EN_US,
            **{
                "name.en_US": term,
                "orderby": "id",
                "_page": page
            }
        )

        return {
            'items': [r['data'] for r in results['results']],
            'current_page': results['page'],
            'total_pages': results['pageCount'],
            'total_results': len(results['results']),
            'has_previous': page > 1,
            'has_next': page < results['pageCount']
        }

    def next_page(self):
        """Get next page of current search."""
        return self.search(self.search_term, self.current_page + 1)

    def previous_page(self):
        """Get previous page of current search."""
        if self.current_page > 1:
            return self.search(self.search_term, self.current_page - 1)
        return None


# Usage
with DecorBrowser(client_id, client_secret) as browser:
    # Initial search
    result = browser.search("mirror")

    print(f"Found items on page {result['current_page']} of {result['total_pages']}")
    for item in result['items'][:5]:
        print(f"  - {item['name']['en_US']} (ID: {item['id']})")

    # Get next page
    if result['has_next']:
        next_result = browser.next_page()
        print(f"\nNext page has {next_result['total_results']} items")
```

### Example 2: Mount Collection Tracker

Find which mounts a player is missing:

```python
async def find_missing_mounts(api, realm, character_name):
    """Find mounts a character doesn't have yet."""
    # Get all available mounts
    all_mounts = []
    page = 1

    while True:
        results = await api.wow.game_data.search_mount_async(
            region=Region.US,
            locale=Locale.EN_US,
            orderby="id",
            _page=page
        )

        for result in results['results']:
            all_mounts.append({
                'id': result['data']['id'],
                'name': result['data']['name']['en_US']
            })

        if page >= results['pageCount']:
            break
        page += 1

    # Get character's mounts
    char_mounts = await api.wow.profile.get_character_mounts_collection_summary_async(
        region=Region.US,
        locale=Locale.EN_US,
        realm_slug=realm,
        character_name=character_name
    )

    collected_ids = {m['mount']['id'] for m in char_mounts['mounts']}

    # Find missing mounts
    missing = [m for m in all_mounts if m['id'] not in collected_ids]

    return missing


# Usage
import asyncio

async def main():
    async with BlizzardAPI(client_id, client_secret) as api:
        missing = await find_missing_mounts(api, "illidan", "beyloc")
        print(f"Missing {len(missing)} mounts:")
        for mount in missing[:10]:
            print(f"  - {mount['name']}")

asyncio.run(main())
```

### Example 3: Item Search with Caching

Implement a cached search system:

```python
from functools import lru_cache
import hashlib
import json

class CachedSearchAPI:
    def __init__(self, api):
        self.api = api

    @lru_cache(maxsize=100)
    def search_items_cached(self, search_term, page=1):
        """Search items with LRU caching."""
        results = self.api.wow.game_data.search_item(
            region=Region.US,
            locale=Locale.EN_US,
            **{
                "name.en_US": search_term,
                "orderby": "id",
                "_page": page
            }
        )
        return results

    def search_with_hash(self, search_params):
        """Search with parameter hashing for cache key."""
        # Create cache key from params
        cache_key = hashlib.md5(
            json.dumps(search_params, sort_keys=True).encode()
        ).hexdigest()

        # Check if in cache...
        # ... implement caching logic

        return self.api.wow.game_data.search_item(
            region=search_params['region'],
            locale=search_params['locale'],
            **search_params['filters']
        )


# Usage
with BlizzardAPI(client_id, client_secret) as api:
    cached_api = CachedSearchAPI(api)

    # First call hits the API
    result1 = cached_api.search_items_cached("sword", 1)

    # Second call uses cache
    result2 = cached_api.search_items_cached("sword", 1)
```

## Best Practices

### 1. Use Type-Safe Enums

Always use `Region` and `Locale` enums for type safety:

```python
# Good
from blizzardapi3 import Region, Locale

results = api.wow.game_data.search_decor(
    region=Region.US,
    locale=Locale.EN_US,
    **{"name.en_US": "wall"}
)

# Works but not recommended
results = api.wow.game_data.search_decor(
    region="us",
    locale="en_US",
    **{"name.en_US": "wall"}
)
```

### 2. Handle Empty Results

Always check if results exist:

```python
results = api.wow.game_data.search_decor(
    region=Region.US,
    locale=Locale.EN_US,
    **{"name.en_US": "nonexistent"}
)

if results['results']:
    for result in results['results']:
        print(result['data']['name']['en_US'])
else:
    print("No results found")
```

### 3. Implement Rate Limiting

Respect API rate limits when making bulk searches:

```python
import time
from blizzardapi3.exceptions import RateLimitError

def search_with_retry(api, search_term, max_retries=3):
    """Search with automatic retry on rate limit."""
    for attempt in range(max_retries):
        try:
            return api.wow.game_data.search_decor(
                region=Region.US,
                locale=Locale.EN_US,
                **{"name.en_US": search_term}
            )
        except RateLimitError as e:
            if attempt < max_retries - 1:
                wait_time = e.retry_after or 60
                print(f"Rate limited. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise
```

### 4. Use Async for Concurrent Searches

When searching multiple terms, use async methods:

```python
import asyncio

async def search_multiple_terms(api, search_terms):
    """Search multiple terms concurrently."""
    tasks = [
        api.wow.game_data.search_decor_async(
            region=Region.US,
            locale=Locale.EN_US,
            **{"name.en_US": term}
        )
        for term in search_terms
    ]

    return await asyncio.gather(*tasks)


async def main():
    async with BlizzardAPI(client_id, client_secret) as api:
        terms = ["wall", "mirror", "table", "chair"]
        results = await search_multiple_terms(api, terms)

        for term, result in zip(terms, results):
            print(f"{term}: {len(result['results'])} items found")

asyncio.run(main())
```

### 5. Validate Locale Matching

Ensure your search locale matches the API locale:

```python
# Correct - locale matches search field
results = api.wow.game_data.search_decor(
    region=Region.EU,
    locale=Locale.DE_DE,
    **{"name.de_DE": "spiegel"}  # German for "mirror"
)

# Incorrect - locale mismatch
results = api.wow.game_data.search_decor(
    region=Region.EU,
    locale=Locale.EN_GB,  # English locale
    **{"name.de_DE": "spiegel"}  # But searching German field
)
```

## Response Structure Reference

All search endpoints return a consistent structure:

```python
{
    "page": 1,                    # Current page number (1-indexed)
    "pageSize": 100,              # Number of results on this page
    "maxPageSize": 100,           # Maximum results per page
    "pageCount": 10,              # Total number of pages
    "resultCountCapped": False,   # Whether result count is capped
    "results": [                  # Array of result objects
        {
            "key": {
                "href": "https://..."  # Link to full resource
            },
            "data": {
                "id": 534,
                "name": {
                    "en_US": "Plain Interior Wall",
                    "es_MX": "...",
                    # ... other locales
                },
                # ... additional resource-specific fields
            }
        }
    ]
}
```

## Common Issues and Solutions

### Issue: No Results Found

**Problem**: Search returns empty results

**Solutions**:
1. Check spelling of search term
2. Verify locale code is correct (`name.en_US`, not `name.en-US`)
3. Try searching without filters first
4. Ensure the resource type exists in that region

### Issue: Parameter Not Working

**Problem**: Search parameter seems to be ignored

**Solutions**:
1. Verify you're using `**{...}` syntax for dict unpacking
2. Check the parameter name is correct (use dot notation for fields)
3. Some endpoints may not support all filter types

### Issue: Pagination Not Working

**Problem**: Always getting first page

**Solutions**:
1. Ensure `_page` parameter is being passed
2. Verify page number is within valid range (1 to `pageCount`)
3. Check that other parameters remain consistent across page requests

## Additional Resources

- [Blizzard API Documentation](https://develop.battle.net/documentation)
- [BlizzardAPI v3 GitHub Repository](https://github.com/lostcol0ny/blizzardapi3)
- [Migration Guide](../MIGRATION.md)
- [API Reference](../README.md)
