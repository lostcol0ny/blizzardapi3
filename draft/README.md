# Refactor Draft

Sample code showing what the "dump YAML / direct-code endpoints" refactor
would look like. Nothing here is wired into the real package — read it as
a design proposal, not runnable code.

## Files

| File | Purpose |
|------|---------|
| `core/auth.py`   | `TokenManager` — OAuth token caching. One class, sync + async methods share `_store()`. |
| `core/executor.py` | `RequestExecutor` — the one `_request` helper. Sync and async execute paths are ~15 lines each; all error translation is in the shared `_decode()` function. |
| `core/client.py` | `BaseClient` — owns the two httpx sessions and the token manager. Context-manager-only cleanup (no `__del__`). |
| `api/wow_game_data.py` | Representative WoW Game Data endpoints (retail). ~25 of 122 methods, including the new Item Appearance and Neighborhood Map families. |
| `api/wow_profile.py` | Representative WoW Profile endpoints. Character, account, and guild methods, including the new character decor + character house Midnight additions. |
| `api/wow_classic.py` | Classic Game Data + Classic-only endpoints. Parameterized on `ClassicTrack` (era/progression/anniversary) so the namespace token is correct for each track. |
| `api/hearthstone.py` | Full Hearthstone surface (cards, card backs, decks, metadata), including both the recommended query-param deck form and the legacy path form. |
| `api/wow.py` | Facade composing WoW retail + Classic sub-APIs. Replaces the dynamic `setattr` loops in the current `api/wow.py`. |

## Key design decisions

**httpx instead of requests + aiohttp.** One HTTP dependency. `httpx.Client`
and `httpx.AsyncClient` have nearly identical APIs, and `Response.json()`
is synchronous in both paths — that's what lets `_decode()` be a single
shared function. Drops `requests` and `aiohttp`.

**Four helpers, not one.** Every endpoint in `wow_game_data.py` delegates
to one of `_static_get`, `_static_get_async`, `_dynamic_get`, `_dynamic_get_async`.
Each endpoint body is 1-2 lines. The `_normalize()` module function handles
region/locale enum coercion and namespace string building.

**Paired sync + async methods, no magic.** `get_achievement` / `get_achievement_async`.
The duplication is ~6 lines per pair, and IDEs see real function signatures.

**Pydantic and PyYAML are gone.** With endpoints as code, there's nothing
to parse or validate at import time. `pydantic` and `pyyaml` come off the
dependency list.

**Classic is its own class, not a `bool` flag.** The v3.0 factory used
`is_classic: bool = False` on every method and only ever produced the
`static-classic-{region}` token — so Era (`classic1x`) and Anniversary
tracks were silently unreachable. `WowClassic(track=ClassicTrack.era)`
makes the track explicit, handles the Classic-only endpoints (multi-house
auctions, `pvp-region` hierarchy) that don't exist on retail, and keeps
retail methods simpler.

## What gets deleted from the real package

- `blizzardapi3/core/factory.py` (~380 lines)
- `blizzardapi3/core/registry.py` (~200 lines)
- `blizzardapi3/core/context.py` (~25 lines)
- `blizzardapi3/config/endpoints/*.yaml` (~2,000 lines)
- `blizzardapi3/**/*.pyi` (~5,300 lines)
- `scripts/generate_stubs.py` (whatever lines)
- `pydantic` + `pyyaml` from `pyproject.toml`

## What replaces it

- Direct endpoint modules totaling roughly 2,500-3,000 lines of real Python
  across the four games. Each endpoint self-documents via its signature
  and docstring; IDEs see everything natively.

## Open question

The sync + async duplication is still ~6 lines per endpoint × ~363 endpoints
= ~2,200 lines of "almost-identical method bodies." That's the price of
explicit, discoverable API. The alternative — a single "awaitable spec"
returned from each endpoint that the caller `.sync()`s or `await`s — breaks
the current public API and is arguably less ergonomic. Recommend we accept
the duplication.
