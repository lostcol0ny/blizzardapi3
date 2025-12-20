# Search Quick Reference

Quick reference for all search endpoints and parameters in BlizzardAPI v3.

## Quick Start

```python
from blizzardapi3 import BlizzardAPI, Region, Locale

with BlizzardAPI(client_id, client_secret) as api:
    results = api.wow.game_data.search_decor(
        region=Region.US,
        locale=Locale.EN_US,
        **{"name.en_US": "wall", "_page": 1}
    )
```

## Search Parameters

### Standard Parameters

All search endpoints support these parameters:

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `region` | Region/str | API region | `Region.US` or `"us"` |
| `locale` | Locale/str | Response locale | `Locale.EN_US` or `"en_US"` |
| `orderby` | str | Sort field and direction | `"id"` or `"id:desc"` |
| `_page` | int | Page number (1-indexed) | `1`, `2`, `3` |

### Filtering Parameters

Use dict unpacking (`**{...}`) for filter parameters:

| Parameter Pattern | Description | Example |
|------------------|-------------|---------|
| `name.{locale}` | Filter by localized name | `**{"name.en_US": "wall"}` |
| `id` | Filter by specific ID | `**{"id": 534}` |

## WoW Game Data Search Endpoints

### search_azerite_essence()

Search for azerite essences.

```python
results = api.wow.game_data.search_azerite_essence(
    region=Region.US,
    locale=Locale.EN_US,
    **{"name.en_US": "essence"}
)
```

**Common filters**: `name.{locale}`, `orderby`, `_page`

---

### search_covenant()

Search for covenants.

```python
results = api.wow.game_data.search_covenant(
    region=Region.US,
    locale=Locale.EN_US,
    **{"name.en_US": "kyrian"}
)
```

**Common filters**: `name.{locale}`, `orderby`, `_page`

---

### search_creature()

Search for creatures/NPCs.

```python
results = api.wow.game_data.search_creature(
    region=Region.US,
    locale=Locale.EN_US,
    **{"name.en_US": "dragon"}
)
```

**Common filters**: `name.{locale}`, `orderby`, `_page`

---

### search_decor()

Search for housing decor items.

```python
results = api.wow.game_data.search_decor(
    region=Region.US,
    locale=Locale.EN_US,
    **{"name.en_US": "wall", "orderby": "id"}
)
```

**Common filters**: `name.{locale}`, `orderby`, `_page`

**Example response**:
```python
{
    'page': 1,
    'pageCount': 3,
    'results': [
        {
            'data': {
                'id': 534,
                'name': {'en_US': 'Plain Interior Wall'}
            }
        }
    ]
}
```

---

### search_item()

Search for items.

```python
results = api.wow.game_data.search_item(
    region=Region.US,
    locale=Locale.EN_US,
    **{"name.en_US": "sword", "orderby": "id:desc"}
)
```

**Common filters**: `name.{locale}`, `orderby`, `_page`

---

### search_media()

Search for media assets.

```python
results = api.wow.game_data.search_media(
    region=Region.US,
    locale=Locale.EN_US,
    orderby="id",
    _page=1
)
```

**Common filters**: `orderby`, `_page`

---

### search_mount()

Search for mounts.

```python
results = api.wow.game_data.search_mount(
    region=Region.US,
    locale=Locale.EN_US,
    **{"name.en_US": "horse"}
)
```

**Common filters**: `name.{locale}`, `orderby`, `_page`

---

### search_pet()

Search for battle pets.

```python
results = api.wow.game_data.search_pet(
    region=Region.US,
    locale=Locale.EN_US,
    **{"name.en_US": "cat"}
)
```

**Common filters**: `name.{locale}`, `orderby`, `_page`

---

### search_profession()

Search for professions.

```python
results = api.wow.game_data.search_profession(
    region=Region.US,
    locale=Locale.EN_US,
    **{"name.en_US": "blacksmithing"}
)
```

**Common filters**: `name.{locale}`, `orderby`, `_page`

---

### search_spell()

Search for spells.

```python
results = api.wow.game_data.search_spell(
    region=Region.US,
    locale=Locale.EN_US,
    **{"name.en_US": "fireball"}
)
```

**Common filters**: `name.{locale}`, `orderby`, `_page`

---

## Async Variants

All search methods have async variants ending with `_async`:

```python
import asyncio

async def main():
    async with BlizzardAPI(client_id, client_secret) as api:
        results = await api.wow.game_data.search_decor_async(
            region=Region.US,
            locale=Locale.EN_US,
            **{"name.en_US": "wall"}
        )

asyncio.run(main())
```

## Common Patterns

### Pattern 1: Basic Name Search

```python
results = api.wow.game_data.search_<resource>(
    region=Region.US,
    locale=Locale.EN_US,
    **{"name.en_US": "search_term"}
)
```

### Pattern 2: Paginated Search

```python
results = api.wow.game_data.search_<resource>(
    region=Region.US,
    locale=Locale.EN_US,
    **{"name.en_US": "search_term"},
    orderby="id",
    _page=1
)
```

### Pattern 3: Sorted Results

```python
# Ascending order
results = api.wow.game_data.search_<resource>(
    region=Region.US,
    locale=Locale.EN_US,
    orderby="id"
)

# Descending order
results = api.wow.game_data.search_<resource>(
    region=Region.US,
    locale=Locale.EN_US,
    orderby="id:desc"
)
```

### Pattern 4: Multi-Locale Search

```python
# Search in different locales
locales = [Locale.EN_US, Locale.DE_DE, Locale.FR_FR]

for locale in locales:
    locale_code = locale.value  # e.g., "en_US"
    results = api.wow.game_data.search_decor(
        region=Region.EU,
        locale=locale,
        **{f"name.{locale_code}": "wall"}
    )
```

## Response Structure

All search endpoints return:

```python
{
    "page": 1,              # Current page
    "pageSize": 100,        # Results per page
    "maxPageSize": 100,     # Max allowed page size
    "pageCount": 5,         # Total pages
    "results": [            # Array of results
        {
            "key": {
                "href": "https://..."
            },
            "data": {
                "id": 123,
                "name": {
                    "en_US": "Item Name",
                    # ... other locales
                },
                # ... other fields
            }
        }
    ]
}
```

## Error Handling

```python
from blizzardapi3.exceptions import (
    NotFoundError,
    RateLimitError,
    BadRequestError
)

try:
    results = api.wow.game_data.search_decor(
        region=Region.US,
        locale=Locale.EN_US,
        **{"name.en_US": "wall"}
    )
except BadRequestError:
    print("Invalid search parameters")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
except NotFoundError:
    print("Resource not found")
```

## Supported Locales

### Americas (US, LA)
- `en_US` - English (US)
- `es_MX` - Spanish (Mexico)
- `pt_BR` - Portuguese (Brazil)

### Europe (EU)
- `en_GB` - English (UK)
- `es_ES` - Spanish (Spain)
- `fr_FR` - French
- `de_DE` - German
- `it_IT` - Italian
- `pt_PT` - Portuguese (Portugal)
- `ru_RU` - Russian

### Asia
- `ko_KR` - Korean
- `zh_TW` - Chinese (Taiwan)
- `zh_CN` - Chinese (China)

## Tips and Tricks

### Tip 1: Case Sensitivity

Search is case-insensitive:

```python
# These are equivalent
**{"name.en_US": "wall"}
**{"name.en_US": "Wall"}
**{"name.en_US": "WALL"}
```

### Tip 2: Partial Matching

Searches match partial strings:

```python
# Finds "Wall Mirror", "Stone Wall", "Wall Shelf", etc.
**{"name.en_US": "wall"}
```

### Tip 3: Empty Search

Omit name filter to get all results:

```python
# Get all decor items (paginated)
results = api.wow.game_data.search_decor(
    region=Region.US,
    locale=Locale.EN_US,
    orderby="id",
    _page=1
)
```

### Tip 4: Extracting Data

Quickly extract just the data you need:

```python
results = api.wow.game_data.search_decor(
    region=Region.US,
    locale=Locale.EN_US,
    **{"name.en_US": "wall"}
)

# Extract just IDs and names
items = [
    {
        'id': r['data']['id'],
        'name': r['data']['name']['en_US']
    }
    for r in results['results']
]
```

### Tip 5: Pagination Helper

```python
def get_all_pages(api, search_func, **kwargs):
    """Generic helper to fetch all pages."""
    all_results = []
    page = 1

    while True:
        results = search_func(**kwargs, _page=page)

        all_results.extend(results['results'])

        if page >= results['pageCount']:
            break

        page += 1

    return all_results


# Usage
all_walls = get_all_pages(
    api,
    api.wow.game_data.search_decor,
    region=Region.US,
    locale=Locale.EN_US,
    **{"name.en_US": "wall"}
)
```

## See Also

- [Complete Search Guide](SEARCH_GUIDE.md)
- [Main README](../README.md)
- [API Reference](API_REFERENCE.md)
