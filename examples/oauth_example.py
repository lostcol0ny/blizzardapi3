"""OAuth Example - Obtain user access tokens for account profile endpoints.

This example demonstrates the OAuth authorization code flow for accessing
user-specific endpoints like account profile summaries.

Usage:
    1. Run this script to get the authorization URL
    2. Visit the URL and authorize
    3. Copy the code from the redirect URL
    4. Run: python oauth_example.py YOUR_CODE_HERE
"""

import json
import os
import sys
from pathlib import Path
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv


def generate_auth_url(client_id, region="us"):
    """Generate OAuth authorization URL."""
    redirect_uri = "https://community.developer.battle.net/"

    auth_params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "wow.profile",
    }

    auth_url = f"https://{region}.battle.net/oauth/authorize?{urlencode(auth_params)}"
    return auth_url


def exchange_code_for_token(code, client_id, client_secret, region="us"):
    """Exchange authorization code for access token."""
    redirect_uri = "https://community.developer.battle.net/"
    token_url = f"https://{region}.battle.net/oauth/token"

    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
    }

    response = requests.post(token_url, auth=(client_id, client_secret), data=token_data, timeout=10)

    if response.status_code != 200:
        raise Exception(f"Token request failed ({response.status_code}): {response.text}")

    return response.json()


def main():
    """Main OAuth flow."""
    # Load environment variables from .env file
    load_dotenv()

    client_id = os.environ.get("BLIZZARD_CLIENT_ID")
    client_secret = os.environ.get("BLIZZARD_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("Error: Set BLIZZARD_CLIENT_ID and BLIZZARD_CLIENT_SECRET")
        return

    print("=" * 70)
    print("OAuth Authorization Code Flow")
    print("=" * 70)

    if len(sys.argv) < 2:
        # Step 1: Generate authorization URL
        auth_url = generate_auth_url(client_id)

        print("\nStep 1: Visit this URL to authorize:")
        print(f"\n{auth_url}\n")
        print("Step 2: After authorizing, copy the 'code' from the redirect URL")
        print("Example: https://community.developer.battle.net/?code=USxxxxx")
        print("\nStep 3: Run this script with the code:")
        print(f"python {sys.argv[0]} YOUR_CODE_HERE")
        print("=" * 70)

    else:
        # Step 2: Exchange code for token
        code = sys.argv[1]

        print("\nExchanging authorization code for access token...")

        try:
            token_response = exchange_code_for_token(code, client_id, client_secret)

            print("\n[OK] Access token obtained!")
            print(f"Token: {token_response['access_token'][:30]}...")
            print(f"Expires in: {token_response['expires_in']} seconds")

            # Save token
            token_file = Path(__file__).parent.parent / "access_token.txt"
            with open(token_file, "w") as f:
                f.write(token_response["access_token"])

            token_json_file = Path(__file__).parent.parent / "access_token.json"
            with open(token_json_file, "w") as f:
                json.dump(token_response, f, indent=2)

            print(f"\nToken saved to: {token_file}")
            print(f"Full response: {token_json_file}")
            print("\nYou can now run: python examples/account_profile_example.py")
            print("=" * 70)

        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    main()
