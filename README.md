# apcli

A Python CLI wrapper around the [atproto](https://github.com/MarshalX/atproto) package for interacting with Bluesky.

## Installation

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
