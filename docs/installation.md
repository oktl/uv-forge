# Installation

## Requirements

- **Python 3.12+**
- **UV** — [install uv](https://docs.astral.sh/uv/getting-started/installation/)
- **Git** (optional, for repository initialization)

## Install from PyPI

The simplest way to run UV Forge:

```bash
# Run directly without installing (recommended)
uvx uv-forge
```

Or install it as a persistent tool:

```bash
uv tool install uv-forge
uv-forge
```

## Run from source

```bash
git clone https://github.com/oktl/uv-forge.git
cd uv-forge
uv run uv-forge
```

!!! tip
    Running from source is useful if you want to contribute or customize templates. See [Contributing](contributing.md) for development setup details.
