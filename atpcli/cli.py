"""CLI commands for atpcli."""

import textwrap

import click
from atproto import Client, SessionEvent
from rich.console import Console

from atpcli.config import Config
from atpcli.display import display_post
from atpcli.spice import spice

console = Console()


def create_client_with_session_refresh(config: Config, handle: str, session_string: str) -> Client:
    """Create a client with automatic session refresh.
    
    Args:
        config: Config instance for saving refreshed session
        handle: User handle
        session_string: Current session string
        
    Returns:
        Configured Client instance
    """
    client = Client()
    
    # Register callback to save refreshed sessions
    def on_session_change(event: SessionEvent, session) -> None:
        if event in (SessionEvent.CREATE, SessionEvent.REFRESH):
            # Save the refreshed session
            new_session_string = client.export_session_string()
            config.save_session(handle, new_session_string)
    
    client.on_session_change(on_session_change)
    
    # Restore session from saved string
    client.login(session_string=session_string)
    
    return client

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


@bsky.command()
@click.option("--handle", prompt="Handle", help="Your Bluesky handle")
@click.option("--password", prompt="Password", hide_input=True, help="Your Bluesky password")
def login(handle: str, password: str):
    """Login to Bluesky and save session."""
    try:
        client = Client()
        console.print(f"[blue]Logging in as {handle}...[/blue]")
        profile = client.login(handle, password)

        # Get the session string from the client
        session_string = client.export_session_string()

        # Save the session
        config = Config()
        config.save_session(handle, session_string)

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
    handle, session_string = config.load_session()

    if not session_string:
        console.print("[red]✗ Not logged in. Please run 'atpcli bsky login' first.[/red]")
        raise SystemExit(1)

    try:
        console.print(f"[blue]Loading timeline for {handle}...[/blue]")

        # Create client with automatic session refresh
        client = create_client_with_session_refresh(config, handle, session_string)

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
            table = display_post(post)
            console.print(table)

        # Show pagination info
        page_info = f"[dim]Showing {len(timeline_response.feed)} posts (page {page})"
        if timeline_response.cursor:
            page_info += f" - Use --p {page + 1} for next page"
        page_info += "[/dim]"
        console.print(f"\n{page_info}")

    except Exception as e:
        console.print(f"[red]✗ Failed to load timeline: {e}[/red]")
        raise SystemExit(1)


@bsky.command()
@click.option("--message", "-m", required=True, help="Message to post")
def post(message: str):
    """Post a message to Bluesky."""
    config = Config()
    handle, session_string = config.load_session()

    if not session_string:
        console.print("[red]✗ Not logged in. Please run 'atpcli bsky login' first.[/red]")
        raise SystemExit(1)

    try:
        console.print(f"[blue]Posting as {handle}...[/blue]")

        # Create client with automatic session refresh
        client = create_client_with_session_refresh(config, handle, session_string)

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


if __name__ == "__main__":
    cli()
