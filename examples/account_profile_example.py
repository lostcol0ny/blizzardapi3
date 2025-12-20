"""Account Profile Example - Fetch user account data (OAuth required).

This example demonstrates accessing user-specific account profile data
using an OAuth access token.

Prerequisites:
    1. Run oauth_example.py to get an access token
    2. The token will be saved to access_token.txt
"""

import os
from pathlib import Path

from dotenv import load_dotenv

from blizzardapi3 import BlizzardAPI, Locale, Region


def main():
    """Fetch and display account profile information."""
    # Load environment variables from .env file
    load_dotenv()

    client_id = os.environ.get("BLIZZARD_CLIENT_ID")
    client_secret = os.environ.get("BLIZZARD_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("Error: Set BLIZZARD_CLIENT_ID and BLIZZARD_CLIENT_SECRET")
        return

    # Load access token
    token_file = Path(__file__).parent.parent / "access_token.txt"
    if not token_file.exists():
        print("\nNo access token found!")
        print("Please run: python examples/oauth_example.py")
        return

    with open(token_file) as f:
        access_token = f.read().strip()

    print("Fetching Account Profile Summary")
    print("=" * 70)

    try:
        with BlizzardAPI(client_id, client_secret) as api:
            # Get account profile with OAuth token
            profile = api.wow.profile.get_account_profile_summary(
                region=Region.US, locale=Locale.EN_US, access_token=access_token
            )

            # Display account information
            print(f"\nAccount ID: {profile['id']}")

            if "wow_accounts" in profile:
                print(f"\nWoW Accounts: {len(profile['wow_accounts'])}")

                for i, wow_account in enumerate(profile["wow_accounts"], 1):
                    print(f"\n  Account {i}:")
                    print(f"    ID: {wow_account['id']}")

                    if "characters" in wow_account:
                        char_count = len(wow_account["characters"])
                        print(f"    Characters: {char_count}")

                        # Show sample characters
                        for char in wow_account["characters"][:5]:
                            realm = char.get("realm", {}).get("name", "Unknown")
                            level = char.get("level", "?")
                            char_class = char.get("playable_class", {}).get("name", "Unknown")
                            name = char.get("name", "Unknown")
                            print(f"      - {name} (Level {level} {char_class} on {realm})")

                        if char_count > 5:
                            print(f"      ... and {char_count - 5} more")

            if "collections" in profile:
                print(f"\nCollections: {profile['collections']['href']}")

            if "houses" in profile:
                print("Houses data available: Yes")

            print("\n" + "=" * 70)
            print("Account Profile retrieved successfully!")
            print("=" * 70)

    except Exception as e:
        print(f"\n[ERROR] {e}")

        if "401" in str(e) or "Forbidden" in str(e):
            print("\nToken may be expired. Get a new one with:")
            print("python examples/oauth_example.py")


if __name__ == "__main__":
    main()
