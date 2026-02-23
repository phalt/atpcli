from rich.table import Table
from rich.text import Text


def get_profile_display(client, did: str, profile_cache: dict) -> str:
    """Get a formatted display string for a user profile.

    Args:
        client: Authenticated atproto client
        did: The DID of the user
        profile_cache: Dictionary to cache profile lookups

    Returns:
        Formatted string with display name and handle, or DID if profile fetch fails
    """
    if did not in profile_cache:
        try:
            profile = client.get_profile(did)
            profile_cache[did] = profile
        except Exception:
            # If profile fetch fails, use DID as fallback
            profile_cache[did] = None

    profile = profile_cache[did]

    if profile:
        return f"{profile.display_name or profile.handle} (@{profile.handle})"
    else:
        return did


def display_spice_note(note, at_uri: str, client, profile_cache: dict) -> Table:
    """Display a Spice note in the terminal as a table.

    Args:
        note: SpiceNote instance
        at_uri: The AT URI of the note
        client: Authenticated atproto client
        profile_cache: Dictionary to cache profile lookups

    Returns:
        Rich Table with the formatted note
    """
    # Extract DID from AT URI (format: at://did:plc:xxx/collection/rkey)
    did = at_uri.split("/")[2]

    # Get formatted author display
    author_display = get_profile_display(client, did, profile_cache)

    # Get profile from cache to build Bluesky URL
    profile = profile_cache.get(did)
    if profile and hasattr(profile, "handle"):
        # Create clickable author link
        profile_url = f"https://bsky.app/profile/{profile.handle}"
        author_link = f"[link={profile_url}]{author_display}[/link]"
    else:
        # Fallback to non-clickable display
        author_link = author_display

    # Create clickable title with author and URL
    clickable_title = f"{author_link} • [link={note.url}]{note.url}[/link]"

    table = Table(title=clickable_title, show_header=True, expand=True)
    # Use overflow="fold" to wrap text instead of truncating with ellipsis
    table.add_column("Note", style="white", overflow="fold")
    table.add_column("Created", justify="right", style="dim", overflow="fold")

    # Render the note text
    rendered_text = Text(note.text)

    table.add_row(rendered_text, note.createdAt)
    return table
