# atpcli

A Python CLI wrapper around the [atproto](https://github.com/MarshalX/atproto) package for interacting with Bluesky.

## Documentation

Full documentation is available at [docs/](docs/):

- [Installation Guide](docs/install.md)
- [Quick Start Guide](docs/getting-started.md) - Learn how to get app passwords and use atpcli
- [Login Command](docs/usage-login.md)
- [Timeline Command](docs/usage-timeline.md)
- [Feeds Commands](docs/usage-feeds.md) - List and view custom Bluesky feeds
- [Post Command](docs/usage-post.md)

Or serve the docs locally:

```bash
make docs-serve
```

## Quick Start

### Installation

Install globally using [uv](https://docs.astral.sh/uv/):

```bash
uv tool install atpcli
```

This installs `atpcli` as a global tool, making it available from anywhere in your terminal.

Or for development:

```bash
git clone https://github.com/phalt/atpcli.git
cd atpcli
make install
```

## Usage

### Login

⚠️ **Security Note**: Use app passwords, not your main password! See the [Quick Start Guide](docs/getting-started.md) for instructions on creating an app password.

Login to an AT Protocol PDS (defaults to Bluesky):

```bash
atpcli login
```

Or login to a custom PDS:

```bash
atpcli login https://my-pds.com
```

You'll be prompted for your handle and password. The session will be saved to `~/.config/atpcli/config.json`.

### View Timeline

View your timeline:

```bash
atpcli bsky timeline
```

Options:
- `--limit N` - Show N posts (default: 10)
- `--p N` - Show page N (default: 1)

Example:
```bash
atpcli bsky timeline --limit 20
atpcli bsky timeline --p 2
```

### Post Messages

Create a post on Bluesky:

```bash
atpcli bsky post --message 'Hello, Bluesky!'
```

**Note:** When using special characters like `!`, use single quotes to avoid shell expansion issues. See the [Post Command documentation](docs/usage-post.md) for more details.

### Custom Feeds

List your saved Bluesky feeds:

```bash
atpcli bsky feeds
```

View posts from a specific feed:

```bash
atpcli bsky feed at://did:plc:xxx/app.bsky.feed.generator/discover
```

Options:
- `--limit N` - Show N posts (default: 10)
- `--p N` - Show page N (default: 1)
- `--format uri` - Output only URIs (for `feeds` command)

Example:
```bash
# List feeds in URI format for scripting
atpcli bsky feeds --format uri

# View a feed with more posts
atpcli bsky feed at://did:plc:xxx/app.bsky.feed.generator/tech --limit 20

# Navigate to page 2
atpcli bsky feed at://did:plc:xxx/app.bsky.feed.generator/tech --p 2
```

See the [Feeds Commands documentation](docs/usage-feeds.md) for more details.

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
