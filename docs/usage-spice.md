# Spice Commands

Spice is a web annotation layer built on the AT Protocol. You can add short public notes ("spices") to any URL on the web.

## Overview

Spice notes are:

- **Public annotations** attached to any URL
- **Stored in your personal data repository** (PDS) on the AT Protocol
- **Plain text only** (no markdown or special formatting)
- **Limited to 256 characters** per note
- **Discoverable** by anyone through your atproto repository

The name "Spice" reflects the idea of adding flavor to any corner of the web — a pinch of commentary, a dash of graffiti, a sprinkle of "I was here."

## Prerequisites

You must be logged in before using Spice commands. If you haven't logged in yet, run:

```bash
atpcli bsky login
```

This will save your session, which the Spice commands will use.

## Commands

### Add a Note

Create a new note for a URL:

```bash
atpcli spice add <url> <text>
```

**Example:**

```bash
atpcli spice add https://example.com "Great article about web standards!"
```

**Output:**

```
Created: at://did:plc:abc123/tools.spice.note/3jt7xyz
```

**Requirements:**

- URL must be fully-qualified with scheme and host (e.g., `https://example.com`)
- Text must be 1-256 characters
- Text is plain text only (raw URLs within the text are acceptable)

**Validation:**

The command validates your input before making any network calls:

- URL format is checked (must include `https://` or similar scheme)
- Text length is validated (max 256 characters)
- Empty text is rejected

### List Your Notes

View all notes you've created for a specific URL:

```bash
atpcli spice list <url>
```

**Example:**

```bash
atpcli spice list https://example.com
```

**Output:**

```
Found 2 note(s):

at://did:plc:abc123/tools.spice.note/3jt7xyz  2026-02-21T10:00:00Z
Great article about web standards!

at://did:plc:abc123/tools.spice.note/3kt9abc  2026-02-21T12:30:00Z
Updated with even more examples now!
```

**Options:**

- `--limit INTEGER`: Number of records to fetch per page (default: 50)
- `--all`: Fetch all records across all pages (by default, only fetches the first page)

**Pagination Examples:**

```bash
# Fetch all notes (across all pages)
atpcli spice list https://example.com --all

# Fetch with custom page size
atpcli spice list https://example.com --limit 100
```

**Notes:**

- Only shows **your own notes** (notes created by your logged-in account)
- URL must match exactly (no normalization is applied)
- If no notes are found, you'll see: "No notes found for \<url\>"
- By default, fetches up to 50 records from the first page. Use `--all` to fetch all pages.

### Delete a Note

Remove a note using its AT URI:

```bash
atpcli spice delete <at-uri>
```

**Example:**

```bash
atpcli spice delete at://did:plc:abc123/tools.spice.note/3jt7xyz
```

**Output:**

```
Deleted: at://did:plc:abc123/tools.spice.note/3jt7xyz
```

**Notes:**

- You can get the AT URI from the output of `spice add` or `spice list`
- Only `tools.spice.note` records can be deleted with this command
- Attempting to delete other record types will result in an error

## Error Handling

Common errors you might encounter:

### Not Logged In

```
✗ Not logged in. Please run 'atpcli bsky login' first.
```

**Solution:** Run `atpcli bsky login` to authenticate.

### Invalid URL

```
✗ Invalid URL: example.com
URL must include scheme and host (e.g., https://example.com)
```

**Solution:** Include the full URL with scheme: `https://example.com`

### Text Too Long

```
✗ Text is too long: 300 characters (max 256)
```

**Solution:** Shorten your text to 256 characters or less.

### Session Expired

```
✗ Failed to create note: [error details]
Your session may have expired. Try logging in again.
```

**Solution:** Run `atpcli bsky login` to refresh your session.

## Technical Details

### Record Schema

Spice notes use the `tools.spice.note` Lexicon (schema) with the following fields:

- `url` (string): The fully-qualified URL being annotated
- `text` (string): The annotation text (max 256 characters)
- `createdAt` (datetime): ISO 8601 / RFC 3339 datetime of record creation

### AT URIs

Each note gets a unique identifier in the form:

```
at://<did>/tools.spice.note/<tid>
```

Where:

- `<did>` is your decentralized identifier (e.g., `did:plc:abc123`)
- `tools.spice.note` is the collection name
- `<tid>` is an auto-generated timestamp-based ID

This URI is permanent and can be used to reference or delete the note.

## Future Possibilities

The Spice implementation is designed to support future features without breaking changes:

- **AppView indexing service**: Query notes from all users for any URL
- **Threading**: Reply to other notes with a `replyTo` field
- **Reactions**: React to notes with emoji or other indicators
- **Browser extension**: See Spice notes inline on any webpage

These features are not yet implemented but are accounted for in the schema design.
