#!/usr/bin/env python3
"""Generate .pyi stub files from YAML endpoint configurations.

This script reads all YAML endpoint configs and generates type stub files
that provide IDE autocomplete for dynamically generated API methods.

Usage:
    python scripts/generate_stubs.py
"""

from pathlib import Path

import yaml


def get_param_type(param: str) -> str:
    """Get type hint for a parameter name."""
    if param == "region":
        return "str | Region"
    if param == "locale":
        return "str | Locale"
    if param == "access_token":
        return "str | None"
    if "_id" in param or param.endswith("_id"):
        return "int"
    return "str"


def generate_method_stub(
    method_name: str,
    params: list[str],
    description: str,
    is_async: bool = False,
    accepts_kwargs: bool = False,
    include_is_classic: bool = True,
) -> str:
    """Generate a method stub signature."""
    # Build parameter list
    param_strs = ["self"]
    param_strs.append("*")  # Force keyword-only args

    for param in params:
        param_type = get_param_type(param)
        if param == "access_token":
            param_strs.append(f"{param}: {param_type} = None")
        else:
            param_strs.append(f"{param}: {param_type}")

    # Add is_classic for WoW endpoints only
    if include_is_classic:
        param_strs.append("is_classic: bool = False")

    # Add **kwargs for search methods
    if accepts_kwargs:
        param_strs.append("**kwargs: Any")

    params_str = ",\n        ".join(param_strs)

    # Build method signature
    if is_async:
        prefix = "async def"
        name = f"{method_name}_async"
    else:
        prefix = "def"
        name = method_name

    return f'''    {prefix} {name}(
        {params_str},
    ) -> ApiResponse:
        """{description}."""
        ...
'''


def load_yaml_config(yaml_path: Path) -> dict:
    """Load a YAML configuration file."""
    with open(yaml_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_endpoint_params(endpoint: dict, patterns: dict) -> tuple[list[str], bool]:
    """Get parameters for an endpoint, resolving pattern if needed."""
    # Check if endpoint has custom params
    if endpoint.get("params"):
        params = endpoint["params"].copy()
    elif endpoint.get("pattern") and patterns:
        pattern = patterns.get(endpoint["pattern"], {})
        params = pattern.get("params", ["region", "locale"]).copy()
    else:
        params = ["region", "locale"]

    # Handle param_name substitution (e.g., 'id' -> 'achievement_id')
    if endpoint.get("param_name") and "id" in params:
        idx = params.index("id")
        params[idx] = endpoint["param_name"]

    # Check if accepts kwargs
    accepts_kwargs = endpoint.get("accepts_kwargs", False)
    if not accepts_kwargs and endpoint.get("pattern") and patterns:
        pattern = patterns.get(endpoint["pattern"], {})
        accepts_kwargs = pattern.get("accepts_kwargs", False)

    return params, accepts_kwargs


def generate_api_class_stub(
    class_name: str,
    endpoints: list[dict],
    patterns: dict,
    include_is_classic: bool = True,
) -> str:
    """Generate stub for an API class."""
    methods = []

    for endpoint in endpoints:
        method_name = endpoint["method_name"]
        description = endpoint.get("description", f"Call {method_name}")
        params, accepts_kwargs = get_endpoint_params(endpoint, patterns)

        # Generate sync method
        methods.append(generate_method_stub(
            method_name, params, description,
            is_async=False, accepts_kwargs=accepts_kwargs,
            include_is_classic=include_is_classic
        ))

        # Generate async method
        methods.append(generate_method_stub(
            method_name, params, description,
            is_async=True, accepts_kwargs=accepts_kwargs,
            include_is_classic=include_is_classic
        ))

    methods_str = "\n".join(methods)

    return f'''class {class_name}:
    """Auto-generated stub for IDE autocomplete."""

{methods_str}
'''


def generate_stubs_for_config(config_path: Path, include_is_classic: bool = True) -> tuple[str, list[dict], dict]:
    """Generate stubs for a single config file."""
    if not config_path.exists():
        return "", [], {}

    config = load_yaml_config(config_path)
    patterns = config.get("pattern_templates", {})
    endpoints = config.get("endpoints", [])

    return config.get("api_type", ""), endpoints, patterns


def has_kwargs_endpoints(endpoints: list[dict], patterns: dict) -> bool:
    """Check if any endpoint accepts **kwargs."""
    for endpoint in endpoints:
        if endpoint.get("accepts_kwargs"):
            return True
        if endpoint.get("pattern") and patterns:
            pattern = patterns.get(endpoint["pattern"], {})
            if pattern.get("accepts_kwargs"):
                return True
    return False


def generate_stub_header(docstring: str, needs_any: bool = False) -> str:
    """Generate properly formatted stub file header."""
    lines = [f'"""{docstring}"""', ""]
    if needs_any:
        lines.append("from typing import Any")
        lines.append("")
    lines.append("from ..core.executor import ApiResponse")
    lines.append("from ..types import Locale, Region")
    lines.append("")
    return "\n".join(lines)


def generate_wow_stubs(config_dir: Path) -> str:
    """Generate stubs for WoW APIs."""
    stubs = []

    # Check if we need Any import (for search methods with **kwargs)
    needs_any = False
    for config_file in ["wow_game_data.yaml", "wow_profile.yaml"]:
        config_path = config_dir / config_file
        if config_path.exists():
            config = load_yaml_config(config_path)
            patterns = config.get("pattern_templates", {})
            endpoints = config.get("endpoints", [])
            if has_kwargs_endpoints(endpoints, patterns):
                needs_any = True
                break

    # Header
    stubs.append(generate_stub_header("Type stubs for WoW API - auto-generated for IDE autocomplete.", needs_any))

    # Load WoW Game Data config
    game_data_path = config_dir / "wow_game_data.yaml"
    if game_data_path.exists():
        config = load_yaml_config(game_data_path)
        patterns = config.get("pattern_templates", {})
        endpoints = config.get("endpoints", [])
        stubs.append(generate_api_class_stub("WowGameDataAPI", endpoints, patterns, include_is_classic=True))

    # Load WoW Profile config
    profile_path = config_dir / "wow_profile.yaml"
    if profile_path.exists():
        config = load_yaml_config(profile_path)
        patterns = config.get("pattern_templates", {})
        endpoints = config.get("endpoints", [])
        stubs.append(generate_api_class_stub("WowProfileAPI", endpoints, patterns, include_is_classic=True))

    # Add WowAPI class
    stubs.append('''
class WowAPI:
    """World of Warcraft API facade."""

    game_data: WowGameDataAPI
    profile: WowProfileAPI
''')

    return "\n".join(stubs)


def generate_d3_stubs(config_dir: Path) -> str:
    """Generate stubs for Diablo 3 APIs."""
    stubs = []

    # Check if we need Any import
    needs_any = False
    for config_file in ["d3_game_data.yaml", "d3_community.yaml"]:
        config_path = config_dir / config_file
        if config_path.exists():
            config = load_yaml_config(config_path)
            patterns = config.get("pattern_templates", {})
            endpoints = config.get("endpoints", [])
            if has_kwargs_endpoints(endpoints, patterns):
                needs_any = True
                break

    # Header
    stubs.append(generate_stub_header("Type stubs for Diablo 3 API - auto-generated for IDE autocomplete.", needs_any))

    # Load D3 Game Data config
    game_data_path = config_dir / "d3_game_data.yaml"
    if game_data_path.exists():
        config = load_yaml_config(game_data_path)
        patterns = config.get("pattern_templates", {})
        endpoints = config.get("endpoints", [])
        stubs.append(generate_api_class_stub("D3GameDataAPI", endpoints, patterns, include_is_classic=False))

    # Load D3 Community config
    community_path = config_dir / "d3_community.yaml"
    if community_path.exists():
        config = load_yaml_config(community_path)
        patterns = config.get("pattern_templates", {})
        endpoints = config.get("endpoints", [])
        stubs.append(generate_api_class_stub("D3CommunityAPI", endpoints, patterns, include_is_classic=False))

    # Add D3API class
    stubs.append('''
class D3API:
    """Diablo 3 API facade."""

    game_data: D3GameDataAPI
    community: D3CommunityAPI
''')

    return "\n".join(stubs)


def generate_hs_stubs(config_dir: Path) -> str:
    """Generate stubs for Hearthstone APIs."""
    stubs = []

    # Check if we need Any import
    needs_any = False
    config_path = config_dir / "hs_game_data.yaml"
    if config_path.exists():
        config = load_yaml_config(config_path)
        patterns = config.get("pattern_templates", {})
        endpoints = config.get("endpoints", [])
        if has_kwargs_endpoints(endpoints, patterns):
            needs_any = True

    # Header
    stubs.append(generate_stub_header(
        "Type stubs for Hearthstone API - auto-generated for IDE autocomplete.", needs_any
    ))

    # Load HS Game Data config
    game_data_path = config_dir / "hs_game_data.yaml"
    if game_data_path.exists():
        config = load_yaml_config(game_data_path)
        patterns = config.get("pattern_templates", {})
        endpoints = config.get("endpoints", [])
        stubs.append(generate_api_class_stub("HSGameDataAPI", endpoints, patterns, include_is_classic=False))

    # Add HearthstoneAPI class
    stubs.append('''
class HearthstoneAPI:
    """Hearthstone API facade."""

    game_data: HSGameDataAPI
''')

    return "\n".join(stubs)


def generate_sc2_stubs(config_dir: Path) -> str:
    """Generate stubs for StarCraft 2 APIs."""
    stubs = []

    # Check if we need Any import
    needs_any = False
    for config_file in ["sc2_game_data.yaml", "sc2_community.yaml"]:
        config_path = config_dir / config_file
        if config_path.exists():
            config = load_yaml_config(config_path)
            patterns = config.get("pattern_templates", {})
            endpoints = config.get("endpoints", [])
            if has_kwargs_endpoints(endpoints, patterns):
                needs_any = True
                break

    # Header
    stubs.append(generate_stub_header(
        "Type stubs for StarCraft 2 API - auto-generated for IDE autocomplete.", needs_any
    ))

    # Load SC2 Game Data config
    game_data_path = config_dir / "sc2_game_data.yaml"
    if game_data_path.exists():
        config = load_yaml_config(game_data_path)
        patterns = config.get("pattern_templates", {})
        endpoints = config.get("endpoints", [])
        stubs.append(generate_api_class_stub("SC2GameDataAPI", endpoints, patterns, include_is_classic=False))

    # Load SC2 Community config
    community_path = config_dir / "sc2_community.yaml"
    if community_path.exists():
        config = load_yaml_config(community_path)
        patterns = config.get("pattern_templates", {})
        endpoints = config.get("endpoints", [])
        stubs.append(generate_api_class_stub("SC2CommunityAPI", endpoints, patterns, include_is_classic=False))

    # Add SC2API class
    stubs.append('''
class SC2API:
    """StarCraft 2 API facade."""

    game_data: SC2GameDataAPI
    community: SC2CommunityAPI
''')

    return "\n".join(stubs)


def generate_blizzard_api_stub(api_dir: Path) -> str:
    """Generate stub for main BlizzardAPI class."""
    return '''"""Type stubs for BlizzardAPI - auto-generated for IDE autocomplete."""

from .api.d3 import D3API
from .api.hs import HearthstoneAPI
from .api.sc2 import SC2API
from .api.wow import WowAPI
from .types import Locale, Region

class BlizzardAPI:
    """Main Blizzard API client with full type hints."""

    wow: WowAPI
    d3: D3API
    hearthstone: HearthstoneAPI
    sc2: SC2API

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        region: Region | str = ...,
        locale: Locale | str | None = ...,
    ) -> None: ...

    def close(self) -> None: ...
    async def aclose(self) -> None: ...

    def __enter__(self) -> BlizzardAPI: ...
    def __exit__(self, exc_type: type | None, exc_val: BaseException | None, exc_tb: object) -> None: ...

    async def __aenter__(self) -> BlizzardAPI: ...
    async def __aexit__(self, exc_type: type | None, exc_val: BaseException | None, exc_tb: object) -> None: ...
'''


def main():
    """Generate all stub files."""
    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    config_dir = project_root / "blizzardapi3" / "config" / "endpoints"
    api_dir = project_root / "blizzardapi3" / "api"
    pkg_dir = project_root / "blizzardapi3"

    print(f"Config directory: {config_dir}")
    print(f"API directory: {api_dir}")
    print()

    total_methods = 0

    # Generate WoW stubs
    wow_stubs = generate_wow_stubs(config_dir)
    stub_path = api_dir / "wow.pyi"
    with open(stub_path, "w", encoding="utf-8") as f:
        f.write(wow_stubs)
    method_count = wow_stubs.count("def ") + wow_stubs.count("async def ")
    print(f"Generated: {stub_path} ({method_count} methods)")
    total_methods += method_count

    # Generate D3 stubs
    d3_stubs = generate_d3_stubs(config_dir)
    stub_path = api_dir / "d3.pyi"
    with open(stub_path, "w", encoding="utf-8") as f:
        f.write(d3_stubs)
    method_count = d3_stubs.count("def ") + d3_stubs.count("async def ")
    print(f"Generated: {stub_path} ({method_count} methods)")
    total_methods += method_count

    # Generate Hearthstone stubs
    hs_stubs = generate_hs_stubs(config_dir)
    stub_path = api_dir / "hs.pyi"
    with open(stub_path, "w", encoding="utf-8") as f:
        f.write(hs_stubs)
    method_count = hs_stubs.count("def ") + hs_stubs.count("async def ")
    print(f"Generated: {stub_path} ({method_count} methods)")
    total_methods += method_count

    # Generate SC2 stubs
    sc2_stubs = generate_sc2_stubs(config_dir)
    stub_path = api_dir / "sc2.pyi"
    with open(stub_path, "w", encoding="utf-8") as f:
        f.write(sc2_stubs)
    method_count = sc2_stubs.count("def ") + sc2_stubs.count("async def ")
    print(f"Generated: {stub_path} ({method_count} methods)")
    total_methods += method_count

    # Generate BlizzardAPI stub
    blizzard_stubs = generate_blizzard_api_stub(api_dir)
    stub_path = pkg_dir / "blizzard_api.pyi"
    with open(stub_path, "w", encoding="utf-8") as f:
        f.write(blizzard_stubs)
    print(f"Generated: {stub_path}")

    print()
    print(f"Total method stubs: {total_methods}")


if __name__ == "__main__":
    main()
