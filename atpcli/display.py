import re
from typing import List, Optional

from atproto_client.models.app.bsky.embed.images import View as ImagesView
from atproto_client.models.app.bsky.embed.record import View as RecordView
from atproto_client.models.app.bsky.embed.record_with_media import View as RecordWithMediaView
from atproto_client.models.app.bsky.feed.defs import PostView
from atproto_client.models.app.bsky.richtext.facet import Link as LinkFacet
from atproto_client.models.app.bsky.richtext.facet import Main as FacetMain
from rich.table import Table
from rich.text import Text


def _at_uri_to_web_url(uri: str, handle: str) -> str:
    """Convert AT protocol URI to Bluesky web URL.

    Args:
        uri: AT protocol URI (e.g., at://did:plc:xxx/app.bsky.feed.post/yyy)
        handle: User handle

    Returns:
        Bluesky web URL (e.g., https://bsky.app/profile/{handle}/post/{post_id})
    """
    # Extract post ID from AT URI
    # Format: at://did:plc:xxx/app.bsky.feed.post/yyy
    parts = uri.split("/")
    if len(parts) >= 5 and parts[3] == "app.bsky.feed.post":
        post_id = parts[4]
        return f"https://bsky.app/profile/{handle}/post/{post_id}"
    return uri


def _render_text_with_links(text: str, facets: Optional[List[FacetMain]] = None) -> Text:
    """Render text with clickable links.

    Args:
        text: The text to render
        facets: Optional list of facets from the post record (for proper link detection)

    Returns:
        Rich Text object with clickable links
    """
    rich_text = Text()

    # If we have facets, use them for accurate link detection
    # Facets use byte indices, so we need to encode/decode properly
    if facets:
        # Extract link facets and sort by byte position
        link_facets = []
        for facet in facets:
            for feature in facet.features:
                if isinstance(feature, LinkFacet):
                    # ByteSlice uses byte offsets, not character offsets
                    link_facets.append(
                        {"byte_start": facet.index.byte_start, "byte_end": facet.index.byte_end, "uri": feature.uri}
                    )

        # Sort by byte position
        link_facets.sort(key=lambda x: x["byte_start"])

        # Convert text to bytes for proper indexing
        text_bytes = text.encode("utf-8")
        last_byte_end = 0

        for link_facet in link_facets:
            byte_start = link_facet["byte_start"]
            byte_end = link_facet["byte_end"]
            uri = link_facet["uri"]

            # Add text before the link
            if byte_start > last_byte_end:
                before_text = text_bytes[last_byte_end:byte_start].decode("utf-8")
                rich_text.append(before_text)

            # Add the link
            link_text = text_bytes[byte_start:byte_end].decode("utf-8")
            rich_text.append(link_text, style=f"link {uri}")
            last_byte_end = byte_end

        # Add any remaining text
        if last_byte_end < len(text_bytes):
            remaining_text = text_bytes[last_byte_end:].decode("utf-8")
            rich_text.append(remaining_text)

        return rich_text

    # Fallback: use regex pattern matching if no facets available
    # Pattern to match URLs with or without protocol.
    # Matches:
    # 1. URLs starting with http:// or https://
    # 2. Domain-like patterns (e.g., github.com/user/repo, example.com, x.com)
    # The pattern looks for:
    # - Optional protocol (https?://)
    # - Domain name: alphanumeric segments with hyphens (but not at start/end) separated by dots
    # - TLD with at least 2 letters
    # - Optional path, query, and fragment
    url_pattern = (
        r'(?:https?://)?(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}(?:[^\s<>"{}|\\^`\[\]]*)?'
    )

    last_end = 0

    for match in re.finditer(url_pattern, text):
        matched_text = match.group()

        # Add text before the URL
        if match.start() > last_end:
            rich_text.append(text[last_end : match.start()])

        # Add the URL as a clickable link
        # If the URL doesn't have a protocol, add https://
        display_url = matched_text
        link_url = matched_text if matched_text.startswith(("http://", "https://")) else f"https://{matched_text}"

        rich_text.append(display_url, style=f"link {link_url}")
        last_end = match.end()

    # Add any remaining text
    if last_end < len(text):
        rich_text.append(text[last_end:])

    return rich_text


def _has_image(post: PostView) -> bool:
    """Check if a post has an image embed.

    Args:
        post: The post to check

    Returns:
        True if the post has an image embed, False otherwise
    """
    if not hasattr(post, "embed") or post.embed is None:
        return False

    # Check if it's an images embed directly
    if isinstance(post.embed, ImagesView):
        return True

    # Check if it's a record with media (quote post with images)
    if isinstance(post.embed, RecordWithMediaView):
        if hasattr(post.embed, "media") and isinstance(post.embed.media, ImagesView):
            return True

    return False


def _is_repost_or_quote(post: PostView) -> bool:
    """Check if a post is a repost or quote post.

    Args:
        post: The post to check

    Returns:
        True if the post is a repost or quote (has a record embed), False otherwise
    """
    if not hasattr(post, "embed") or post.embed is None:
        return False

    # Check if it's a record embed (quote post)
    if isinstance(post.embed, RecordView):
        return True

    # Check if it's a record with media (quote post with images)
    if isinstance(post.embed, RecordWithMediaView):
        return True

    return False


def _is_reply(post: PostView) -> bool:
    """Check if a post is a reply to another post.

    Args:
        post: The post to check

    Returns:
        True if the post is a reply, False otherwise
    """
    # Check if the post record has a reply field with actual content
    try:
        reply = getattr(post.record, "reply", None)
        return reply is not None
    except AttributeError:
        return False


def display_post(post: PostView) -> Table:
    """Display a post in the terminal as a table."""
    # Convert AT URI to web URL
    web_url = _at_uri_to_web_url(post.uri, post.author.handle)

    # Create clickable title
    title = f"{post.author.display_name} (@{post.author.handle})"

    # Add appropriate emoji indicator
    # Priority: reply > repost/quote > image
    if _is_reply(post):
        title = f"⤴️ {title}"
    elif _is_repost_or_quote(post):
        title = f"🔁 {title}"
    elif _has_image(post):
        title = f"📷 {title}"

    clickable_title = f"[link={web_url}]{title}[/link]"

    table = Table(title=clickable_title, show_header=True, expand=True)
    # Use overflow="fold" to wrap text instead of truncating with ellipsis
    table.add_column("Post", style="white", overflow="fold")
    table.add_column("Likes", justify="right", style="green", overflow="fold")

    # Render text with clickable links using facets if available
    text = post.record.text if hasattr(post.record, "text") else ""
    facets = post.record.facets if hasattr(post.record, "facets") else None
    rendered_text = _render_text_with_links(text, facets)

    likes = post.like_count or 0
    table.add_row(rendered_text, str(likes))
    return table


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
