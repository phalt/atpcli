"""Spice commands for atpcli."""

from datetime import datetime, timezone
from urllib.parse import urlparse

import click
from atproto import Client
from atproto.exceptions import AtProtocolError
from rich.console import Console

from atpcli.config import Config

console = Console()

COLLECTION_NAME = "tools.spice.note"
MAX_TEXT_LENGTH = 256


@click.group()
def spice():
    """Commands for Spice - web annotations on AT Protocol."""
    pass


@spice.command()
@click.argument("url")
@click.argument("text")
def add(url: str, text: str):
    """Add a new note to a URL.

    Creates a new tools.spice.note record in your personal data repository.

    URL: The fully-qualified URL to annotate (e.g., https://example.com/page)
    TEXT: The annotation text (max 256 characters, plain text only)
    """
    # Load session
    config = Config()
    handle, session_string = config.load_session()

    if not session_string:
        console.print("[red]✗ Not logged in. Please run 'atpcli bsky login' first.[/red]")
        raise SystemExit(1)

    # Validate URL
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            console.print(f"[red]✗ Invalid URL: {url}[/red]")
            console.print("[yellow]URL must include scheme and host (e.g., https://example.com)[/yellow]")
            raise SystemExit(1)
    except Exception as e:
        console.print(f"[red]✗ Invalid URL: {e}[/red]")
        raise SystemExit(1)

    # Validate text length
    if not text or not text.strip():
        console.print("[red]✗ Text cannot be empty.[/red]")
        raise SystemExit(1)

    if len(text) > MAX_TEXT_LENGTH:
        console.print(f"[red]✗ Text is too long: {len(text)} characters (max {MAX_TEXT_LENGTH})[/red]")
        raise SystemExit(1)

    # Create the record
    try:
        client = Client()
        console.print(f"[blue]Creating note for {url}...[/blue]")

        # Restore session
        client.login(session_string=session_string)

        # Set createdAt to current UTC time in RFC 3339 format
        created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        # Create the record
        record = {
            "url": url,
            "text": text,
            "createdAt": created_at,
            "$type": COLLECTION_NAME,
        }

        response = client.com.atproto.repo.create_record(
            {
                "repo": client.me.did,
                "collection": COLLECTION_NAME,
                "record": record,
            }
        )

        # Use the AT URI returned by the server
        at_uri = response.uri

        console.print(f"[green]✓ Created: {at_uri}[/green]")

    except AtProtocolError as e:
        console.print(f"[red]✗ Failed to create note: {e}[/red]")
        console.print("[yellow]Your session may have expired. Try logging in again.[/yellow]")
        raise SystemExit(1)
    except Exception as e:
        console.print(f"[red]✗ Failed to create note: {e}[/red]")
        raise SystemExit(1)


@spice.command()
@click.argument("url")
def list(url: str):
    """List all your notes for a URL.

    Shows all tools.spice.note records you have created for the given URL.

    URL: The URL to query for notes
    """
    # Load session
    config = Config()
    handle, session_string = config.load_session()

    if not session_string:
        console.print("[red]✗ Not logged in. Please run 'atpcli bsky login' first.[/red]")
        raise SystemExit(1)

    try:
        client = Client()
        console.print(f"[blue]Loading notes for {url}...[/blue]")

        # Restore session
        client.login(session_string=session_string)

        # List all records in the collection
        response = client.com.atproto.repo.list_records(
            {
                "repo": client.me.did,
                "collection": COLLECTION_NAME,
            }
        )

        # Filter for matching URL
        matching_records = [r for r in response.records if r.value.get("url") == url]

        if not matching_records:
            console.print(f"[yellow]No notes found for {url}[/yellow]")
            return

        # Display each matching record
        console.print(f"\n[green]Found {len(matching_records)} note(s):[/green]\n")
        for record in matching_records:
            # Use the AT URI from the record
            at_uri = record.uri
            created_at = record.value.get("createdAt", "")
            text = record.value.get("text", "")

            console.print(f"[cyan]{at_uri}[/cyan]  [dim]{created_at}[/dim]")
            console.print(f"{text}\n")

    except AtProtocolError as e:
        console.print(f"[red]✗ Failed to list notes: {e}[/red]")
        console.print("[yellow]Your session may have expired. Try logging in again.[/yellow]")
        raise SystemExit(1)
    except Exception as e:
        console.print(f"[red]✗ Failed to list notes: {e}[/red]")
        raise SystemExit(1)


@spice.command()
@click.argument("at_uri")
def delete(at_uri: str):
    """Delete a note by its AT URI.

    Removes a tools.spice.note record from your personal data repository.

    AT_URI: The at:// URI of the note to delete (e.g., at://did:plc:abc/tools.spice.note/123)
    """
    # Load session
    config = Config()
    handle, session_string = config.load_session()

    if not session_string:
        console.print("[red]✗ Not logged in. Please run 'atpcli bsky login' first.[/red]")
        raise SystemExit(1)

    # Parse and validate AT URI
    if not at_uri.startswith("at://"):
        console.print(f"[red]✗ Invalid AT URI: {at_uri}[/red]")
        console.print("[yellow]AT URI must start with 'at://'[/yellow]")
        raise SystemExit(1)

    try:
        # Parse AT URI: at://did/collection/rkey
        parts = at_uri.replace("at://", "").split("/")
        if len(parts) != 3:
            console.print(f"[red]✗ Invalid AT URI format: {at_uri}[/red]")
            console.print("[yellow]Expected format: at://did:plc:xxx/collection/rkey[/yellow]")
            raise SystemExit(1)

        repo_did, collection, rkey = parts

        # Validate collection
        if collection != COLLECTION_NAME:
            console.print(f"[red]✗ Invalid collection: {collection}[/red]")
            console.print(f"[yellow]This command only deletes {COLLECTION_NAME} records[/yellow]")
            raise SystemExit(1)

    except ValueError as e:
        console.print(f"[red]✗ Failed to parse AT URI: {e}[/red]")
        raise SystemExit(1)

    # Delete the record
    try:
        client = Client()
        console.print(f"[blue]Deleting note {at_uri}...[/blue]")

        # Restore session
        client.login(session_string=session_string)

        # Delete the record
        client.com.atproto.repo.delete_record(
            {
                "repo": client.me.did,
                "collection": collection,
                "rkey": rkey,
            }
        )

        console.print(f"[green]✓ Deleted: {at_uri}[/green]")

    except AtProtocolError as e:
        console.print(f"[red]✗ Failed to delete note: {e}[/red]")
        if "not found" in str(e).lower():
            console.print("[yellow]Record may not exist or may have already been deleted.[/yellow]")
        else:
            console.print("[yellow]Your session may have expired. Try logging in again.[/yellow]")
        raise SystemExit(1)
    except Exception as e:
        console.print(f"[red]✗ Failed to delete note: {e}[/red]")
        raise SystemExit(1)
