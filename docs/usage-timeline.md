# 📱 Timeline Command

The `timeline` command displays posts from your Bluesky timeline in a beautifully formatted table.

## Basic Usage

```bash
atpcli bsky timeline
```

This will display your timeline with the default limit of 10 posts.

## Command Options

```bash
atpcli bsky timeline [OPTIONS]
```

### Options

- `--limit INTEGER`: Number of posts to show (default: 10)
- `--p INTEGER`: Page number to load (default: 1)
- `--help`: Show help message

## Examples

### View Default Timeline (10 posts)

```bash
atpcli bsky timeline
```

Output:

```
Loading timeline for alice.bsky.social...
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Author            ┃ Post                                ┃ Likes ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Alice             │ Just discovered this cool CLI tool!│    42 │
│ Bob               │ Beautiful day for coding 🌞         │    15 │
│ Charlie           │ Check out my new project...        │     8 │
└───────────────────┴─────────────────────────────────────┴───────┘

Showing 3 posts
```

### View More Posts

```bash
atpcli bsky timeline --limit 20
```

### View Fewer Posts

```bash
atpcli bsky timeline --limit 5
```

### View Maximum Posts

```bash
atpcli bsky timeline --limit 50
```

### Navigate Through Pages

```bash
# View page 2
atpcli bsky timeline --p 2

# View page 3
atpcli bsky timeline --p 3

# View page 2 with 20 posts per page
atpcli bsky timeline --limit 20 --p 2
```

## Output Format

The timeline is displayed as a table with three columns:

1. **Author**: Display name or handle of the post author
2. **Post**: The text content of the post (truncated if too long)
3. **Likes**: Number of likes the post has received

### Text Truncation

Long posts are automatically truncated to fit in the table:

- Posts longer than 80 characters are shortened
- Truncated posts end with `...`

Example:

```
Original: "This is a very long post about my experience with the new technology and how it has changed my workflow dramatically..."
Displayed: "This is a very long post about my experience with the new technology and h..."
```

## Requirements

Before using the timeline command, you must be logged in:

```bash
atpcli bsky login
```

## Authentication Errors

### Not Logged In

If you haven't logged in yet:

```bash
$ atpcli bsky timeline
✗ Not logged in. Please run 'atpcli bsky login' first.
```

**Solution**: Run `atpcli bsky login` first.

### Session Expired

If your session has expired:

```bash
$ atpcli bsky timeline
✗ Failed to load timeline: ...
Your session may have expired. Try logging in again.
```

**Solution**: Login again with `atpcli bsky login`.

## Performance

The timeline command fetches posts from the Bluesky API:

- **Response time**: Typically 1-3 seconds depending on network
- **Limit impact**: Higher limits may take slightly longer to fetch
- **Caching**: Currently no caching (each run fetches fresh data)

## Customization Tips

### Quick Aliases

Add these to your shell config (`.bashrc`, `.zshrc`, etc.):

```bash
# Quick timeline with different limits
alias tl='atpcli bsky timeline'
alias tl5='atpcli bsky timeline --limit 5'
alias tl20='atpcli bsky timeline --limit 20'
alias tl50='atpcli bsky timeline --limit 50'
```

### Script Integration

Use in shell scripts:

```bash
#!/bin/bash
# Check timeline and count posts

posts=$(atpcli bsky timeline --limit 50 2>/dev/null | grep "Showing" | awk '{print $2}')
echo "You have $posts posts in your timeline"
```

## Understanding the Timeline

The timeline shows:

- **Your following feed**: Posts from accounts you follow
- **Chronological order**: Most recent posts first
- **Like counts**: Snapshot at the time of fetching

!!! note "Real-time Updates"
    The timeline is a snapshot. Run the command again to see new posts.

## Limitations

Current limitations of the timeline command:

- **Text only**: Images, videos, and embeds are not displayed
- **No interactions**: Can't like, reply, or repost from the CLI (yet)
- **No filtering**: Shows all posts without filtering by type or author
- **No pagination**: Must specify limit upfront (no "load more")

## Troubleshooting

### Empty Timeline

If your timeline is empty:

1. **No follows**: Make sure you're following some accounts
2. **New account**: New accounts may have empty timelines initially
3. **Network issues**: Check your internet connection

### Encoding Issues

If you see strange characters:

1. Ensure your terminal supports UTF-8
2. Set the locale: `export LANG=en_US.UTF-8`

### Slow Performance

If the timeline loads slowly:

1. **Reduce limit**: Use `--limit 5` for faster response
2. **Check connection**: Test your network speed
3. **Bluesky status**: Check if Bluesky services are slow

## Future Enhancements

Potential future features:

- Media preview in terminal
- Interactive post selection
- Filtering by author or content
- Pagination support
- Like/reply/repost actions

## API Rate Limits

Be mindful of Bluesky's API rate limits:

- **Normal usage**: The timeline command is well within limits
- **Excessive use**: Running the command hundreds of times per minute may hit limits
- **Best practice**: Wait a few seconds between runs

## Privacy

The timeline command:

- ✅ Only reads your timeline (no write operations)
- ✅ Uses your authenticated session
- ✅ Doesn't store or transmit timeline data
- ✅ Respects your account's privacy settings
