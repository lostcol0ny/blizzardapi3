# OAuth Authorization Guide

This guide explains how to use OAuth authentication with BlizzardAPI v3 for user-specific endpoints.

## Table of Contents

- [Overview](#overview)
- [Client Credentials vs Authorization Code Flow](#client-credentials-vs-authorization-code-flow)
- [Quick Start](#quick-start)
- [Step-by-Step Guide](#step-by-step-guide)
- [Using Access Tokens](#using-access-tokens)
- [OAuth Scopes](#oauth-scopes)
- [Troubleshooting](#troubleshooting)

## Overview

Blizzard API uses two OAuth flows:

1. **Client Credentials** - Used for public game data (achievements, items, etc.)
2. **Authorization Code Flow** - Required for user-specific data (account profiles, private collections)

BlizzardAPI v3 handles client credentials automatically. For authorization code flow, you need to obtain a user access token manually.

## Client Credentials vs Authorization Code Flow

### Client Credentials (Automatic)

Used for public endpoints. BlizzardAPI handles this automatically:

```python
from blizzardapi3 import BlizzardAPI, Region, Locale

# Automatically gets client credentials token
with BlizzardAPI(client_id, client_secret) as api:
    achievement = api.wow.game_data.get_achievement(
        region=Region.US,
        locale=Locale.EN_US,
        achievement_id=6
    )
```

**Endpoints using client credentials:**
- Game Data APIs (achievements, items, mounts, etc.)
- Public character profiles
- Guild information
- Most search endpoints

### Authorization Code Flow (Manual)

Required for user-specific endpoints. Requires user authorization:

```python
# Need to provide user access token
with BlizzardAPI(client_id, client_secret) as api:
    profile = api.wow.profile.get_account_profile_summary(
        region=Region.US,
        locale=Locale.EN_US,
        access_token=user_access_token  # Required!
    )
```

**Endpoints requiring authorization code flow:**
- Account profile summaries
- Account collections (private mounts, pets)
- Protected character profiles
- User-specific data

## Quick Start

### Step 1: Configure Redirect URI

You can use either:

**Option A: Use the standard Battle.net redirect (Recommended for simplicity)**
- Redirect URI: `https://community.developer.battle.net/`
- No local server needed
- Manually copy the authorization code from URL

**Option B: Use localhost callback**
- Redirect URI: `http://localhost:8080/callback`
- Automated callback handling
- Requires running local server

Configure in your Battle.net application:
1. Go to https://develop.battle.net/access/clients
2. Select your application
3. Add your chosen redirect URI
4. Save changes

### Step 2: Get Authorization Code

**Using Option A (Battle.net redirect):**

```bash
# Generate authorization URL
python get_oauth_url.py

# Visit the URL shown, authorize, then copy the code from the redirect URL
# Example: https://community.developer.battle.net/?code=USxxxxx

# Exchange the code for a token
python exchange_code.py YOUR_CODE_HERE
```

**Using Option B (localhost):**

```bash
python oauth_helper.py
```

This will:
1. Open your browser for authorization
2. Start a local server to receive the callback
3. Exchange the authorization code for an access token
4. Save the token to `access_token.txt`

### Step 3: Use the Token

```python
from blizzardapi3 import BlizzardAPI, Region, Locale

# Load the saved token
with open('access_token.txt') as f:
    access_token = f.read().strip()

# Use it with the API
with BlizzardAPI(client_id, client_secret) as api:
    profile = api.wow.profile.get_account_profile_summary(
        region=Region.US,
        locale=Locale.EN_US,
        access_token=access_token
    )

    print(f"Account ID: {profile['id']}")
    print(f"WoW Accounts: {len(profile['wow_accounts'])}")
```

## Step-by-Step Guide

### 1. Configure Your Application

Before starting, ensure your Battle.net application is configured:

1. **Create an Application** (if you haven't):
   - Go to https://develop.battle.net/access/clients
   - Click "Create Client"
   - Choose "Web Application"
   - Fill in the details

2. **Add Redirect URI**:
   - In your application settings
   - Add: `http://localhost:8080/callback`
   - Save changes

3. **Note Your Credentials**:
   - Client ID
   - Client Secret
   - Keep these secure!

### 2. Understanding the OAuth Flow

The authorization code flow has 4 steps:

```
1. Your App                 →  Authorization URL  →  Battle.net
   (Redirect user)

2. Battle.net              →  User Login/Approve  →  User
   (User authorizes)

3. Battle.net              →  Redirect + Code     →  Your App
   (Authorization code)

4. Your App                →  Exchange Code       →  Battle.net
   (Gets access token)
```

### 3. Using the OAuth Helper Script

The `oauth_helper.py` script automates this flow:

```bash
python oauth_helper.py
```

**What happens:**

1. **Browser Opens**: You're redirected to Battle.net login
2. **Login/Authorize**: Log in and approve the application
3. **Redirect**: Battle.net redirects back to localhost
4. **Token Exchange**: Script exchanges code for token
5. **Save**: Token saved to `access_token.txt`

**Interactive Prompts:**

```
Select region:
  1. US (Americas)
  2. EU (Europe)
  3. KR (Korea)
  4. TW (Taiwan)

Enter choice (1-4, default=1): 1

Enter callback port (default=8080): 8080

Press ENTER when ready to continue...
```

### 4. Manual OAuth Implementation

If you want to implement OAuth yourself:

```python
import requests
from urllib.parse import urlencode

# Step 1: Build authorization URL
auth_params = {
    'client_id': client_id,
    'redirect_uri': 'http://localhost:8080/callback',
    'response_type': 'code',
    'scope': 'wow.profile',
}
auth_url = f"https://us.battle.net/oauth/authorize?{urlencode(auth_params)}"

# Step 2: User visits auth_url and authorizes
# (You'll receive authorization code via redirect)

# Step 3: Exchange code for token
token_response = requests.post(
    'https://us.battle.net/oauth/token',
    auth=(client_id, client_secret),
    data={
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': 'http://localhost:8080/callback',
    }
)

token_data = token_response.json()
access_token = token_data['access_token']
```

## Using Access Tokens

### Passing Tokens to Endpoints

All profile endpoints that require OAuth accept an `access_token` parameter:

```python
from blizzardapi3 import BlizzardAPI, Region, Locale

with BlizzardAPI(client_id, client_secret) as api:
    # Account profile summary
    profile = api.wow.profile.get_account_profile_summary(
        region=Region.US,
        locale=Locale.EN_US,
        access_token=access_token
    )

    # Account mounts
    mounts = api.wow.profile.get_account_mounts_collection_summary(
        region=Region.US,
        locale=Locale.EN_US,
        access_token=access_token
    )

    # Account pets
    pets = api.wow.profile.get_account_pets_collection_summary(
        region=Region.US,
        locale=Locale.EN_US,
        access_token=access_token
    )
```

### Token Expiration

Access tokens expire after a certain time (usually 24 hours):

```python
import time
from pathlib import Path

def get_fresh_token():
    """Check if token is fresh, otherwise prompt for new one."""
    token_file = Path('access_token.txt')

    if not token_file.exists():
        print("No token found. Run: python oauth_helper.py")
        return None

    # Check file modification time
    token_age = time.time() - token_file.stat().st_mtime

    if token_age > 86400:  # 24 hours
        print("Token may be expired. Consider getting a new one.")

    with open(token_file) as f:
        return f.read().strip()
```

### Refreshing Tokens

If you want to implement token refresh (advanced):

```python
# When you get the initial token, save the refresh_token
token_response = {
    'access_token': 'USxxx...',
    'refresh_token': 'USyyy...',
    'expires_in': 86400
}

# Later, when token expires:
refresh_response = requests.post(
    'https://us.battle.net/oauth/token',
    auth=(client_id, client_secret),
    data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
)

new_token_data = refresh_response.json()
```

## OAuth Scopes

Different endpoints require different scopes:

| Scope | Description | Endpoints |
|-------|-------------|-----------|
| `wow.profile` | World of Warcraft profile access | Account profile, collections |
| `sc2.profile` | StarCraft 2 profile access | SC2 account data |
| `d3.profile` | Diablo 3 profile access | D3 account data |
| `openid` | Basic user identification | User ID |

### Requesting Multiple Scopes

```python
auth_params = {
    'client_id': client_id,
    'redirect_uri': redirect_uri,
    'response_type': 'code',
    'scope': 'wow.profile sc2.profile',  # Space-separated
}
```

### Scope Requirements by Endpoint

**WoW Profile Endpoints (require `wow.profile`):**
- `get_account_profile_summary()`
- `get_account_collections_index()`
- `get_account_mounts_collection_summary()`
- `get_account_pets_collection_summary()`
- `get_account_heirlooms_collection_summary()`
- `get_account_toys_collection_summary()`
- `get_account_transmog_collection_summary()`
- `get_protected_character_profile_summary()`

**Public Endpoints (no scope required):**
- All game data endpoints
- Public character profiles
- Guild information

## Troubleshooting

### Issue: Redirect URI Mismatch

**Error**: `redirect_uri_mismatch`

**Solution**:
1. Check your Battle.net application settings
2. Ensure redirect URI is exactly: `http://localhost:8080/callback`
3. No trailing slash
4. Correct port number
5. Save changes and wait a few minutes

### Issue: Invalid Scope

**Error**: `invalid_scope`

**Solution**:
- Verify scope name is correct: `wow.profile` (not `wow_profile`)
- Ensure your application has permission for that scope
- Some scopes may be restricted

### Issue: Token Expired

**Error**: 401 Unauthorized

**Solution**:
```python
# Get a fresh token
from oauth_helper import get_user_access_token

token_response = get_user_access_token(client_id, client_secret, region="us")
access_token = token_response['access_token']
```

### Issue: Port Already in Use

**Error**: `OSError: [Errno 48] Address already in use`

**Solution**:
```python
# Use a different port
python oauth_helper.py
# When prompted, enter: 8081
```

Or find and kill the process using port 8080:
```bash
# Windows
netstat -ano | findstr :8080
taskkill /PID <pid> /F

# Linux/Mac
lsof -ti:8080 | xargs kill
```

### Issue: No Authorization Code Received

**Checklist**:
1. ✓ Redirect URI configured in Battle.net app
2. ✓ Port not blocked by firewall
3. ✓ Browser opened the authorization URL
4. ✓ You clicked "Authorize" on Battle.net
5. ✓ Redirected back to localhost
6. ✓ Local server was running

### Issue: HTTPS Required

Some environments require HTTPS. For production:

1. Use a proper domain with HTTPS
2. Deploy a web server to handle OAuth callback
3. Store tokens securely (not in plain text files)

**Production Example**:
```python
redirect_uri = "https://yourdomain.com/oauth/callback"
```

## Best Practices

### 1. Secure Token Storage

Don't commit tokens to version control:

```bash
# Add to .gitignore
access_token.txt
.env
```

### 2. Token Validation

Check if token is still valid:

```python
def validate_token(access_token, region="us"):
    """Check if token is valid."""
    url = "https://oauth.battle.net/oauth/check_token"

    response = requests.post(
        url,
        data={'token': access_token}
    )

    return response.status_code == 200
```

### 3. Error Handling

Handle token errors gracefully:

```python
from blizzardapi3.exceptions import ForbiddenError

try:
    profile = api.wow.profile.get_account_profile_summary(
        region=Region.US,
        locale=Locale.EN_US,
        access_token=access_token
    )
except ForbiddenError:
    print("Token expired or invalid. Please re-authorize.")
    # Trigger new OAuth flow
```

### 4. User Privacy

Be transparent about data access:
- Clearly state what data you're accessing
- Only request scopes you actually need
- Provide way for users to revoke access

## Testing OAuth Flow

Test script provided: `test_account_profile.py`

```bash
# 1. Get token
python oauth_helper.py

# 2. Test endpoint
python test_account_profile.py
```

Expected output:
```
Testing Account Profile Summary Endpoint
======================================================================

Fetching account profile summary...

✓ SUCCESS! Retrieved account profile
======================================================================
Account ID: 12345678

WoW Accounts: 1

  Account 1:
    ID: 87654321
    Characters: 15
      - Beyloc (Level 80 Warlock on Illidan)
      - ... and 14 more

======================================================================
Account Profile API is working correctly!
======================================================================
```

## Additional Resources

- [Blizzard OAuth Documentation](https://develop.battle.net/documentation/guides/using-oauth)
- [Battle.net Developer Portal](https://develop.battle.net)
- [OAuth 2.0 Specification](https://oauth.net/2/)

## Summary

1. **Configure** your Battle.net application with redirect URI
2. **Run** `oauth_helper.py` to get user access token
3. **Use** the token with OAuth-required endpoints
4. **Handle** token expiration and errors gracefully

For most use cases, the provided `oauth_helper.py` script is sufficient. For production applications, implement proper token storage, refresh logic, and error handling.
