"""Session management utilities for atpcli."""

from atproto import Client, SessionEvent

from atpcli.config import Config
from atpcli.constants import DEFAULT_PDS_URL


def create_client_with_session_refresh(
    config: Config, handle: str, session_string: str, pds_url: str = DEFAULT_PDS_URL
) -> Client:
    """Create a client with automatic session refresh.

    This function creates an atproto Client instance and registers a callback to
    automatically save refreshed sessions. When the session expires, the atproto
    client will automatically refresh it and trigger the callback to save the new
    session to the config file.

    Args:
        config: Config instance for saving refreshed session
        handle: User handle
        session_string: Current session string
        pds_url: PDS base URL (defaults to https://bsky.social)

    Returns:
        Configured Client instance with session refresh callback registered

    Note:
        The atproto client handles session refresh automatically. This function
        ensures that refreshed sessions are persisted to disk.
    """
    client = Client(base_url=pds_url)

    # Register callback to save refreshed sessions
    def on_session_change(event: SessionEvent, session) -> None:
        if event in (SessionEvent.CREATE, SessionEvent.REFRESH):
            # Save the refreshed session
            new_session_string = client.export_session_string()
            config.save_session(handle, new_session_string, pds_url)

    client.on_session_change(on_session_change)

    # Restore session from saved string
    client.login(session_string=session_string)

    return client
