"""Tests for CLI commands."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from apcli.cli import cli, login, timeline


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


def test_login_command_help(runner):
    """Test login command help."""
    result = runner.invoke(login, ["--help"])
    assert result.exit_code == 0
    assert "Login" in result.output


def test_timeline_command_help(runner):
    """Test timeline command help."""
    result = runner.invoke(timeline, ["--help"])
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
    result = runner.invoke(login, ["--handle", "test.bsky.social", "--password", "testpass"])

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

    result = runner.invoke(timeline)

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

    mock_feed_view = MagicMock()
    mock_feed_view.post = mock_post

    mock_timeline = MagicMock()
    mock_timeline.feed = [mock_feed_view]
    mock_client.get_timeline.return_value = mock_timeline

    # Mock config
    mock_config = MagicMock()
    mock_config.load_session.return_value = ("test.bsky.social", "test_session")
    mock_config_class.return_value = mock_config

    # Run timeline
    result = runner.invoke(timeline, ["--limit", "10"])

    # Verify
    assert result.exit_code == 0
    assert "Timeline for test.bsky.social" in result.output
    mock_client.login.assert_called_once_with(session_string="test_session")
    mock_client.get_timeline.assert_called_once_with(limit=10)
