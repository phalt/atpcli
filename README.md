# apcli

A Python CLI wrapper around the [atproto](https://github.com/MarshalX/atproto) package for interacting with Bluesky.

## Documentation

Full documentation is available at [docs/](docs/):

- [Installation Guide](docs/install.md)
- [Quick Start Guide](docs/getting-started.md) - Learn how to get app passwords and use apcli
- [Login Command](docs/usage-login.md)
- [Timeline Command](docs/usage-timeline.md)

Or serve the docs locally:

```bash
make docs-serve
```

## Quick Start

### Installation

Install using [uv](https://docs.astral.sh/uv/):

```bash
uv pip install apcli
```

Or for development:

```bash
git clone https://github.com/phalt/apcli.git
cd apcli
make install
```

## Usage

### Login

⚠️ **Security Note**: Use Bluesky app passwords, not your main password! See the [Quick Start Guide](docs/getting-started.md) for instructions on creating an app password.

Login to your Bluesky account and save the session:

```bash
uv run apcli login
```

You'll be prompted for your handle and password. The session will be saved to `~/.config/apcli/config.json`.

### View Timeline

View your timeline:

```bash
uv run apcli timeline
```

Options:
- `--limit N` - Show N posts (default: 10)

Example:
```bash
uv run apcli timeline --limit 20
```

## Development

### Setup

```bash
make install
```

### Run tests

```bash
make test
```

### Build documentation

```bash
make docs-build
```

### Serve documentation locally

```bash
make docs-serve
```

### Format code

```bash
make format
```

### Clean build artifacts

```bash
make clean
```

## Requirements

- Python 3.10+
- uv package manager

## License

MIT
