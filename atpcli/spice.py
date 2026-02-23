"""Spice commands for atpcli."""

from datetime import datetime, timezone

import click
from atproto import Client
from atproto.exceptions import AtProtocolError
from pydantic import ValidationError
from rich.console import Console

from atpcli.config import Config
from atpcli.constants import SPICE_COLLECTION_NAME, SPICE_MAX_TEXT_LENGTH
from atpcli.models import SpiceNote

console = Console()


def parse_at_uri(at_uri: str) -> tuple[str, str, str]:
    """Parse an AT URI into its components.
    
    Args:
        at_uri: The AT URI to parse (e.g., at://did:plc:xxx/collection/rkey)
        
    Returns:
        Tuple of (repo_did, collection, rkey)
        
    Raises:
        ValueError: If the URI format is invalid
    """
    if not at_uri.startswith("at://"):
        raise ValueError(f"AT URI must start with 'at://': {at_uri}")
    
    parts = at_uri.replace("at://", "").split("/")
    if len(parts) != 3:
        raise ValueError(f"Invalid AT URI format (expected at://did/collection/rkey): {at_uri}")
    
    return parts[0], parts[1], parts[2]


@click.group()
def spice():
    """Commands for Spice - web annotations on AT Protocol.
    
    Sprinkle some spice across the web: https://spice.tools
    """
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

    # Set createdAt to current UTC time in RFC 3339 format
    created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # Validate and create the note model
    try:
        note = SpiceNote(url=url, text=text, createdAt=created_at)
    except ValidationError as e:
        for error in e.errors():
            field = error["loc"][0]
            msg = error["msg"]
            if field == "url":
                console.print(f"[red]✗ Invalid URL: {url}[/red]")
                console.print(f"[yellow]{msg}[/yellow]")
            elif field == "text":
                if "String should have at most" in msg:
                    console.print(
                        f"[red]✗ Text is too long: {len(text)} characters (max {SPICE_MAX_TEXT_LENGTH})[/red]"
                    )
                else:
                    console.print(f"[red]✗ {msg}[/red]")
        raise SystemExit(1)

    # Create the record
    try:
        client = Client()
        console.print(f"[blue]Creating note for {url}...[/blue]")

        # Restore session
        client.login(session_string=session_string)

        # Create the record using pydantic model
        record = note.to_record()

        response = client.com.atproto.repo.create_record(
            {
                "repo": client.me.did,
                "collection": SPICE_COLLECTION_NAME,
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
@click.option("--limit", default=None, type=int, help="Maximum number of matching notes to display")
@click.option("--all", "fetch_all", is_flag=True, help="Fetch all records across all pages")
def list(url: str, limit: int, fetch_all: bool):
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

        # Collect all matching records
        all_matching_records = []
        cursor = None
        api_page_size = 100  # Use larger page size for API calls to reduce requests

        while True:
            # List records in the collection with pagination
            params = {
                "repo": client.me.did,
                "collection": SPICE_COLLECTION_NAME,
                "limit": api_page_size,
            }
            if cursor:
                params["cursor"] = cursor

            response = client.com.atproto.repo.list_records(params)

            # Filter for matching URL
            matching_records = [r for r in response.records if r.value.get("url") == url]
            all_matching_records.extend(matching_records)

            # Check if we've reached the limit
            if limit is not None and len(all_matching_records) >= limit:
                all_matching_records = all_matching_records[:limit]
                break

            # Check if we should continue pagination
            cursor = getattr(response, "cursor", None)
            if not cursor or not fetch_all:
                break

        if not all_matching_records:
            console.print(f"[yellow]No notes found for {url}[/yellow]")
            return

        # Reverse the order to show latest at the bottom
        all_matching_records.reverse()

        # Display each matching record
        console.print(f"\n[green]Found {len(all_matching_records)} note(s):[/green]\n")
        for record in all_matching_records:
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
    try:
        repo_did, collection, rkey = parse_at_uri(at_uri)
    except ValueError as e:
        console.print(f"[red]✗ {e}[/red]")
        console.print("[yellow]Expected format: at://did:plc:xxx/collection/rkey[/yellow]")
        raise SystemExit(1)

    # Validate collection
    if collection != SPICE_COLLECTION_NAME:
        console.print(f"[red]✗ Invalid collection: {collection}[/red]")
        console.print(f"[yellow]This command only deletes {SPICE_COLLECTION_NAME} records[/yellow]")
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
