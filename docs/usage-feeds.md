# 📡 Feeds Commands

The feeds commands allow you to list and view custom Bluesky feeds in beautifully formatted tables, reusing the same display infrastructure as the timeline command.

## Overview

Custom feeds are one of Bluesky's key differentiators, allowing users to curate algorithmic feeds based on specific topics, communities, or interests. The `feeds` command lists your saved feeds, while the `feed` command displays posts from a specific feed.

## Commands

### List Saved Feeds

List all feeds you've saved in Bluesky:

```bash
atpcli bsky feeds
```

This displays your saved feeds in a table format with feed names, URIs, and descriptions.

### View Feed Posts

View posts from a specific feed by URI:

```bash
atpcli bsky feed <feed-uri>
```

This displays posts from the specified feed in the same beautiful table format as the timeline command.

## List Saved Feeds Command

### Basic Usage

```bash
atpcli bsky feeds
```

Shows your saved feeds in a table format with:
- Feed display name
- Feed URI (for copy/paste)
- Feed description
- Count of saved feeds

### Output Formats

#### Table Format (Default)

```bash
atpcli bsky feeds
```

Example output:

```
Loading saved feeds for alice.bsky.social...
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Feed Name               ┃ URI                               ┃ Description                      ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Discover                │ at://did:plc:abc.../discover      │ Discover new content on Bluesky  │
│ Popular with Friends    │ at://did:plc:xyz.../popular       │ See what's trending with friends │
└─────────────────────────┴───────────────────────────────────┴──────────────────────────────────┘

Use 'atpcli bsky feed <uri>' to view posts from a specific feed.
```

#### URI-Only Format

For scripting or easy copy/paste:

```bash
atpcli bsky feeds --format uri
```

Example output:

```
at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.generator/discover
at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.generator/popular
```

This format is useful for piping to other commands or scripting:

```bash
# Get the first saved feed URI
FEED_URI=$(atpcli bsky feeds --format uri | head -n 1)

# View that feed
atpcli bsky feed "$FEED_URI"
```

### Empty Feeds List

If you haven't saved any feeds:

```
No saved feeds found.
Save feeds in the Bluesky app to see them here.
```

## View Feed Command

### Basic Usage

```bash
atpcli bsky feed <feed-uri>
```

Replace `<feed-uri>` with the full AT URI of the feed you want to view.

### Command Options

```bash
atpcli bsky feed <feed-uri> [OPTIONS]
```

#### Options

- `--limit INTEGER`: Number of posts to show (default: 10)
- `--p INTEGER`: Page number to load (default: 1)
- `--help`: Show help message

### Examples

#### View a Discover Feed

```bash
atpcli bsky feed at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.generator/discover
```

#### View with Custom Limit

```bash
atpcli bsky feed at://did:plc:abc123/app.bsky.feed.generator/science --limit 20
```

#### Paginate Through Feed

```bash
# View page 1
atpcli bsky feed at://did:plc:abc123/app.bsky.feed.generator/tech

# View page 2
atpcli bsky feed at://did:plc:abc123/app.bsky.feed.generator/tech --p 2

# View page 3 with 20 posts per page
atpcli bsky feed at://did:plc:abc123/app.bsky.feed.generator/tech --limit 20 --p 3
```

### Output Format

The feed command displays posts in exactly the same format as the `timeline` command:

1. **Author**: Display name and handle with emoji indicators:
   - ⤴️ Reply to another post
   - 🔁 Repost or quote post
   - 📷 Post with images
2. **Post**: The text content (wrapped to fit)
3. **Likes**: Number of likes the post received

Posts are displayed with the latest at the bottom, allowing you to scroll up to read.

### Empty Feed

If a feed has no posts:

```
This feed has no posts.
```

## Finding Feed URIs

### From the Feeds List

The easiest way to get feed URIs is from your saved feeds:

```bash
# List saved feeds
atpcli bsky feeds

# Copy a URI from the table and use it
atpcli bsky feed <copied-uri>
```

### From the Bluesky App

1. Open a feed in the Bluesky app
2. Look at the URL: `https://bsky.app/profile/did:plc:xxx/feed/feed-name`
3. Convert to AT URI format: `at://did:plc:xxx/app.bsky.feed.generator/feed-name`

### Feed URI Format

Feed URIs follow this format:
```
at://did:plc:<user-did>/app.bsky.feed.generator/<feed-name>
```

Example:
```
at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.generator/discover
```

## Requirements

Before using feed commands, you must be logged in:

```bash
atpcli login
```

## Authentication Errors

### Not Logged In

If you haven't logged in yet:

```bash
$ atpcli bsky feeds
✗ Not logged in. Please run 'atpcli login' first.
```

**Solution**: Run `atpcli login` first.

### Session Expired

Sessions are automatically refreshed when they expire. If your session cannot be refreshed:

```bash
$ atpcli bsky feeds
✗ Failed to load feeds: ...
```

**Solution**: Login again with `atpcli login`.

## Workflow Examples

### Discover and View New Feeds

```bash
# List your saved feeds
atpcli bsky feeds

# Pick a feed and view it
atpcli bsky feed at://did:plc:abc123/app.bsky.feed.generator/discover

# Like what you see? View more posts
atpcli bsky feed at://did:plc:abc123/app.bsky.feed.generator/discover --limit 30
```

### Script Integration

```bash
#!/bin/bash
# Check all saved feeds for new content

# Get all feed URIs
atpcli bsky feeds --format uri | while read -r feed_uri; do
    echo "Checking feed: $feed_uri"
    
    # Get first post from feed
    atpcli bsky feed "$feed_uri" --limit 1
    echo "---"
done
```

### Quick Aliases

Add these to your shell config (`.bashrc`, `.zshrc`, etc.):

```bash
# Quick feed commands
alias feeds='atpcli bsky feeds'
alias feed='atpcli bsky feed'

# Quick access to your favorite feeds
alias discover='atpcli bsky feed at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.generator/discover'
alias science='atpcli bsky feed at://did:plc:xyz123/app.bsky.feed.generator/science'
```

## Performance

Feed commands use the Bluesky API:

- **Response time**: Typically 1-3 seconds depending on network
- **Pagination**: Same as timeline - accessing high page numbers requires sequential API calls
- **Caching**: No caching (each run fetches fresh data)

## Comparison with Timeline

| Feature | Timeline | Feed |
|---------|----------|------|
| Content source | Following feed | Custom algorithmic feed |
| Display format | ✓ Same | ✓ Same |
| Pagination | ✓ Yes | ✓ Yes |
| --limit option | ✓ Yes | ✓ Yes |
| --p option | ✓ Yes | ✓ Yes |
| Post display | ✓ display_post() | ✓ display_post() |

The feed command reuses all display infrastructure from timeline, ensuring a consistent experience.

## Troubleshooting

### Invalid Feed URI

If you provide an invalid feed URI:

```
✗ Failed to load feed: ...
```

**Solution**: Check the URI format and ensure it's a valid feed URI from your saved feeds.

### Empty Feed List

If `atpcli bsky feeds` shows no feeds:

1. **No saved feeds**: Save feeds in the Bluesky app first
2. **Wrong account**: Make sure you're logged in with the correct account
3. **Sync issue**: Try logging out and back in

### Feed Not Loading

If a feed won't load:

1. **Check URI**: Ensure the URI is correct and complete
2. **Feed deleted**: The feed may have been deleted by its creator
3. **Network issues**: Check your internet connection
4. **Bluesky status**: Check if Bluesky services are operational

## Privacy

The feed commands:

- ✅ Only read your preferences and feed content (no write operations)
- ✅ Use your authenticated session
- ✅ Don't store or transmit feed data
- ✅ Respect your account's privacy settings

## API Rate Limits

Be mindful of Bluesky's API rate limits:

- **Normal usage**: Feed commands are well within limits
- **Excessive use**: Running commands hundreds of times per minute may hit limits
- **Best practice**: Wait a few seconds between runs

## Future Enhancements

Potential future features:

- Feed discovery/search
- Feed popularity metrics
- Save/unsave feeds from CLI
- Create custom feeds
- Feed composition/filtering

## Related Commands

- [`atpcli bsky timeline`](usage-timeline.md) - View your personal timeline
- [`atpcli bsky post`](usage-post.md) - Create posts
- [`atpcli login`](usage-login.md) - Authenticate with Bluesky
