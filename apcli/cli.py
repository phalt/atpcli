"""CLI commands for apcli."""


import click
from atproto import Client
from rich.console import Console
from rich.table import Table

from apcli.config import Config

console = Console()


@click.group()
def cli():
    """apcli - A Python CLI wrapper around the atproto package."""
    pass


@cli.command()
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
        raise click.Abort()


@cli.command()
@click.option("--limit", default=10, help="Number of posts to show")
def timeline(limit: int):
    """View your timeline."""
    config = Config()
    handle, session_string = config.load_session()

    if not session_string:
        console.print("[red]✗ Not logged in. Please run 'apcli login' first.[/red]")
        raise click.Abort()

    try:
        client = Client()
        console.print(f"[blue]Loading timeline for {handle}...[/blue]")

        # Restore session from saved string
        client.login(session_string=session_string)

        # Get timeline
        timeline_response = client.get_timeline(limit=limit)

        # Display posts in a nice table
        table = Table(title=f"Timeline for {handle}", show_header=True, header_style="bold magenta")
        table.add_column("Author", style="cyan", no_wrap=True)
        table.add_column("Post", style="white")
        table.add_column("Likes", justify="right", style="green")

        for feed_view in timeline_response.feed:
            post = feed_view.post
            author_display = post.author.display_name or post.author.handle
            text = post.record.text if hasattr(post.record, "text") else ""
            likes = post.like_count or 0

            # Truncate long posts
            if len(text) > 80:
                text = text[:77] + "..."

            table.add_row(author_display, text, str(likes))

        console.print(table)
        console.print(f"\n[dim]Showing {len(timeline_response.feed)} posts[/dim]")

    except Exception as e:
        console.print(f"[red]✗ Failed to load timeline: {e}[/red]")
        console.print("[yellow]Your session may have expired. Try logging in again.[/yellow]")
        raise click.Abort()


if __name__ == "__main__":
    cli()
