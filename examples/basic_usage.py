"""Basic usage example for BlizzardAPI v3."""

import asyncio

from blizzardapi3 import BlizzardAPI, Locale, Region

# Replace with your actual credentials
CLIENT_ID = "your_client_id_here"
CLIENT_SECRET = "your_client_secret_here"


def sync_example():
    """Example of synchronous API usage."""
    print("=== Synchronous Example ===")

    with BlizzardAPI(CLIENT_ID, CLIENT_SECRET) as api:
        # Get an achievement
        achievement = api.wow.game_data.get_achievement(
            region=Region.US, locale=Locale.EN_US, achievement_id=6
        )
        print(f"Achievement: {achievement.get('name', {}).get('en_US')}")

        # Search for decor items
        decor_results = api.wow.game_data.search_decor(
            region="us", locale="en_US", name_en_US="Fireplace"
        )
        print(f"Found {len(decor_results.get('results', []))} decor items")


async def async_example():
    """Example of asynchronous API usage."""
    print("\n=== Asynchronous Example ===")

    async with BlizzardAPI(CLIENT_ID, CLIENT_SECRET) as api:
        # Get an achievement asynchronously
        achievement = await api.wow.game_data.get_achievement_async(
            region=Region.US, locale=Locale.EN_US, achievement_id=6
        )
        print(f"Achievement: {achievement.get('name', {}).get('en_US')}")

        # Get multiple items concurrently
        tasks = [
            api.wow.game_data.get_achievement_async(
                region="us", locale="en_US", achievement_id=i
            )
            for i in range(1, 6)
        ]
        achievements = await asyncio.gather(*tasks, return_exceptions=True)
        print(f"Fetched {len([a for a in achievements if not isinstance(a, Exception)])} achievements concurrently")


def error_handling_example():
    """Example of error handling."""
    print("\n=== Error Handling Example ===")

    from blizzardapi3.exceptions import NotFoundError, RateLimitError

    with BlizzardAPI(CLIENT_ID, CLIENT_SECRET) as api:
        try:
            # Try to get a non-existent achievement
            api.wow.game_data.get_achievement(
                region="us", locale="en_US", achievement_id=999999999
            )
        except NotFoundError as e:
            print(f"Caught NotFoundError: {e}")
        except RateLimitError as e:
            print(f"Rate limited! Retry after {e.retry_after} seconds")


if __name__ == "__main__":
    # Run synchronous example
    sync_example()

    # Run async example
    asyncio.run(async_example())

    # Run error handling example
    error_handling_example()
