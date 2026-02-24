# 🏠 atpcli

**A Python CLI wrapper around the atproto package for interacting with Bluesky**

## What is atpcli?

atpcli is a minimal command-line interface for interacting with [Bluesky](https://bsky.app), built on top of the [atproto](https://github.com/MarshalX/atproto) Python SDK. It provides simple commands for logging in, viewing your timeline, and posting messages.

## Features

- **🔐 Secure Login** - Uses Bluesky app passwords for safe authentication
- **📱 Timeline Viewing** - Browse your Bluesky timeline directly from the terminal
- **✍️ Post Messages** - Create posts on Bluesky from the command line
- **💾 Session Persistence** - Login once, stay authenticated across commands
- **🎨 Beautiful Output** - Rich terminal formatting with tables and colors
- **⚡️ Modern Tooling** - Built with uv, click, and rich

## Quick Example

```bash
# Login to Bluesky
atpcli login

# View your timeline
atpcli bsky timeline --limit 10

# Post a message
atpcli bsky post --message 'Hello, Bluesky!'
```

## Why use atpcli?

- **Simple**: Easy-to-use commands for common Bluesky operations
- **Secure**: Uses app passwords instead of your main password
- **Fast**: Built with modern Python tooling (uv)
- **Beautiful**: Rich terminal output with colors and tables

## Getting Started

Ready to get started? Check out the [Installation](install.md) guide and then the [Quick Start](getting-started.md) guide.

## Project Information

- **GitHub**: [phalt/atpcli](https://github.com/phalt/atpcli)
- **License**: MIT
- **Python Version**: 3.10+
