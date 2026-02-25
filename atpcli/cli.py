"""CLI commands for atpcli."""

import os
import subprocess
import tempfile
import textwrap

import click
from atproto import Client
from rich.console import Console

from atpcli.config import Config
from atpcli.constants import DEFAULT_PDS_URL
from atpcli.display.bsky import display_feeds, display_post, display_profile
from atpcli.session import create_client_with_session_refresh
from atpcli.spice import spice

console = Console()

atpcli_HEADER = r"""
                  _  _
  __ _ _ __  ____| (_)
 / _` | '_ \/ ___| | |
| (_| | |_) | (__| | |
 \__,_| .__/ \___|_|_|
      |_|
""".strip("\n")


@click.group()
def cli():
    """atpcli - A Python CLI wrapper around the atproto package."""
    pass


cli.help = textwrap.dedent(f"""\
\b
{atpcli_HEADER}

🦋 atpcli - A Python CLI wrapper around the atproto package

📚 GitHub: https://github.com/phalt/atpcli

""").strip("\n")


@click.group()
def bsky():
    """Commands for interacting with Bluesky."""
    pass


cli.add_command(bsky)
cli.add_command(spice)


@cli.command()
@click.argument("pds_url", required=False, default=DEFAULT_PDS_URL)
@click.option("--handle", prompt="Handle", help="Your AT Protocol handle")
@click.option("--password", prompt="Password", hide_input=True, help="Your app password")
def login(pds_url: str, handle: str, password: str):
    """Login to an AT Protocol PDS and save session."""
    try:
        client = Client(base_url=pds_url)
        console.print(f"[blue]Logging in to {pds_url} as {handle}...[/blue]")
        profile = client.login(handle, password)

        # Get the session string from the client
        session_string = client.export_session_string()

        # Save the session
        config = Config()
        config.save_session(handle, session_string, pds_url)

        console.print(f"[green]✓ Successfully logged in as {profile.display_name or handle}[/green]")
        console.print(f"[dim]Session saved to {config.config_file}[/dim]")
    except Exception as e:
        console.print(f"[red]✗ Login failed: {e}[/red]")
        raise SystemExit(1)


@bsky.command()
@click.option("--limit", default=10, help="Number of posts to show")
@click.option("--p", "page", default=1, help="Page number to load")
def timeline(limit: int, page: int):
    """View your timeline."""
    config = Config()
    handle, session_string, pds_url = config.load_session()

    if not session_string:
        console.print("[red]✗ Not logged in. Please run 'atpcli login' first.[/red]")
        raise SystemExit(1)

    try:
        console.print(f"[blue]Loading timeline for {handle}...[/blue]")

        # Create client with automatic session refresh
        client = create_client_with_session_refresh(config, handle, session_string, pds_url)

        # Calculate cursor position for pagination
        # Note: We need to fetch pages sequentially to get the cursor for each page.
        # This means accessing page N requires N API calls, which can be slow for high page numbers.
        cursor = None
        if page > 5:
            warning_msg = f"[yellow]⚠ Loading page {page} requires {page} API calls. This may take a moment...[/yellow]"
            console.print(warning_msg)

        for i in range(1, page):
            response = client.get_timeline(limit=limit, cursor=cursor)
            cursor = response.cursor
            if not cursor:
                console.print(f"[yellow]⚠ Page {page} does not exist. Showing last available page (page {i}).[/yellow]")
                page = i
                break

        # Get the requested page
        timeline_response = client.get_timeline(limit=limit, cursor=cursor)

        # Reverse the feed so latest posts appear at the bottom
        # This allows users to scroll up to read
        reversed_feed = list(reversed(timeline_response.feed))

        for feed_view in reversed_feed:
            post = feed_view.post
            table = display_post(post, client)
            console.print(table)

        # Show pagination info
        post_count = len(timeline_response.feed)
        post_word = "post" if post_count == 1 else "posts"
        page_info = f"[dim]Showing {post_count} {post_word} (page {page})"
        if timeline_response.cursor:
            page_info += f" - Use --p {page + 1} for next page"
        page_info += "[/dim]"
        console.print(f"\n{page_info}")

    except Exception as e:
        console.print(f"[red]✗ Failed to load timeline: {e}[/red]")
        raise SystemExit(1)


def get_message_from_editor():
    """Open an editor for the user to compose a message."""
    # Determine which editor to use
    editor = os.environ.get("EDITOR")
    if not editor:
        # Try to find vim or vi
        for candidate in ["vim", "vi"]:
            try:
                subprocess.run([candidate, "--version"], capture_output=True, check=True)
                editor = candidate
                break
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue

    if not editor:
        console.print("[red]✗ No editor found. Please set the EDITOR environment variable or install vim/vi.[/red]")
        raise SystemExit(1)

    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as tf:
        temp_file = tf.name
        # Add a comment to help the user
        tf.write("\n# Enter your message above this line. Lines starting with # will be ignored.\n")
        tf.write("# Save and exit the editor to post your message.\n")

    try:
        # Open the editor
        subprocess.run([editor, temp_file], check=True)

        # Read the content
        with open(temp_file, "r") as f:
            lines = f.readlines()

        # Filter out comment lines and empty lines at the end
        message_lines = []
        for line in lines:
            if not line.startswith("#"):
                message_lines.append(line)

        message = "".join(message_lines).strip()

        if not message:
            console.print("[yellow]⚠ Empty message. Post cancelled.[/yellow]")
            raise SystemExit(0)

        return message
    finally:
        # Clean up the temporary file
        try:
            os.unlink(temp_file)
        except OSError:
            pass


@bsky.command()
@click.option("--message", "-m", required=False, help="Message to post (if not provided, opens editor)")
def post(message: str):
    """Post a message to Bluesky."""
    config = Config()
    handle, session_string, pds_url = config.load_session()

    if not session_string:
        console.print("[red]✗ Not logged in. Please run 'atpcli login' first.[/red]")
        raise SystemExit(1)

    # If no message provided, open editor
    if not message:
        message = get_message_from_editor()

    try:
        console.print(f"[blue]Posting as {handle}...[/blue]")

        # Create client with automatic session refresh
        client = create_client_with_session_refresh(config, handle, session_string, pds_url)

        # Send the post
        response = client.send_post(text=message)

        # Convert AT URI to web URL
        post_id = response.uri.split("/")[-1]
        web_url = f"https://bsky.app/profile/{handle}/post/{post_id}"

        console.print("[green]✓ Post created successfully![/green]")
        console.print(f"[blue]View your post at: [link={web_url}]{web_url}[/link][/blue]")

    except Exception as e:
        console.print(f"[red]✗ Failed to post: {e}[/red]")
        raise SystemExit(1)


@bsky.command()
@click.option("--format", "output_format", type=click.Choice(["table", "uri"]), default="table", help="Output format")
def feeds(output_format: str):
    """List your saved feeds."""
    config = Config()
    handle, session_string, pds_url = config.load_session()

    if not session_string:
        console.print("[red]✗ Not logged in. Please run 'atpcli login' first.[/red]")
        raise SystemExit(1)

    try:
        console.print(f"[blue]Loading saved feeds for {handle}...[/blue]")

        # Create client with automatic session refresh
        client = create_client_with_session_refresh(config, handle, session_string, pds_url)

        # Get user preferences which includes saved feeds
        preferences = client.app.bsky.actor.get_preferences()

        # Extract saved feeds from preferences
        saved_feeds = []
        for pref in preferences.preferences:
            if hasattr(pref, "py_type") and pref.py_type == "app.bsky.actor.defs#savedFeedsPref":
                # This preference contains saved feed URIs
                if hasattr(pref, "saved"):
                    saved_feeds = pref.saved
                elif hasattr(pref, "pinned"):
                    saved_feeds = pref.pinned
                break

        if not saved_feeds:
            console.print("[yellow]No saved feeds found.[/yellow]")
            console.print("[dim]Save feeds in the Bluesky app to see them here.[/dim]")
            return

        # Output URI-only format
        if output_format == "uri":
            for feed_uri in saved_feeds:
                console.print(feed_uri)
            return

        # Fetch detailed feed information for table format
        feed_details = []
        for feed_uri in saved_feeds:
            try:
                feed_info = client.app.bsky.feed.get_feed_generator({"feed": feed_uri})
                feed_details.append(
                    {
                        "name": feed_info.view.display_name,
                        "uri": feed_uri,
                        "description": getattr(feed_info.view, "description", ""),
                    }
                )
            except Exception:
                # If we can't fetch details, just show the URI
                feed_details.append({"name": feed_uri.split("/")[-1], "uri": feed_uri, "description": ""})

        # Display table using display function
        table = display_feeds(feed_details)
        console.print(table)
        console.print("\n[dim]Use 'atpcli bsky feed <uri>' to view posts from a specific feed.[/dim]")

    except Exception as e:
        console.print(f"[red]✗ Failed to load feeds: {e}[/red]")
        raise SystemExit(1)


@bsky.command()
@click.argument("feed_uri")
@click.option("--limit", default=10, help="Number of posts to show")
@click.option("--p", "page", default=1, help="Page number to load")
def feed(feed_uri: str, limit: int, page: int):
    """View posts from a specific feed."""
    config = Config()
    handle, session_string, pds_url = config.load_session()

    if not session_string:
        console.print("[red]✗ Not logged in. Please run 'atpcli login' first.[/red]")
        raise SystemExit(1)

    try:
        console.print(f"[blue]Loading feed {feed_uri}...[/blue]")

        # Create client with automatic session refresh
        client = create_client_with_session_refresh(config, handle, session_string, pds_url)

        # Calculate cursor position for pagination (same logic as timeline)
        cursor = None
        if page > 5:
            warning_msg = f"[yellow]⚠ Loading page {page} requires {page} API calls. This may take a moment...[/yellow]"
            console.print(warning_msg)

        for i in range(1, page):
            response = client.app.bsky.feed.get_feed({"feed": feed_uri, "limit": limit, "cursor": cursor})
            cursor = response.cursor
            if not cursor:
                console.print(f"[yellow]⚠ Page {page} does not exist. Showing last available page (page {i}).[/yellow]")
                page = i
                break

        # Get the requested page
        feed_response = client.app.bsky.feed.get_feed({"feed": feed_uri, "limit": limit, "cursor": cursor})

        if not feed_response.feed:
            console.print("[yellow]This feed has no posts.[/yellow]")
            return

        # Reverse the feed so latest posts appear at the bottom (same as timeline)
        reversed_feed = list(reversed(feed_response.feed))

        for feed_view in reversed_feed:
            post = feed_view.post
            table = display_post(post, client)
            console.print(table)

        # Show pagination info (same as timeline)
        post_count = len(feed_response.feed)
        post_word = "post" if post_count == 1 else "posts"
        page_info = f"[dim]Showing {post_count} {post_word} (page {page})"
        if feed_response.cursor:
            page_info += f" - Use --p {page + 1} for next page"
        page_info += "[/dim]"
        console.print(f"\n{page_info}")

    except Exception as e:
        console.print(f"[red]✗ Failed to load feed: {e}[/red]")
        raise SystemExit(1)


@bsky.command()
@click.argument("handle", required=False)
@click.option("--me", is_flag=True, help="View your own profile")
def profile(handle: str, me: bool):
    """View a user's profile."""
    config = Config()
    session_handle, session_string, pds_url = config.load_session()

    if not session_string:
        console.print("[red]✗ Not logged in. Please run 'atpcli login' first.[/red]")
        raise SystemExit(1)

    if me:
        handle = session_handle
    elif not handle:
        console.print("[red]✗ Please provide a handle or use --me[/red]")
        raise SystemExit(1)

    try:
        client = create_client_with_session_refresh(config, session_handle, session_string, pds_url)

        # Get profile
        profile_data = client.get_profile(handle)

        # Display using Rich formatting
        display_profile(profile_data)

    except Exception as e:
        console.print(f"[red]✗ Failed to load profile: {e}[/red]")
        raise SystemExit(1)


@bsky.command()
@click.argument("handle", required=False)
@click.option("--limit", default=10, help="Number of posts to show")
@click.option("--p", "page", default=1, help="Page number to load")
@click.option("--me", is_flag=True, help="View your own posts")
def posts(handle: str, limit: int, page: int, me: bool):
    """View posts from a specific user."""
    config = Config()
    session_handle, session_string, pds_url = config.load_session()

    if not session_string:
        console.print("[red]✗ Not logged in. Please run 'atpcli login' first.[/red]")
        raise SystemExit(1)

    if me:
        handle = session_handle
    elif not handle:
        console.print("[red]✗ Please provide a handle or use --me[/red]")
        raise SystemExit(1)

    try:
        console.print(f"[blue]Loading posts from {handle}...[/blue]")

        client = create_client_with_session_refresh(config, session_handle, session_string, pds_url)

        # Pagination logic (SAME as timeline)
        cursor = None
        if page > 5:
            console.print(f"[yellow]⚠ Loading page {page} requires {page} API calls. This may take a moment...[/yellow]")

        for i in range(1, page):
            response = client.get_author_feed(actor=handle, limit=limit, cursor=cursor)
            cursor = response.cursor
            if not cursor:
                console.print(f"[yellow]⚠ Page {page} does not exist. Showing last available page (page {i}).[/yellow]")
                page = i
                break

        # Get the requested page
        feed_response = client.get_author_feed(actor=handle, limit=limit, cursor=cursor)

        # Reverse feed (SAME as timeline)
        reversed_feed = list(reversed(feed_response.feed))

        # Display posts (SAME as timeline - reuse display_post!)
        # DIDs are automatically shown because display_post() includes them
        for feed_view in reversed_feed:
            post = feed_view.post
            table = display_post(post, client)
            console.print(table)

        # Pagination info (SAME as timeline)
        post_count = len(feed_response.feed)
        post_word = "post" if post_count == 1 else "posts"
        page_info = f"[dim]Showing {post_count} {post_word} (page {page})"
        if feed_response.cursor:
            page_info += f" - Use --p {page + 1} for next page"
        page_info += "[/dim]"
        console.print(f"\n{page_info}")

    except Exception as e:
        console.print(f"[red]✗ Failed to load posts: {e}[/red]")
        raise SystemExit(1)


if __name__ == "__main__":
    cli()
