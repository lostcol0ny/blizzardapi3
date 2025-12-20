"""Search Example - Demonstrate search functionality with pagination.

This example shows how to search for items using the WoW Game Data API
search endpoints with filtering and pagination.
"""

import os

from dotenv import load_dotenv

from blizzardapi3 import BlizzardAPI, Locale, Region


def main():
    """Demonstrate search functionality."""
    # Load environment variables from .env file
    load_dotenv()

    client_id = os.environ.get("BLIZZARD_CLIENT_ID")
    client_secret = os.environ.get("BLIZZARD_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("Error: Set BLIZZARD_CLIENT_ID and BLIZZARD_CLIENT_SECRET")
        return

    print("BlizzardAPI v3 - Search Examples")
    print("=" * 70)

    with BlizzardAPI(client_id, client_secret) as api:
        # Example 1: Basic search
        print("\nExample 1: Search for decor items containing 'wall'")
        print("-" * 70)

        results = api.wow.game_data.search_decor(region=Region.US, locale=Locale.EN_US, **{"name.en_US": "wall"})

        print(f"Found {len(results['results'])} items on page {results['page']}")
        print(f"Total pages: {results['pageCount']}\n")

        for i, result in enumerate(results["results"][:5], 1):
            data = result["data"]
            print(f"{i}. {data['name']['en_US']} (ID: {data['id']})")

        # Example 2: Pagination
        print("\n" + "=" * 70)
        print("Example 2: Paginated search with ordering")
        print("-" * 70)

        results = api.wow.game_data.search_decor(region=Region.US, locale=Locale.EN_US, orderby="id", _page=1)

        print(f"Page {results['page']} of {results['pageCount']}")
        print(f"Results per page: {results['pageSize']}")
        print(f"Items on this page: {len(results['results'])}\n")

        for i, result in enumerate(results["results"][:3], 1):
            data = result["data"]
            print(f"{i}. {data['name']['en_US']} (ID: {data['id']})")

        # Example 3: Search multiple resource types
        print("\n" + "=" * 70)
        print("Example 3: Search for mounts")
        print("-" * 70)

        mount_results = api.wow.game_data.search_mount(
            region=Region.US, locale=Locale.EN_US, **{"name.en_US": "dragon"}
        )

        print(f"Found {len(mount_results['results'])} mounts with 'dragon'\n")

        for i, result in enumerate(mount_results["results"][:5], 1):
            data = result["data"]
            print(f"{i}. {data['name']['en_US']} (ID: {data['id']})")


if __name__ == "__main__":
    main()
