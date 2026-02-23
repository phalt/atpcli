"""Tests for Spice commands."""

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from atpcli.cli import cli
from atpcli.spice import parse_at_uri


@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()


def test_parse_at_uri_valid():
    """Test parsing valid AT URI."""
    repo_did, collection, rkey = parse_at_uri("at://did:plc:test123/tools.spice.note/abc123")
    assert repo_did == "did:plc:test123"
    assert collection == "tools.spice.note"
    assert rkey == "abc123"


def test_parse_at_uri_invalid_no_scheme():
    """Test parsing AT URI without scheme."""
    with pytest.raises(ValueError, match="AT URI must start with 'at://'"):
        parse_at_uri("did:plc:test123/tools.spice.note/abc123")


def test_parse_at_uri_invalid_format():
    """Test parsing AT URI with invalid format."""
    with pytest.raises(ValueError, match="Invalid AT URI format"):
        parse_at_uri("at://invalid")


def test_spice_group(runner):
    """Test that spice group runs."""
    result = runner.invoke(cli, ["spice", "--help"])
    assert result.exit_code == 0
    assert "Spice" in result.output
    assert "web annotations" in result.output


def test_add_command_help(runner):
    """Test add command help."""
    result = runner.invoke(cli, ["spice", "add", "--help"])
    assert result.exit_code == 0
    assert "Add a new note to a URL" in result.output


def test_list_command_help(runner):
    """Test list command help."""
    result = runner.invoke(cli, ["spice", "list", "--help"])
    assert result.exit_code == 0
    assert "List all your notes for a URL" in result.output


def test_delete_command_help(runner):
    """Test delete command help."""
    result = runner.invoke(cli, ["spice", "delete", "--help"])
    assert result.exit_code == 0
    assert "Delete a note by its AT URI" in result.output


@patch("atpcli.spice.create_client_with_session_refresh")
@patch("atpcli.spice.Config")
def test_add_not_logged_in(mock_config_class, mock_create_client, runner):
    """Test add when not logged in."""
    mock_config = MagicMock()
    mock_config.load_session.return_value = (None, None)
    mock_config_class.return_value = mock_config

    result = runner.invoke(cli, ["spice", "add", "https://example.com", "Test note"])

    assert result.exit_code == 1
    assert "Not logged in" in result.output


@patch("atpcli.spice.create_client_with_session_refresh")
@patch("atpcli.spice.Config")
def test_add_invalid_url_no_scheme(mock_config_class, mock_create_client, runner):
    """Test add with invalid URL (no scheme)."""
    mock_config = MagicMock()
    mock_config.load_session.return_value = ("test.bsky.social", "test_session")
    mock_config_class.return_value = mock_config

    result = runner.invoke(cli, ["spice", "add", "example.com", "Test note"])

    assert result.exit_code == 1
    assert "Invalid URL" in result.output


@patch("atpcli.spice.create_client_with_session_refresh")
@patch("atpcli.spice.Config")
def test_add_empty_text(mock_config_class, mock_create_client, runner):
    """Test add with empty text."""
    mock_config = MagicMock()
    mock_config.load_session.return_value = ("test.bsky.social", "test_session")
    mock_config_class.return_value = mock_config

    result = runner.invoke(cli, ["spice", "add", "https://example.com", ""])

    assert result.exit_code == 1
    assert "Text cannot be empty" in result.output


@patch("atpcli.spice.create_client_with_session_refresh")
@patch("atpcli.spice.Config")
def test_add_text_too_long(mock_config_class, mock_create_client, runner):
    """Test add with text exceeding max length."""
    mock_config = MagicMock()
    mock_config.load_session.return_value = ("test.bsky.social", "test_session")
    mock_config_class.return_value = mock_config

    # Create text longer than 256 characters
    long_text = "x" * 257

    result = runner.invoke(cli, ["spice", "add", "https://example.com", long_text])

    assert result.exit_code == 1
    assert "Text is too long" in result.output
    assert "257 characters" in result.output


@patch("atpcli.spice.create_client_with_session_refresh")
@patch("atpcli.spice.Config")
def test_add_success(mock_config_class, mock_create_client, runner):
    """Test successful note creation."""
    # Setup mocks
    mock_client = MagicMock()
    mock_create_client.return_value = mock_client
    mock_client.me.did = "did:plc:test123"

    # Mock create_record response
    mock_response = MagicMock()
    mock_response.uri = "at://did:plc:test123/tools.spice.note/abc123xyz"
    mock_client.com.atproto.repo.create_record.return_value = mock_response

    # Mock config
    mock_config = MagicMock()
    mock_config.load_session.return_value = ("test.bsky.social", "test_session")
    mock_config_class.return_value = mock_config

    # Run add
    result = runner.invoke(cli, ["spice", "add", "https://example.com/page", "Great article!"])

    # Verify
    assert result.exit_code == 0
    assert "Created: at://did:plc:test123/tools.spice.note/abc123xyz" in result.output
    mock_create_client.assert_called_once_with(mock_config, "test.bsky.social", "test_session")

    # Verify create_record was called with correct parameters
    call_args = mock_client.com.atproto.repo.create_record.call_args
    assert call_args is not None
    record_data = call_args[0][0]
    assert record_data["repo"] == "did:plc:test123"
    assert record_data["collection"] == "tools.spice.note"
    assert record_data["record"]["url"] == "https://example.com/page"
    assert record_data["record"]["text"] == "Great article!"
    assert "createdAt" in record_data["record"]


@patch("atpcli.spice.create_client_with_session_refresh")
@patch("atpcli.spice.Config")
def test_list_not_logged_in(mock_config_class, mock_create_client, runner):
    """Test list when not logged in."""
    mock_config = MagicMock()
    mock_config.load_session.return_value = (None, None)
    mock_config_class.return_value = mock_config

    result = runner.invoke(cli, ["spice", "list", "https://example.com"])

    assert result.exit_code == 1
    assert "Not logged in" in result.output


@patch("atpcli.spice.create_client_with_session_refresh")
@patch("atpcli.spice.Config")
def test_list_no_notes(mock_config_class, mock_create_client, runner):
    """Test list with no matching notes."""
    # Setup mocks
    mock_client = MagicMock()
    mock_create_client.return_value = mock_client
    mock_client.me.did = "did:plc:test123"

    # Mock list_records response with no records
    mock_response = MagicMock()
    mock_response.records = []
    mock_client.com.atproto.repo.list_records.return_value = mock_response

    # Mock config
    mock_config = MagicMock()
    mock_config.load_session.return_value = ("test.bsky.social", "test_session")
    mock_config_class.return_value = mock_config

    # Run list
    result = runner.invoke(cli, ["spice", "list", "https://example.com"])

    # Verify
    assert result.exit_code == 0
    assert "No notes found" in result.output
    mock_create_client.assert_called_once_with(mock_config, "test.bsky.social", "test_session")


@patch("atpcli.spice.create_client_with_session_refresh")
@patch("atpcli.spice.Config")
def test_list_success(mock_config_class, mock_create_client, runner):
    """Test successful note listing."""
    # Setup mocks
    mock_client = MagicMock()
    mock_create_client.return_value = mock_client
    mock_client.me.did = "did:plc:test123"

    # Mock list_records response
    mock_record1 = MagicMock()
    mock_record1.uri = "at://did:plc:test123/tools.spice.note/abc123"
    mock_record1.value = {
        "url": "https://example.com",
        "text": "First note",
        "createdAt": "2026-02-21T10:00:00Z",
    }

    mock_record2 = MagicMock()
    mock_record2.uri = "at://did:plc:test123/tools.spice.note/xyz789"
    mock_record2.value = {
        "url": "https://different.com",
        "text": "Different URL",
        "createdAt": "2026-02-21T11:00:00Z",
    }

    mock_record3 = MagicMock()
    mock_record3.uri = "at://did:plc:test123/tools.spice.note/def456"
    mock_record3.value = {
        "url": "https://example.com",
        "text": "Second note",
        "createdAt": "2026-02-21T12:00:00Z",
    }

    mock_response = MagicMock()
    mock_response.records = [mock_record1, mock_record2, mock_record3]
    mock_response.cursor = None
    mock_client.com.atproto.repo.list_records.return_value = mock_response

    # Mock config
    mock_config = MagicMock()
    mock_config.load_session.return_value = ("test.bsky.social", "test_session")
    mock_config_class.return_value = mock_config

    # Run list
    result = runner.invoke(cli, ["spice", "list", "https://example.com"])

    # Verify - should only show records for https://example.com
    # After reverse, oldest appears first so latest appears at bottom when scrolling
    assert result.exit_code == 0
    assert "Found 2 note(s)" in result.output
    assert "First note" in result.output
    assert "Second note" in result.output
    assert "Different URL" not in result.output
    assert "at://did:plc:test123/tools.spice.note/abc123" in result.output
    assert "at://did:plc:test123/tools.spice.note/def456" in result.output
    # Verify the order - Second note (newer) appears before First note (older)
    # After reverse, oldest is first so latest appears at bottom when scrolling
    first_note_pos = result.output.index("First note")
    second_note_pos = result.output.index("Second note")
    assert second_note_pos < first_note_pos  # Second (newer) appears before First (older)
    mock_create_client.assert_called_once_with(mock_config, "test.bsky.social", "test_session")


@patch("atpcli.spice.create_client_with_session_refresh")
@patch("atpcli.spice.Config")
def test_list_with_pagination(mock_config_class, mock_create_client, runner):
    """Test list with pagination."""
    # Setup mocks
    mock_client = MagicMock()
    mock_create_client.return_value = mock_client
    mock_client.me.did = "did:plc:test123"

    # Mock first page
    mock_record1 = MagicMock()
    mock_record1.uri = "at://did:plc:test123/tools.spice.note/abc123"
    mock_record1.value = {
        "url": "https://example.com",
        "text": "First note",
        "createdAt": "2026-02-21T10:00:00Z",
    }

    mock_response1 = MagicMock()
    mock_response1.records = [mock_record1]
    mock_response1.cursor = "cursor_page_2"

    # Mock second page
    mock_record2 = MagicMock()
    mock_record2.uri = "at://did:plc:test123/tools.spice.note/def456"
    mock_record2.value = {
        "url": "https://example.com",
        "text": "Second note",
        "createdAt": "2026-02-21T12:00:00Z",
    }

    mock_response2 = MagicMock()
    mock_response2.records = [mock_record2]
    mock_response2.cursor = None

    # Mock list_records to return different responses for pagination
    mock_client.com.atproto.repo.list_records.side_effect = [mock_response1, mock_response2]

    # Mock config
    mock_config = MagicMock()
    mock_config.load_session.return_value = ("test.bsky.social", "test_session")
    mock_config_class.return_value = mock_config

    # Run list with --all flag
    result = runner.invoke(cli, ["spice", "list", "https://example.com", "--all"])

    # Verify
    assert result.exit_code == 0
    assert "Found 2 note(s)" in result.output
    assert "First note" in result.output
    assert "Second note" in result.output
    mock_create_client.assert_called_once_with(mock_config, "test.bsky.social", "test_session")
    # Should be called twice for pagination
    assert mock_client.com.atproto.repo.list_records.call_count == 2


@patch("atpcli.spice.create_client_with_session_refresh")
@patch("atpcli.spice.Config")
def test_delete_not_logged_in(mock_config_class, mock_create_client, runner):
    """Test delete when not logged in."""
    mock_config = MagicMock()
    mock_config.load_session.return_value = (None, None)
    mock_config_class.return_value = mock_config

    result = runner.invoke(cli, ["spice", "delete", "at://did:plc:test123/tools.spice.note/abc123"])

    assert result.exit_code == 1
    assert "Not logged in" in result.output


@patch("atpcli.spice.create_client_with_session_refresh")
@patch("atpcli.spice.Config")
def test_delete_invalid_uri_no_scheme(mock_config_class, mock_create_client, runner):
    """Test delete with invalid AT URI (no at:// scheme)."""
    mock_config = MagicMock()
    mock_config.load_session.return_value = ("test.bsky.social", "test_session")
    mock_config_class.return_value = mock_config

    result = runner.invoke(cli, ["spice", "delete", "did:plc:test123/tools.spice.note/abc123"])

    assert result.exit_code == 1
    assert "AT URI must start with 'at://'" in result.output


@patch("atpcli.spice.create_client_with_session_refresh")
@patch("atpcli.spice.Config")
def test_delete_invalid_uri_format(mock_config_class, mock_create_client, runner):
    """Test delete with invalid AT URI format."""
    mock_config = MagicMock()
    mock_config.load_session.return_value = ("test.bsky.social", "test_session")
    mock_config_class.return_value = mock_config

    result = runner.invoke(cli, ["spice", "delete", "at://invalid"])

    assert result.exit_code == 1
    assert "Invalid AT URI format" in result.output


@patch("atpcli.spice.create_client_with_session_refresh")
@patch("atpcli.spice.Config")
def test_delete_wrong_collection(mock_config_class, mock_create_client, runner):
    """Test delete with wrong collection type."""
    mock_config = MagicMock()
    mock_config.load_session.return_value = ("test.bsky.social", "test_session")
    mock_config_class.return_value = mock_config

    result = runner.invoke(cli, ["spice", "delete", "at://did:plc:test123/app.bsky.feed.post/abc123"])

    assert result.exit_code == 1
    assert "Invalid collection" in result.output


@patch("atpcli.spice.create_client_with_session_refresh")
@patch("atpcli.spice.Config")
def test_delete_success(mock_config_class, mock_create_client, runner):
    """Test successful note deletion."""
    # Setup mocks
    mock_client = MagicMock()
    mock_create_client.return_value = mock_client
    mock_client.me.did = "did:plc:test123"

    # Mock delete_record (it returns None on success)
    mock_client.com.atproto.repo.delete_record.return_value = None

    # Mock config
    mock_config = MagicMock()
    mock_config.load_session.return_value = ("test.bsky.social", "test_session")
    mock_config_class.return_value = mock_config

    # Run delete
    at_uri = "at://did:plc:test123/tools.spice.note/abc123xyz"
    result = runner.invoke(cli, ["spice", "delete", at_uri])

    # Verify
    assert result.exit_code == 0
    assert f"Deleted: {at_uri}" in result.output
    mock_create_client.assert_called_once_with(mock_config, "test.bsky.social", "test_session")

    # Verify delete_record was called with correct parameters
    call_args = mock_client.com.atproto.repo.delete_record.call_args
    assert call_args is not None
    delete_data = call_args[0][0]
    assert delete_data["repo"] == "did:plc:test123"
    assert delete_data["collection"] == "tools.spice.note"
    assert delete_data["rkey"] == "abc123xyz"
