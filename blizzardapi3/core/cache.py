"""In-process response cache that honors HTTP ``Cache-Control`` directives.

Blizzard marks static game data ``public, max-age=86400`` — a full day — so
the same achievement/item/realm fetch is a wasted round-trip until the next
patch. This cache reads that directive and serves the stored response until it
expires, turning every repeat into a dict lookup instead of an ~80 ms request.

Profile endpoints (character equipment, etc.) send *no* ``Cache-Control`` at
all, because gear changes. Those are never cached by default. A caller who
knows their tolerance for staleness can pass ``default_ttl`` to cache them for
a chosen number of seconds — but an explicit ``no-store``/``no-cache``/
``private`` from the server is always obeyed and never overridden.
"""

from __future__ import annotations

import threading
import time
from collections import OrderedDict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from .executor import ApiResponse

# (region, path, sorted (key, value) pairs) — two logically identical requests
# produce identical keys regardless of param ordering.
CacheKey = tuple[str, str, tuple[tuple[str, str], ...]]


def _make_key(region: str, path: str, params: dict[str, Any]) -> CacheKey:
    return (region, path, tuple(sorted((str(k), str(v)) for k, v in params.items())))


def _max_age(headers: dict[str, str], default: int | None) -> int | None:
    """Resolve a TTL in seconds from a response's ``Cache-Control``.

    Returns ``None`` (don't cache) when the server forbids it or no usable
    lifetime is available. ``default`` applies only when the header is absent —
    an explicit ``no-store``/``no-cache``/``private`` always wins.
    """
    cache_control = headers.get("cache-control")
    if cache_control is None:
        return default

    directives = [d.strip().lower() for d in cache_control.split(",")]
    if any(d in ("no-store", "no-cache", "private") for d in directives):
        return None

    for directive in directives:
        if directive.startswith("max-age="):
            try:
                age = int(directive.split("=", 1)[1])
            except ValueError:
                return default
            return age if age > 0 else None

    return default


class ResponseCache:
    """Thread-safe, bounded, TTL response cache keyed by request identity.

    Bounded by ``max_entries`` with least-recently-used eviction. Expiry uses a
    monotonic clock so it is immune to wall-clock adjustments.
    """

    def __init__(self, max_entries: int = 1024, default_ttl: int | None = None):
        self._store: OrderedDict[CacheKey, tuple[ApiResponse, float]] = OrderedDict()
        self._max_entries = max_entries
        self._default_ttl = default_ttl
        self._lock = threading.Lock()

    def get(self, region: str, path: str, params: dict[str, Any]) -> ApiResponse | None:
        key = _make_key(region, path, params)
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            response, expires_at = entry
            if time.monotonic() >= expires_at:
                del self._store[key]
                return None
            self._store.move_to_end(key)
            return response

    def store(self, region: str, path: str, params: dict[str, Any], response: ApiResponse) -> None:
        ttl = _max_age(response.headers, self._default_ttl)
        if ttl is None:
            return
        key = _make_key(region, path, params)
        with self._lock:
            self._store[key] = (response, time.monotonic() + ttl)
            self._store.move_to_end(key)
            while len(self._store) > self._max_entries:
                self._store.popitem(last=False)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()
