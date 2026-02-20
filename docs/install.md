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

## Installing atpcli

### As a Global Tool (Recommended)

Install atpcli globally using uv's tool management:

```bash
uv tool install atpcli
```

This makes the `atpcli` command available system-wide, so you can run it from anywhere in your terminal without needing `uv run` or activating a virtual environment.

After installation, verify it works:

```bash
atpcli --help
```

### From Source (Development)

Clone the repository and install:

```bash
git clone https://github.com/phalt/atpcli.git
cd atpcli
uv sync
```

This will create a virtual environment and install all dependencies.

### Using uv pip (Alternative)

If you prefer to install in a specific virtual environment:

```bash
uv pip install atpcli
```

Note: With this method, you'll need to use `uv run atpcli` or activate the virtual environment first.

### Using pip (Alternative)

```bash
pip install atpcli
```

## Verifying Installation

After installation, verify that atpcli is working:

```bash
atpcli --help
```

You should see the help message with available commands:

```
Usage: atpcli [OPTIONS] COMMAND [ARGS]...

  atpcli - A Python CLI wrapper around the atproto package.

Options:
  --help  Show this message and exit.

Commands:
  login     Login to Bluesky and save session.
  timeline  View your timeline.
```

## Next Steps

Now that you have atpcli installed, check out the [Quick Start Guide](getting-started.md) to learn how to:

1. Get an app password from Bluesky
2. Login to your account
3. View your timeline
