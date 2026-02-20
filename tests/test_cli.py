"""Tests for CLI commands."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from apcli.cli import cli


@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()


@pytest.fixture
def temp_config():
    """Create a temporary config directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_cli_group(runner):
    """Test that CLI group runs."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "apcli" in result.output


def test_bsky_group(runner):
    """Test that bsky group runs."""
    result = runner.invoke(cli, ["bsky", "--help"])
    assert result.exit_code == 0
    assert "Commands for interacting with Bluesky" in result.output


def test_login_command_help(runner):
    """Test login command help."""
    result = runner.invoke(cli, ["bsky", "login", "--help"])
    assert result.exit_code == 0
    assert "Login" in result.output


def test_timeline_command_help(runner):
    """Test timeline command help."""
    result = runner.invoke(cli, ["bsky", "timeline", "--help"])
    assert result.exit_code == 0
    assert "View your timeline" in result.output


@patch("apcli.cli.Client")
@patch("apcli.cli.Config")
def test_login_success(mock_config_class, mock_client_class, runner, temp_config):
    """Test successful login."""
    # Setup mocks
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    mock_profile = MagicMock()
    mock_profile.display_name = "Test User"
    mock_client.login.return_value = mock_profile
    mock_client.export_session_string.return_value = "test_session"

    mock_config = MagicMock()
    mock_config.config_file = temp_config / "config.json"
    mock_config_class.return_value = mock_config

    # Run login
    result = runner.invoke(cli, ["bsky", "login", "--handle", "test.bsky.social", "--password", "testpass"])

    # Verify
    assert result.exit_code == 0
    assert "Successfully logged in" in result.output
    mock_client.login.assert_called_once_with("test.bsky.social", "testpass")
    mock_config.save_session.assert_called_once_with("test.bsky.social", "test_session")


@patch("apcli.cli.Client")
@patch("apcli.cli.Config")
def test_timeline_not_logged_in(mock_config_class, mock_client_class, runner):
    """Test timeline when not logged in."""
    mock_config = MagicMock()
    mock_config.load_session.return_value = (None, None)
    mock_config_class.return_value = mock_config

    result = runner.invoke(cli, ["bsky", "timeline"])

    assert result.exit_code == 1
    assert "Not logged in" in result.output


@patch("apcli.cli.Client")
@patch("apcli.cli.Config")
def test_timeline_success(mock_config_class, mock_client_class, runner):
    """Test successful timeline fetch."""
    # Setup mocks
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    # Mock timeline response
    mock_post = MagicMock()
    mock_post.author.display_name = "Test Author"
    mock_post.author.handle = "test.bsky.social"
    mock_post.record.text = "Test post"
    mock_post.like_count = 5
    mock_post.uri = "at://did:plc:test123/app.bsky.feed.post/abc123"

    mock_feed_view = MagicMock()
    mock_feed_view.post = mock_post

    mock_timeline = MagicMock()
    mock_timeline.feed = [mock_feed_view]
    mock_timeline.cursor = None
    mock_client.get_timeline.return_value = mock_timeline

    # Mock config
    mock_config = MagicMock()
    mock_config.load_session.return_value = ("test.bsky.social", "test_session")
    mock_config_class.return_value = mock_config

    # Run timeline
    result = runner.invoke(cli, ["bsky", "timeline", "--limit", "10"])

    # Verify
    assert result.exit_code == 0
    assert "Loading timeline for test.bsky.social" in result.output
    assert "Test Author" in result.output
    assert "Test post" in result.output
    assert "Showing 1 posts" in result.output
    mock_client.login.assert_called_once_with(session_string="test_session")
    mock_client.get_timeline.assert_called_once_with(limit=10, cursor=None)


@patch("apcli.cli.Client")
@patch("apcli.cli.Config")
def test_timeline_with_pagination(mock_config_class, mock_client_class, runner):
    """Test timeline with pagination."""
    # Setup mocks
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    # Mock timeline response for page 1
    mock_timeline_page1 = MagicMock()
    mock_timeline_page1.feed = []
    mock_timeline_page1.cursor = "cursor_page_2"

    # Mock timeline response for page 2
    mock_post = MagicMock()
    mock_post.author.display_name = "Test Author"
    mock_post.author.handle = "test.bsky.social"
    mock_post.record.text = "Test post on page 2"
    mock_post.like_count = 3
    mock_post.uri = "at://did:plc:test123/app.bsky.feed.post/xyz789"

    mock_feed_view = MagicMock()
    mock_feed_view.post = mock_post

    mock_timeline_page2 = MagicMock()
    mock_timeline_page2.feed = [mock_feed_view]
    mock_timeline_page2.cursor = "cursor_page_3"

    # Mock get_timeline to return different responses
    mock_client.get_timeline.side_effect = [mock_timeline_page1, mock_timeline_page2]

    # Mock config
    mock_config = MagicMock()
    mock_config.load_session.return_value = ("test.bsky.social", "test_session")
    mock_config_class.return_value = mock_config

    # Run timeline with page 2
    result = runner.invoke(cli, ["bsky", "timeline", "--limit", "5", "--p", "2"])

    # Verify
    assert result.exit_code == 0
    assert "Loading timeline for test.bsky.social" in result.output
    assert "Test post on page 2" in result.output
    assert "page 2" in result.output
    assert "--p 3" in result.output  # Should show next page hint
    mock_client.login.assert_called_once_with(session_string="test_session")
    # Should be called twice: once to skip page 1, once to get page 2
    assert mock_client.get_timeline.call_count == 2
