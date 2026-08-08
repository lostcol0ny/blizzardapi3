"""Namespace-kind checks across the whole endpoint layer, without touching the network.

The endpoint layer is hand-written by design. The cost of that choice is
copy-paste drift: a method reaches for ``_static_get`` where its siblings use
``_dynamic_get``, and silently queries the wrong namespace. Blizzard answers
such a request — with the wrong data, or with nothing — so the mistake survives
until a user notices. Issue #8 was exactly this, and its fix moved seasons and
periods to dynamic while leaving the two dungeon methods behind.

These tests re-derive every namespace by calling all of the endpoint methods
against a recording executor, so there is no table of expected values to keep in
sync with the code. The invariants are checked against the code itself.
"""

from __future__ import annotations

import asyncio
import inspect
import pkgutil
from collections import defaultdict
from importlib import import_module
from typing import Any, NamedTuple

import blizzardapi3.api


class Call(NamedTuple):
    cls: str
    method: str
    path: str
    namespace: str | None


class _RecordingExecutor:
    """Stands in for RequestExecutor, capturing the request instead of sending it."""

    def __init__(self) -> None:
        self.seen: list[tuple[str, str | None]] = []

    def execute(self, *, region: str, path: str, params: dict[str, Any], client: Any) -> dict[str, Any]:
        self.seen.append((path, params.get("namespace")))
        return {}

    async def execute_async(self, *, region: str, path: str, params: dict[str, Any], client: Any) -> dict[str, Any]:
        self.seen.append((path, params.get("namespace")))
        return {}


class _FakeClient:
    sync_client = None
    async_client = None


def _dummy(param: inspect.Parameter) -> Any:
    if param.name == "region":
        return "us"
    if param.name == "locale":
        return "en_US"
    return 1 if "int" in str(param.annotation) else "x"


def _endpoint_classes() -> list[type]:
    classes: list[type] = []
    for info in pkgutil.iter_modules(blizzardapi3.api.__path__):
        module = import_module(f"blizzardapi3.api.{info.name}")
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if cls.__module__ == module.__name__:
                classes.append(cls)
    return classes


def _record_every_endpoint() -> list[Call]:
    calls: list[Call] = []
    for cls in _endpoint_classes():
        executor = _RecordingExecutor()
        instance = cls(_FakeClient(), executor)
        for name, fn in inspect.getmembers(cls, inspect.isfunction):
            if name.startswith("_"):
                continue
            kwargs = {p.name: _dummy(p) for p in inspect.signature(fn).parameters.values() if p.name != "self"}
            before = len(executor.seen)
            result = getattr(instance, name)(**kwargs)
            if inspect.iscoroutine(result):
                asyncio.run(result)
            issued = len(executor.seen) - before
            assert issued == 1, f"{cls.__name__}.{name} issued {issued} requests, expected 1"
            path, namespace = executor.seen[-1]
            calls.append(Call(cls.__name__, name, path, namespace))
    return calls


CALLS = _record_every_endpoint()


def test_the_probe_reaches_the_whole_endpoint_layer():
    """Guards the tests below: they prove nothing if the probe stops finding methods."""
    assert len(CALLS) > 500


def test_sync_and_async_twins_issue_the_same_request():
    """A method and its _async twin are written separately, so they can drift separately."""
    by_name = {(c.cls, c.method): c for c in CALLS}
    problems: list[str] = []

    for (cls, method), call in by_name.items():
        if method.endswith("_async"):
            continue
        twin = by_name.get((cls, f"{method}_async"))
        if twin is None:
            problems.append(f"{cls}.{method} has no async twin")
        elif (twin.path, twin.namespace) != (call.path, call.namespace):
            problems.append(
                f"{cls}.{method} sends {call.path} {call.namespace}, "
                f"but its async twin sends {twin.path} {twin.namespace}"
            )

    assert problems == []


def test_a_resource_family_uses_one_namespace_kind():
    """Siblings under the same resource path agree, so an odd one out is a typo."""
    families: dict[tuple[str, str], set[str]] = defaultdict(set)

    for call in CALLS:
        # Search endpoints take the namespace of whatever they search, so
        # /data/wow/search/item is static while /data/wow/search/realm is
        # dynamic. Their mixture is correct rather than a drift.
        if call.namespace is None or call.path.startswith("/data/wow/search/"):
            continue
        family = "/".join(call.path.split("/")[:4])
        families[(call.cls, family)].add(call.namespace.split("-")[0])

    mixed = {family: kinds for family, kinds in families.items() if len(kinds) > 1}
    assert mixed == {}


def test_mythic_keystone_endpoints_are_dynamic():
    """Pinned rather than merely self-consistent: this family has drifted twice (#8).

    The consistency check above only catches a family that disagrees with
    itself, so it would pass if every keystone method were wrong together.
    """
    kinds = {
        call.path: call.namespace.split("-")[0]
        for call in CALLS
        if call.namespace and call.path.startswith("/data/wow/mythic-keystone/")
    }
    assert kinds, "probe found no mythic-keystone endpoints"
    assert set(kinds.values()) == {"dynamic"}, kinds
