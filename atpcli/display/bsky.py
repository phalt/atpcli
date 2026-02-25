import re
from typing import Any, List, Optional

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


def _get_embedded_post(post: PostView, client=None) -> Optional[Any]:
    """Extract the embedded post from a repost or reply.

    Args:
        post: The post to check
        client: Optional atproto client for fetching reply parents

    Returns:
        The embedded post object if available, None otherwise
    """
    # Check for reply parent
    # Note: The timeline API provides post.reply with hydrated parent data,
    # but it's not always present. If missing, we can fetch it using the URI.
    if hasattr(post, "reply") and post.reply is not None:
        parent = getattr(post.reply, "parent", None)
        if parent:
            return parent

    # If no hydrated reply but we have a reply reference and a client, fetch the parent
    if client and hasattr(post.record, "reply") and post.record.reply is not None:
        try:
            parent_ref = getattr(post.record.reply, "parent", None)
            if parent_ref and hasattr(parent_ref, "uri"):
                # Fetch the parent post using get_posts
                result = client.get_posts([parent_ref.uri])
                if result and result.posts and len(result.posts) > 0:
                    return result.posts[0]
        except Exception:
            # If fetching fails, just skip showing the parent
            pass

    # Check for repost/quote embed
    if hasattr(post, "embed") and post.embed is not None:
        if isinstance(post.embed, RecordView):
            # Direct record embed (quote post)
            return getattr(post.embed, "record", None)
        elif isinstance(post.embed, RecordWithMediaView):
            # Record with media (quote post with images)
            return getattr(post.embed, "record", None)

    return None


def _display_embedded_post(embedded_post) -> Optional[Table]:
    """Display an embedded post as a smaller nested table.

    Args:
        embedded_post: The embedded post object (ViewRecord or PostView)

    Returns:
        Rich Table with the embedded post, or None if cannot be displayed
    """
    if not embedded_post:
        return None

    try:
        # Extract author info
        author = getattr(embedded_post, "author", None)
        if not author:
            return None

        author_name = getattr(author, "display_name", None) or getattr(author, "handle", "Unknown")
        author_handle = getattr(author, "handle", "")

        # Extract post content
        # Quote posts (ViewRecord) have .value.text
        # Reply parents (PostView) have .record.text
        text = ""
        value = getattr(embedded_post, "value", None)
        if value:
            # This is a ViewRecord from a quote post
            text = getattr(value, "text", "")
        else:
            # This might be a PostView from a reply parent
            record = getattr(embedded_post, "record", None)
            if record:
                text = getattr(record, "text", "")

        if not text:
            # If we still don't have text, try to return None
            return None

        # Extract like count if available (may not be present in all embed types)
        like_count = getattr(embedded_post, "like_count", 0) or 0

        # Create a smaller nested table
        nested_table = Table(show_header=False, box=None, padding=(0, 1))
        nested_table.add_column("Content", style="dim white", overflow="fold")
        nested_table.add_column("Likes", justify="right", style="dim green", overflow="fold", width=6)

        # Format the embedded post
        header = Text()
        header.append("   ↳ ", style="dim")
        header.append(f"{author_name}", style="dim bold")
        if author_handle:
            header.append(f" @{author_handle}", style="dim")

        content = Text()
        content.append("\n", style="dim")
        content.append(f"     {text}", style="dim")

        nested_table.add_row(header, "")
        nested_table.add_row(content, str(like_count) if like_count > 0 else "")

        return nested_table
    except Exception:
        # If anything fails, return None and don't show embedded post
        return None


def display_post(post: PostView, client=None) -> Table:
    """Display a post in the terminal as a table.

    Args:
        post: The post to display
        client: Optional atproto client for fetching reply parents

    Returns:
        Rich Table with the formatted post
    """
    # Convert AT URI to web URL
    web_url = _at_uri_to_web_url(post.uri, post.author.handle)

    # Create clickable title (WITHOUT DID)
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
    
    # Add DID on a separate line (not part of the link)
    full_title = f"{clickable_title}\n[dim]{post.author.did}[/dim]"

    table = Table(title=full_title, show_header=True, expand=True)
    # Use overflow="fold" to wrap text instead of truncating with ellipsis
    table.add_column("Post", style="white", overflow="fold")
    table.add_column("Likes", justify="right", style="green", overflow="fold")

    # Render text with clickable links using facets if available
    text = post.record.text if hasattr(post.record, "text") else ""
    facets = post.record.facets if hasattr(post.record, "facets") else None
    rendered_text = _render_text_with_links(text, facets)

    likes = post.like_count or 0
    table.add_row(rendered_text, str(likes))

    # Add embedded post if this is a quote post or reply
    embedded_post = _get_embedded_post(post, client)
    if embedded_post:
        nested_table = _display_embedded_post(embedded_post)
        if nested_table:
            table.add_row(nested_table, "")

    return table


def display_feeds(feed_details: List[dict]) -> Table:
    """Display a list of feeds as a table.

    Args:
        feed_details: List of dictionaries with 'name', 'uri', and 'description' keys

    Returns:
        Rich Table with the formatted feeds
    """
    table = Table(title=f"Saved Feeds ({len(feed_details)})", show_header=True, expand=True)
    table.add_column("Feed Name", style="cyan", overflow="fold")
    table.add_column("URI", style="dim white", overflow="fold")
    table.add_column("Description", style="white", overflow="fold")

    for feed in feed_details:
        table.add_row(feed["name"], feed["uri"], feed["description"])

    return table


def display_profile(profile) -> None:
    """Display a user profile in the terminal.

    Args:
        profile: Profile object from atproto
    """
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text

    console = Console()

    # Title with name and handle
    title = f"{profile.display_name or profile.handle} (@{profile.handle})"

    # Build content
    content = Text()

    # DID (for copy/paste)
    content.append("DID: ", style="dim")
    content.append(f"{profile.did}\n\n", style="dim cyan")

    # Bio/Description
    if profile.description:
        content.append("Bio: ", style="bold")
        content.append(f"{profile.description}\n\n")

    # Stats
    content.append("📊 Stats\n", style="bold cyan")
    content.append(f"  • {profile.followers_count or 0:,} followers\n")
    content.append(f"  • {profile.follows_count or 0:,} following\n")
    content.append(f"  • {profile.posts_count or 0:,} posts\n\n")

    # Links
    content.append("🔗 Links\n", style="bold cyan")
    profile_url = f"https://bsky.app/profile/{profile.handle}"
    content.append("  Profile: ")
    content.append(profile_url, style="link " + profile_url)
    content.append("\n")

    if profile.avatar:
        content.append("  Avatar:  ")
        content.append(profile.avatar, style="dim")
        content.append("\n")

    # Create panel
    panel = Panel(content, title=title, border_style="blue")
    console.print(panel)


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
