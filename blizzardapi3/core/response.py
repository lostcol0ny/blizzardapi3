"""The response value types.

Two types, one seam. :class:`RawResponse` is the undecoded material every
internal path carries around — the transport produces it, the cache stores it,
and coalesced callers share it. :class:`ApiResponse` is what a caller receives,
and it is built by :meth:`RawResponse.parse` at the moment of hand-off.

Splitting them is what makes the cache safe to hand out. A parsed response is a
mutable tree; if the cache handed out the same one twice, one caller's
``resp["realms"][0]["name"] = ...`` would silently rewrite what the next caller
reads. Storing bytes means every reader parses its own tree, so there is nothing
shared left to corrupt.
"""

from __future__ import annotations

import json
from typing import Any, NamedTuple


class ApiResponse(dict):
    """dict with ``.headers`` and ``.status_code`` attached.

    Preserves v3's bracket-access contract while exposing HTTP metadata.
    """

    def __init__(self, data: dict[str, Any], headers: dict[str, str], status_code: int):
        super().__init__(data)
        self._headers = headers
        self._status_code = status_code

    @property
    def headers(self) -> dict[str, str]:
        return self._headers

    @property
    def status_code(self) -> int:
        return self._status_code


class RawResponse(NamedTuple):
    """A successful response before it is decoded, safe to share and store."""

    body: bytes
    headers: dict[str, str]
    status_code: int

    def parse(self) -> ApiResponse:
        """Build a fresh :class:`ApiResponse` owned solely by the caller."""
        return ApiResponse(json.loads(self.body), dict(self.headers), self.status_code)
