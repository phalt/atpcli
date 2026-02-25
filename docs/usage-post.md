# Post Command

The `post` command allows you to create new posts on Bluesky directly from the command line.

## Basic Usage

### Using the Editor (Interactive Mode)

Simply run the post command without any arguments to open your editor:

```bash
atpcli bsky post
```

This will open your default editor (from the `EDITOR` environment variable, or `vim`/`vi` if available) where you can compose your message. Lines starting with `#` are treated as comments and will be ignored. Save and exit to post, or save an empty file to cancel.

### Using the -m Flag (Direct Mode)

```bash
atpcli bsky post --message "Your message here"
```

Or use the shorter `-m` option:

```bash
atpcli bsky post -m "Your message here"
```

The command will post your message to Bluesky and return a link to the created post.

## Command Options

- `--message TEXT` / `-m TEXT` - The text content of your post (optional - if not provided, opens editor)

## Examples

### Interactive Editor Mode

For composing longer messages or messages with special formatting, use the interactive editor:

```bash
atpcli bsky post
```

This opens your editor with helpful comments:
- Write your message at the top
- Lines starting with `#` are ignored (comments)
- Save and exit to post
- Save an empty file (or only comments) to cancel

### Simple Post

```bash
atpcli bsky post --message "Hello, Bluesky!"
# Or use the shorter -m option:
atpcli bsky post -m "Hello, Bluesky!"
```

### Post with Links

```bash
atpcli bsky post --message "Check out this article: https://example.com/article"
```

The atproto library automatically detects and creates proper link facets for URLs in your posts.

### Multi-line Posts

```bash
atpcli bsky post --message "Line 1
Line 2
Line 3"
```

## Special Characters and Shell Escaping

When posting messages that contain special characters, you need to be aware of shell escaping rules.

### The Exclamation Mark (!) Issue

The exclamation mark (`!`) is a special character in bash and zsh shells that triggers history expansion. This can cause issues when posting messages with exclamation marks.

**Problem:**
```bash
atpcli bsky post --message "Hello world!"
# Error: bash tries to expand "world!" as a history reference
```

**Solutions:**

1. **Use single quotes (recommended):**
   ```bash
   atpcli bsky post --message 'Hello world!'
   ```

2. **Escape the exclamation mark:**
   ```bash
   atpcli bsky post --message "Hello world\!"
   ```

3. **Disable history expansion temporarily:**
   ```bash
   set +H
   atpcli bsky post --message "Hello world!"
   set -H
   ```

### Other Special Characters

Other characters that may need escaping in double quotes:
- `$` (dollar sign) - variable expansion
- `` ` `` (backtick) - command substitution
- `\` (backslash) - escape character
- `"` (double quote) - string delimiter

**Best Practice:** Use single quotes for messages unless you need variable expansion:
```bash
# Single quotes prevent shell interpretation of special characters
atpcli bsky post --message 'My message with special characters: $ ! @ #'
```

**Alternative:** Use the interactive editor mode to avoid shell escaping issues entirely:
```bash
atpcli bsky post
# Your editor opens - type your message freely without worrying about shell escaping
```

## Configuring Your Editor

By default, the command will use your editor in this order of preference:

1. The `EDITOR` environment variable
2. `vim` (if available)
3. `vi` (if available)

To set your preferred editor permanently, add this to your shell configuration file (`.bashrc`, `.zshrc`, etc.):

```bash
export EDITOR=nano      # Use nano
export EDITOR=emacs     # Use emacs
export EDITOR=code -w   # Use VS Code (wait for window to close)
export EDITOR=vim       # Use vim (default if available)
```

## Character Limits

Bluesky posts have a character limit of 300 characters (grapheme clusters). The command will fail if your message exceeds this limit.

## Authentication

You must be logged in to post. If you're not logged in, you'll see:

```
✗ Not logged in. Please run 'atpcli login' first.
```

Run `atpcli login` to authenticate before posting.

## Success Output

When a post is created successfully, you'll see:

```
Posting as your.handle...
✓ Post created successfully!
View your post at: https://bsky.app/profile/your.handle/post/abc123xyz
```

The link is clickable in most terminals and will open the post in your browser.

## Error Handling

If posting fails (e.g., network error), you'll see:

```
✗ Failed to post: [error message]
```

## Session Management

The CLI automatically refreshes expired sessions, so you won't need to re-login manually. Sessions are automatically saved when they are refreshed, ensuring a seamless experience.
