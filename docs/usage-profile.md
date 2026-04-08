# 👤 Profile Commands

The profile commands allow you to view user profiles and browse posts from specific users on Bluesky.

## Profile Command

View any user's profile information including bio, stats, and links.

### Basic Usage

```bash
atpcli bsky profile @alice.bsky.social
```

### Command Options

```bash
atpcli bsky profile [HANDLE] [OPTIONS]
```

#### Arguments

- `HANDLE`: The user's handle (e.g., `@alice.bsky.social` or `alice.bsky.social`)

#### Options

- `--me`: View your own profile
- `--help`: Show help message

### Examples

#### View Another User's Profile

```bash
atpcli bsky profile @alice.bsky.social
```

Output:

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Alice (@alice.bsky.social)                           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  DID: did:plc:abc123xyz789...
  
  Bio: Python developer and open source enthusiast 🐍
       Building cool things with AT Protocol!
  
  📊 Stats
    • 1,234 followers
    • 567 following  
    • 890 posts
  
  🔗 Links
    Profile: https://bsky.app/profile/alice.bsky.social
    Avatar:  https://cdn.bsky.app/avatar/...
```

#### View Your Own Profile

```bash
atpcli bsky profile --me
```

This will display your profile using your logged-in handle.

### Profile Information

The profile command displays:

- **Display Name** - The user's chosen display name
- **Handle** - The user's AT Protocol handle
- **DID** - The user's decentralized identifier (for copy/paste)
- **Bio** - The user's profile description
- **Stats** - Follower count, following count, and post count
- **Profile Link** - Clickable link to the web profile
- **Avatar URL** - URL to the user's avatar image

---

## Posts Command

View posts from a specific user (author feed).

### Basic Usage

```bash
atpcli bsky posts @alice.bsky.social
```

### Command Options

```bash
atpcli bsky posts [HANDLE] [OPTIONS]
```

#### Arguments

- `HANDLE`: The user's handle (e.g., `@alice.bsky.social` or `alice.bsky.social`)

#### Options

- `--limit INTEGER`: Number of posts to show (default: 10)
- `--p INTEGER`: Page number to load (default: 1)
- `--me`: View your own posts
- `--help`: Show help message

### Examples

#### View Default Posts (10 posts)

```bash
atpcli bsky posts @alice.bsky.social
```

Output:

```
Loading posts from @alice.bsky.social...
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Alice (@alice.bsky.social)                           ┃
┃ did:plc:abc123xyz789...                              ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Post     │ Great day coding! Check out...       │ 42│
└──────────┴──────────────────────────────────────┴───┘

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Alice (@alice.bsky.social)                           ┃
┃ did:plc:abc123xyz789...                              ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Post     │ Working on atpcli features...        │ 15│
└──────────┴──────────────────────────────────────┴───┘

Showing 2 posts (page 1)
```

#### View More Posts

```bash
atpcli bsky posts @alice.bsky.social --limit 20
```

This will display 20 posts from the user.

#### View Your Own Posts

```bash
atpcli bsky posts --me
```

This will display your posts using your logged-in handle.

#### Pagination

```bash
atpcli bsky posts @alice.bsky.social --p 2
```

Navigate through posts using the `--p` option. The command will show pagination info:

```
Showing 10 posts (page 2) - Use --p 3 for next page
```

### Post Display Features

All posts displayed include:

- **Author Name and Handle** - Clickable link to the post on Bluesky
- **DID** - User's decentralized identifier (always shown, styled subtly)
- **Post Content** - The text of the post with clickable links
- **Like Count** - Number of likes on the post
- **Indicators** - Emojis showing post type:
  - ⤴️ - Reply to another post
  - 🔁 - Repost or quote post
  - 📷 - Post with image

### DID Display

**New in this version:** All posts now display the user's DID (decentralized identifier) below the author name. This is styled with dim text for subtlety but remains easily selectable for copy/paste operations.

The DID is NOT part of the clickable link, so you can:
- Shift+Click on the author name to open the post in your browser
- Select and copy the DID without opening the link

### Performance Note

Like the timeline command, accessing higher page numbers requires multiple API calls. For example, accessing page 10 requires 10 sequential API calls. For pages beyond 5, you'll see a warning message with an estimate of the time required.

---

## Use Cases

### Discovering Users

Use the profile command to:
- Check out someone's bio and interests
- See their follower/following counts
- Get their DID for other tools or automation

### Browsing User Content

Use the posts command to:
- Read through a user's post history
- Find specific posts you remember
- Explore content from interesting accounts
- Archive or reference user posts

### Working with DIDs

The DID display feature makes it easy to:
- Copy DIDs for use in other AT Protocol tools
- Reference users in scripts or automation
- Work with AT Protocol identifiers directly
- Share user identifiers precisely

---

## Tips

- **Handle Format**: You can use handles with or without the `@` prefix
- **Pagination**: Start with small page numbers for faster response times
- **DIDs**: The displayed DIDs are easily selectable for copy/paste
- **Session**: Make sure you're logged in with `atpcli login` before using these commands

---

## Related Commands

- [Timeline Command](usage-timeline.md) - View your personal timeline
- [Feeds Commands](usage-feeds.md) - View custom feeds
- [Login Command](usage-login.md) - Authenticate with Bluesky
