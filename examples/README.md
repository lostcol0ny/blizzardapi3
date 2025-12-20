# BlizzardAPI v3 - Examples

This directory contains example scripts demonstrating various features of BlizzardAPI v3.

## Examples

### OAuth Authorization

**[oauth_example.py](oauth_example.py)** - Complete OAuth authorization code flow example
- Shows how to obtain user access tokens
- Demonstrates using tokens with account profile endpoints
- Includes both manual and automated approaches

### Character Profile

**[character_profile_example.py](character_profile_example.py)** - Fetch character information
- Get character appearance, equipment, and stats
- Public character profile access (no OAuth required)

### Search

**[search_example.py](search_example.py)** - Search functionality examples
- Search for decor items by name
- Pagination through results
- Advanced filtering

### Account Profile

**[account_profile_example.py](account_profile_example.py)** - User account data (OAuth required)
- Get account profile summary
- List all WoW accounts and characters
- Access collections data

## Running Examples

1. **Install dependencies:**
   ```bash
   # Using uv (recommended)
   uv pip install -e ".[examples]"

   # Or using pip
   pip install -e .
   pip install python-dotenv
   ```

2. **Set up credentials:**
   ```bash
   # Create .env file in project root
   BLIZZARD_CLIENT_ID=your_client_id
   BLIZZARD_CLIENT_SECRET=your_client_secret
   ```

3. **Run an example:**
   ```bash
   python examples/character_profile_example.py
   ```

## OAuth Examples

For examples requiring OAuth (account profile, collections):

1. **Get authorization URL:**
   ```bash
   python examples/oauth_example.py
   ```

2. **Follow the instructions** to authorize and get an access token

3. **Run OAuth-required examples:**
   ```bash
   python examples/account_profile_example.py
   ```

## Additional Resources

- [OAuth Guide](../docs/OAUTH_GUIDE.md) - Complete OAuth documentation
- [Search Guide](../docs/SEARCH_GUIDE.md) - Search functionality guide
- [API Reference](../README.md) - Main documentation
