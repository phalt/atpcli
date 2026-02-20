# Post Command

The `post` command allows you to create new posts on Bluesky directly from the command line.

## Basic Usage

```bash
atpcli bsky post --message "Your message here"
```

The command will post your message to Bluesky and return a link to the created post.

## Command Options

- `--message TEXT` - The text content of your post (required)

## Examples

### Simple Post

```bash
atpcli bsky post --message "Hello, Bluesky!"
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
atpcli bsky post --message 'My message with $pecial ch@racters!'
```

## Character Limits

Bluesky posts have a character limit of 300 characters (grapheme clusters). The command will fail if your message exceeds this limit.

## Authentication

You must be logged in to post. If you're not logged in, you'll see:

```
✗ Not logged in. Please run 'atpcli bsky login' first.
```

Run `atpcli bsky login` to authenticate before posting.

## Success Output

When a post is created successfully, you'll see:

```
Posting as your.handle...
✓ Post created successfully!
View your post at: https://bsky.app/profile/your.handle/post/abc123xyz
```

The link is clickable in most terminals and will open the post in your browser.

## Error Handling

If posting fails (e.g., network error, expired session), you'll see:

```
✗ Failed to post: [error message]
Your session may have expired. Try logging in again.
```

In this case, try logging in again with `atpcli bsky login`.
