# 🏠 apcli

**A Python CLI wrapper around the atproto package for interacting with Bluesky**

## What is apcli?

apcli is a minimal command-line interface for interacting with [Bluesky](https://bsky.app), built on top of the [atproto](https://github.com/MarshalX/atproto) Python SDK. It provides simple commands for logging in and viewing your timeline.

## Features

- **🔐 Secure Login** - Uses Bluesky app passwords for safe authentication
- **📱 Timeline Viewing** - Browse your Bluesky timeline directly from the terminal
- **💾 Session Persistence** - Login once, stay authenticated across commands
- **🎨 Beautiful Output** - Rich terminal formatting with tables and colors
- **⚡️ Modern Tooling** - Built with uv, click, and rich

## Quick Example

```bash
# Login to Bluesky
uv run apcli login

# View your timeline
uv run apcli timeline --limit 10
```

## Why use apcli?

- **Simple**: Just two commands - login and timeline
- **Secure**: Uses app passwords instead of your main password
- **Fast**: Built with modern Python tooling (uv)
- **Beautiful**: Rich terminal output with colors and tables

## Getting Started

Ready to get started? Check out the [Installation](install.md) guide and then the [Quick Start](getting-started.md) guide.

## Project Information

- **GitHub**: [phalt/apcli](https://github.com/phalt/apcli)
- **License**: MIT
- **Python Version**: 3.10+
