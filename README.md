# BlizzardAPI v3

A modern, config-driven Python wrapper for the Blizzard API with full async support, type safety via Pydantic, and comprehensive error handling.

## Features

- 🚀 **Async/Await Support** - First-class async support with both sync and async methods
- 🔒 **Type Safety** - Full Pydantic models with IDE autocomplete
- 📝 **Config-Driven** - YAML-defined endpoints, easy to extend
- 🎯 **Better Errors** - Specific exception types with detailed context
- ⚡ **Efficient** - Single session management, proper resource cleanup
- 🎮 **Complete Coverage** - Supports WoW, Diablo 3, Hearthstone, and StarCraft 2

## Installation

```bash
pip install blizzardapi3
```

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

## Supported Games

- **World of Warcraft** - Game Data & Profile APIs
- **Diablo 3** - Community & Game Data APIs
- **Hearthstone** - Game Data API
- **StarCraft 2** - Community & Game Data APIs

## Migration from v2

See [MIGRATION.md](MIGRATION.md) for a detailed guide on migrating from blizzardapi2.

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
```

## Architecture

BlizzardAPI v3 uses a config-driven architecture:

- **YAML Endpoint Definitions** - All API endpoints defined in YAML configs
- **Dynamic Method Generation** - Methods generated at runtime from configs
- **Pydantic Models** - Type-safe response models
- **Custom Exceptions** - Detailed error hierarchy
- **Single Session** - Efficient session management with proper cleanup

## License

MIT License - see [LICENSE](LICENSE) for details

## Credits

Built with ❤️ by [lostcol0ny](https://github.com/lostcol0ny)

Powered by Claude Sonnet 4.5
