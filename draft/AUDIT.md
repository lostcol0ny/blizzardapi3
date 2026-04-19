# API Coverage Audit

Source of truth: HTML exports from `community.developer.battle.net` saved
to `/mnt/c/Users/TobyD/Downloads/Blizzard API Docs/` (2026-04).
Tool: `/tmp/audit.py` — parses method panels, resolves YAML pattern templates,
normalizes placeholders.

## Summary table

| API surface            | Docs | YAML | Match | New | Stale | Action                       |
|------------------------|-----:|-----:|------:|----:|------:|------------------------------|
| WoW Game Data (retail) |  122 |  116 |   113 |  9* |     0 | Add Item Appearance + Neighborhood Map (done in draft) |
| WoW Profile (retail)   |   31 |   29 |    29 |   2 |     0 | Add character decor + character house |
| WoW Classic Game Data  |   44 |    0 |     0 |  n/a |     0 | **Classic is unreachable** — see Classic section |
| WoW Classic Profile    |   18 |    0 |     0 |  n/a |     0 | Same |
| D3 Game Data           |    6 |    6 |     0 |  n/a |     0 | Miscategorized — see D3 section |
| D3 Community (global)  |   14 |   14 |    14 |   0 |     0 | OK; category boundary fuzzy |
| D3 Community (CN)      |   14 |   14 |    14 |   0 |     0 | Same endpoints as global |
| SC2 Game Data          |    1 |    1 |     0 |  n/a |     1 | **Bug: wrong path prefix** |
| SC2 Community          |   14 |   14 |    14 |   0 |     0 | OK |
| Hearthstone            |    7 |    8 |     7 |   1 |     0 | Add query-param deck endpoint |

\* 9 discovered in earlier audit pass: Item Appearance ×6 (Set, Set Index, Set Slot,
Appearance, Appearance Slot, Appearance Index) + Neighborhood Map ×3 — all already
handled in the draft module.

## Critical issues

### 1. SC2 Game Data path prefix bug

`blizzardapi3/config/endpoints/sc2_game_data.yaml:9` declares:

```yaml
path_template: "/sc2/league/{season_id}/{queue_id}/{team_type}/{league_id}"
```

Docs specify `/data/sc2/league/...`. Current path returns 404 against the
live API. Add the `/data/` prefix.

### 2. WoW Classic is completely unreachable

- `blizzardapi3/core/factory.py:126-127` emits `{type}-classic-{region}` only —
  no support for `classic1x` (Era) or other Classic variants introduced
  since the factory was written.
- Every WoW YAML entry has `supports_classic: false`.
- Net effect: `WowClient(..., is_classic=True)` returns the retail namespace
  string regardless, so Classic calls fail or silently return retail data.
- Additionally, 8 endpoints are Classic-only and missing from the YAML
  entirely:
  - `/data/wow/connected-realm/{id}/auctions/index`
  - `/data/wow/connected-realm/{id}/auctions/{auctionHouseId}`
  - `/data/wow/pvp-region/index`
  - `/data/wow/pvp-region/{pvpRegionId}/pvp-season/index`
  - `/data/wow/pvp-region/{pvpRegionId}/pvp-season/{pvpSeasonId}`
  - `/data/wow/pvp-region/{pvpRegionId}/pvp-season/{pvpSeasonId}/pvp-leaderboard/index`
  - `/data/wow/pvp-region/{pvpRegionId}/pvp-season/{pvpSeasonId}/pvp-leaderboard/{pvpBracket}`
  - `/data/wow/pvp-region/{pvpRegionId}/pvp-season/{pvpSeasonId}/pvp-reward/index`

In the direct-Python refactor, the cleanest fix is a dedicated
`WowClassicGameData` / `WowClassicProfile` sub-API — most paths overlap
retail but the namespace token differs (`static-classic`, `static-classic1x`,
etc.) and a few endpoints are Classic-only. Separate classes avoid a
boolean flag that has to thread through every method.

### 3. D3 category boundary is wrong

- `d3_game_data.yaml` contains 6 endpoints that Blizzard's docs place
  under **Community** (artisan, follower, item, item-type, recipe).
- Those 6 are also duplicated in `d3_community.yaml`.
- Conversely, `d3_community.yaml` holds the 6 endpoints Blizzard documents
  as **Game Data**: Era/Season indexes and leaderboards.

Net: every path is reachable from *some* method on the D3 client, but the
categorization is inverted. In the refactor, collapse to one `D3API` surface
or mirror Blizzard's split. I recommend the former — the community/game-data
line is not meaningful for D3 (no namespace distinction, no auth
distinction).

## New endpoints to add

**WoW Profile** — two new Midnight-era endpoints:
- `/profile/wow/character/{realmSlug}/{characterName}/collections/decor`
  (character decor collection — account variant at
  `/profile/user/wow/collections/decor` already exists in YAML)
- `/profile/wow/character/{realmSlug}/{characterName}/house/house-{houseNumber}`
  (house inspection)

**Hearthstone** — new preferred deck retrieval variant:
- `GET /hearthstone/deck?code={url_encoded_deck_code}` — Blizzard recommends
  this over the existing `/hearthstone/deck/{deck_code}` path form (which
  breaks on `=` in deck codes). Keep both; mark the path form as legacy.

## Classic namespace variants (from guides)

Blizzard now exposes three Classic tracks, each with its own namespace token:

| Track                         | Static                      | Dynamic                      | Profile                     |
|-------------------------------|-----------------------------|------------------------------|-----------------------------|
| Era (Classic 1x)              | `static-classic1x-{region}` | `dynamic-classic1x-{region}` | `profile-classic1x-{region}`|
| Progression (MoP Classic)     | `static-classic-{region}`   | `dynamic-classic-{region}`   | `profile-classic-{region}`  |
| Anniversary (BCC)             | (TBD — check when released) | (TBD)                        | (TBD)                       |

The refactor should model these as an enum on the Classic sub-APIs:
`WowClassicGameData(client, executor, track=ClassicTrack.era)`.

## Search syntax (guide content not surfaced in the library)

`WoW Search` guide documents query operators that the current library
accepts via `**kwargs` but doesn't help the caller build:

- AND: multiple query params (implicit)
- OR: `field=a||b`
- NOT: `field!=value` (combines with OR: `race!=orc||human`)
- RANGE: `[min,max]` inclusive, `(min,max)` exclusive
- Reserved: `_page`, `_pageSize` (max 1000), `orderby`, `_tag`

Worth a docstring on each `search_*` method in the refactor pointing at
these operators. No code change needed — just documentation.

## Regionality reminders

- CN partition is completely separate: `gateway.battlenet.com.cn` + `oauth.battlenet.com.cn`.
  Existing `TokenManager._oauth_url(region)` handles this.
- Game data is per-region; the library already exposes `region` on every call.
- No Russian region (`ru`) — use `eu` with `ru_RU` locale.

## No-op findings

- SC2 Community: 14/14 match, clean.
- D3 Community CN: identical endpoint set to global D3 Community.
- Hearthstone metadata/search/cards: all covered.

## Recommended order of changes

1. **Bug fix** — add `/data/` prefix to `sc2_game_data.yaml` (`v3.0.6` patch release).
2. **New endpoints** — add WoW character-decor, character-house, HS deck query
   variant to the current YAML-based release (`v3.1.0`).
3. **Refactor** — dump YAMLs; in the direct-Python rewrite, split Classic
   into its own sub-API and collapse D3 community/game-data into one class.
