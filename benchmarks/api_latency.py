"""Latency benchmark for blizzardapi3 — measure before optimizing.

Answers two questions with real numbers, against the live Blizzard API:

  1. Repeat-call cost (the response-cache opportunity)
     The same static endpoint is fetched N times. There is no response cache
     today, so every repeat is a full network round-trip. The median here is
     what an in-memory/disk cache would turn into ~0ms on a hit.

  2. Serial vs concurrent fan-out (the batch-helper opportunity)
     The same set of connected-realm IDs is fetched serially (sync) and then
     concurrently (async + asyncio.gather, bounded by a semaphore). The ratio
     is the speedup a batch helper would unlock for bulk profile/game-data
     pulls.

Run it yourself so your credentials never leave your machine::

    export BLIZZARD_CLIENT_ID=...        # from develop.battle.net
    export BLIZZARD_CLIENT_SECRET=...
    uv run python benchmarks/api_latency.py

Nothing here is a permanent library change — it only reads the public API.
"""

from __future__ import annotations

import asyncio
import os
import statistics
import sys
import time

from blizzardapi3 import BlizzardAPI

REGION = "us"
LOCALE = "en_US"
REPEATS = 10          # how many times to refetch one static endpoint
FANOUT = 15           # how many connected realms to pull in the serial/concurrent test
MAX_CONCURRENCY = 10  # semaphore bound — stay well under Blizzard's 100 req/s


def _creds() -> tuple[str, str]:
    cid = os.environ.get("BLIZZARD_CLIENT_ID")
    secret = os.environ.get("BLIZZARD_CLIENT_SECRET")
    if not cid or not secret:
        sys.exit(
            "Set BLIZZARD_CLIENT_ID and BLIZZARD_CLIENT_SECRET in your environment.\n"
            "Get them at https://develop.battle.net → API Access."
        )
    return cid, secret


def _realm_id_from_href(href: str) -> int:
    """Index entries are {'href': '.../connected-realm/11?namespace=...'}."""
    return int(href.rstrip("/").split("/connected-realm/")[1].split("?")[0])


def _ms(seconds: float) -> str:
    return f"{seconds * 1000:7.1f} ms"


def repeat_latency(api: BlizzardAPI) -> None:
    """Test 1 — how expensive is refetching the same static resource."""
    timings: list[float] = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        api.wow.game_data.get_achievement(region=REGION, locale=LOCALE, achievement_id=6)
        timings.append(time.perf_counter() - t0)

    cold, warm = timings[0], timings[1:]
    print("\n[1] Repeat-call latency  (get_achievement, same args x%d)" % REPEATS)
    print(f"    cold (1st):   {_ms(cold)}   <- includes token fetch + new connection")
    print(f"    warm median:  {_ms(statistics.median(warm))}   <- pooled connection, but STILL a round-trip")
    print(f"    warm min/max: {_ms(min(warm))} / {_ms(max(warm))}")
    print(f"    => a response cache would make every repeat ~0ms instead of ~{_ms(statistics.median(warm)).strip()}")


def serial_fanout(api: BlizzardAPI, ids: list[int]) -> float:
    t0 = time.perf_counter()
    for rid in ids:
        api.wow.game_data.get_connected_realm(region=REGION, locale=LOCALE, connected_realm_id=rid)
    return time.perf_counter() - t0


async def concurrent_fanout(client_id: str, secret: str, ids: list[int]) -> float:
    sem = asyncio.Semaphore(MAX_CONCURRENCY)

    async with BlizzardAPI(client_id, secret, region=REGION) as api:
        async def one(rid: int) -> None:
            async with sem:
                await api.wow.game_data.get_connected_realm_async(
                    region=REGION, locale=LOCALE, connected_realm_id=rid
                )

        # Warm the token once so the gather measures request fan-out, not auth.
        await api.wow.game_data.get_connected_realms_index_async(region=REGION, locale=LOCALE)
        t0 = time.perf_counter()
        await asyncio.gather(*(one(rid) for rid in ids))
        return time.perf_counter() - t0


def main() -> None:
    client_id, secret = _creds()

    with BlizzardAPI(client_id, secret, region=REGION) as api:
        repeat_latency(api)

        index = api.wow.game_data.get_connected_realms_index(region=REGION, locale=LOCALE)
        ids = [_realm_id_from_href(e["href"]) for e in index["connected_realms"]][:FANOUT]
        n = len(ids)

        serial = serial_fanout(api, ids)

    concurrent = asyncio.run(concurrent_fanout(client_id, secret, ids))

    print(f"\n[2] Fan-out: fetch {n} connected realms")
    print(f"    serial (sync loop):       {_ms(serial)}  ({_ms(serial / n).strip()}/req)")
    print(f"    concurrent (gather, sem={MAX_CONCURRENCY}): {_ms(concurrent)}  ({_ms(concurrent / n).strip()}/req)")
    if concurrent > 0:
        print(f"    => concurrency speedup: {serial / concurrent:.1f}x for this batch size")

    print("\nInterpretation:")
    print("  - Big [1] warm number  -> response caching is the highest-leverage fix.")
    print("  - Big [2] speedup      -> a bounded-concurrency batch helper is worth adding.")


if __name__ == "__main__":
    main()
