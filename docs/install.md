# 🚀 Installation

## Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended)

## Installing uv

If you don't have uv installed, install it first:

### macOS and Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Using pip

```bash
pip install uv
```

### Windows

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Installing apcli

### From Source (Development)

Clone the repository and install:

```bash
git clone https://github.com/phalt/apcli.git
cd apcli
uv sync
```

This will create a virtual environment and install all dependencies.

### Using uv (when published to PyPI)

```bash
uv pip install apcli
```

### Using pip (when published to PyPI)

```bash
pip install apcli
```

## Verifying Installation

After installation, verify that apcli is working:

```bash
uv run apcli --help
```

You should see the help message with available commands:

```
Usage: apcli [OPTIONS] COMMAND [ARGS]...

  apcli - A Python CLI wrapper around the atproto package.

Options:
  --help  Show this message and exit.

Commands:
  login     Login to Bluesky and save session.
  timeline  View your timeline.
```

## Next Steps

Now that you have apcli installed, check out the [Quick Start Guide](getting-started.md) to learn how to:

1. Get an app password from Bluesky
2. Login to your account
3. View your timeline
