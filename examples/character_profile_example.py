"""Character Profile Example - Fetch public character information.

This example demonstrates fetching character profile data using the
WoW Profile API. No OAuth token required for public character data.
"""

import os

from dotenv import load_dotenv

from blizzardapi3 import BlizzardAPI, Locale, Region


def main():
    """Fetch and display character profile information."""
    # Load environment variables from .env file
    load_dotenv()

    client_id = os.environ.get("BLIZZARD_CLIENT_ID")
    client_secret = os.environ.get("BLIZZARD_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("Error: Set BLIZZARD_CLIENT_ID and BLIZZARD_CLIENT_SECRET")
        print("Create a .env file in the project root with your credentials")
        return

    # Character to look up
    realm = "illidan"
    character = "beyloc"

    print(f"Fetching character profile: {character.title()}-{realm.title()}")
    print("=" * 70)

    with BlizzardAPI(client_id, client_secret) as api:
        # Get character appearance
        appearance = api.wow.profile.get_character_appearance_summary(
            region=Region.US, locale=Locale.EN_US, realm_slug=realm, character_name=character
        )

        print(f"\nCharacter: {appearance['character']['name']}")
        print(f"Realm: {appearance['character']['realm']['name']}")
        print(f"Race: {appearance['playable_race']['name']}")
        print(f"Class: {appearance['playable_class']['name']}")
        print(f"Spec: {appearance['active_spec']['name']}")
        print(f"Gender: {appearance['gender']['name']}")
        print(f"Faction: {appearance['faction']['name']}")

        # Get character equipment
        print("\n" + "=" * 70)
        print("Equipment")
        print("=" * 70)

        equipment = api.wow.profile.get_character_equipment_summary(
            region=Region.US, locale=Locale.EN_US, realm_slug=realm, character_name=character
        )

        for item in equipment["equipped_items"][:5]:  # Show first 5 items
            slot = item["slot"]["name"]
            name = item["name"]
            quality = item["quality"]["name"]
            level = item.get("level", {}).get("value", "N/A")
            print(f"  {slot}: {name} ({quality}, ilvl {level})")

        if len(equipment["equipped_items"]) > 5:
            print(f"  ... and {len(equipment['equipped_items']) - 5} more items")


if __name__ == "__main__":
    main()
