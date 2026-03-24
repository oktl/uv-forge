# Installation

## Requirements

- **Python 3.12+**
- **UV** — [install uv](https://docs.astral.sh/uv/getting-started/installation/)
- **Git** (optional, for repository initialization)

## Install from PyPI

The simplest way to run UV Forger:

```bash
# Run directly without installing (recommended)
uvx uv-forger
```

Or install it as a persistent tool:

```bash
uv tool install uv-forger
uv-forger
```

## Run from source

```bash
git clone https://github.com/oktl/uv-forger.git
cd uv-forger
uv run uv-forger
```

!!! tip
    Running from source is useful if you want to contribute or customize templates. See [Contributing](contributing.md) for development setup details.
