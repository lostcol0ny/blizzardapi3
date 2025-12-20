# Using uv with BlizzardAPI v3

[uv](https://github.com/astral-sh/uv) is an extremely fast Python package installer and resolver, written in Rust. It's 10-100x faster than pip and is the recommended way to manage dependencies for BlizzardAPI v3.

## Why uv?

- ⚡ **10-100x faster** than pip
- 🔒 **Reliable** - Consistent dependency resolution
- 🎯 **Drop-in replacement** - Works with existing pyproject.toml
- 📦 **Modern** - Built for Python's future

## Installation

### Install uv

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Using pip (if you already have Python)
pip install uv
```

## Basic Usage

### Install BlizzardAPI v3

```bash
# Install from PyPI
uv pip install blizzardapi3

# Install from source
git clone https://github.com/lostcol0ny/blizzardapi3.git
cd blizzardapi3
uv pip install -e .
```

### Development Setup

```bash
# Clone repository
git clone https://github.com/lostcol0ny/blizzardapi3.git
cd blizzardapi3

# Install with dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
ruff check .
```

### Running Examples

```bash
# Install with examples dependencies (includes python-dotenv)
uv pip install -e ".[examples]"

# Run an example
python examples/character_profile_example.py
```

## Virtual Environments

uv can create and manage virtual environments:

```bash
# Create a virtual environment
uv venv

# Activate it
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate

# Install dependencies
uv pip install -e ".[dev]"
```

## Complete Workflow Example

```bash
# 1. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone project
git clone https://github.com/lostcol0ny/blizzardapi3.git
cd blizzardapi3

# 3. Create virtual environment
uv venv

# 4. Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows

# 5. Install project with all dependencies
uv pip install -e ".[dev,examples]"

# 6. Set up credentials
cat > .env << EOF
BLIZZARD_CLIENT_ID=your_client_id
BLIZZARD_CLIENT_SECRET=your_client_secret
EOF

# 7. Run tests
pytest

# 8. Try an example
python examples/character_profile_example.py
```

## Dependency Groups

BlizzardAPI v3 has organized dependencies into groups:

### Core Dependencies (always installed)
- `requests` - HTTP library
- `aiohttp` - Async HTTP library
- `pydantic` - Data validation
- `pyyaml` - YAML parsing

### Development Dependencies (`[dev]`)
- `pytest` - Testing framework
- `pytest-mock` - Test mocking
- `pytest-asyncio` - Async testing
- `black` - Code formatter
- `ruff` - Linter

### Examples Dependencies (`[examples]`)
- `python-dotenv` - Environment variable management

## Install Multiple Groups

```bash
# Install library + dev tools
uv pip install -e ".[dev]"

# Install library + examples tools
uv pip install -e ".[examples]"

# Install everything
uv pip install -e ".[dev,examples]"
```

## Performance Comparison

Real-world comparison installing BlizzardAPI v3 with all dependencies:

| Tool | Time | Speed |
|------|------|-------|
| pip | ~15s | 1x |
| uv | ~0.5s | **30x faster** |

## Common Commands

```bash
# Install package
uv pip install blizzardapi3

# Install from source (editable)
uv pip install -e .

# Install with extras
uv pip install -e ".[dev]"

# Upgrade package
uv pip install --upgrade blizzardapi3

# Uninstall package
uv pip uninstall blizzardapi3

# List installed packages
uv pip list

# Show package info
uv pip show blizzardapi3

# Freeze dependencies
uv pip freeze > requirements.txt
```

## Troubleshooting

### uv command not found

Make sure uv is in your PATH:

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.cargo/bin:$PATH"
```

### Virtual environment issues

If you have issues with virtual environments:

```bash
# Remove existing venv
rm -rf .venv

# Create fresh venv with uv
uv venv

# Activate and reinstall
source .venv/bin/activate  # macOS/Linux
uv pip install -e ".[dev,examples]"
```

### Compatibility with pip

uv is a drop-in replacement for pip. If you encounter issues:

```bash
# Fall back to pip
pip install -e ".[dev]"
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Install dependencies
        run: |
          uv pip install -e ".[dev]"

      - name: Run tests
        run: pytest
```

## Additional Resources

- [uv Documentation](https://github.com/astral-sh/uv)
- [uv Performance Benchmarks](https://github.com/astral-sh/uv#benchmarks)
- [BlizzardAPI v3 GitHub](https://github.com/lostcol0ny/blizzardapi3)

## Summary

Using uv with BlizzardAPI v3:
1. ✅ Faster installation (10-100x)
2. ✅ Reliable dependency resolution
3. ✅ Drop-in replacement for pip
4. ✅ Modern Python tooling
5. ✅ Same commands as pip

Simply replace `pip` with `uv pip` in any command!
