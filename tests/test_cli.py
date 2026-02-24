"""Tests for CLI commands."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from atpcli.cli import cli


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
    assert "atpcli" in result.output


def test_bsky_group(runner):
    """Test that bsky group runs."""
    result = runner.invoke(cli, ["bsky", "--help"])
    assert result.exit_code == 0
    assert "Commands for interacting with Bluesky" in result.output


def test_login_command_help(runner):
    """Test login command help."""
    result = runner.invoke(cli, ["login", "--help"])
    assert result.exit_code == 0
    assert "Login" in result.output


def test_timeline_command_help(runner):
    """Test timeline command help."""
    result = runner.invoke(cli, ["bsky", "timeline", "--help"])
    assert result.exit_code == 0
    assert "View your timeline" in result.output


@patch("atpcli.cli.Client")
@patch("atpcli.cli.Config")
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
    result = runner.invoke(cli, ["login", "--handle", "test.bsky.social", "--password", "testpass"])

    # Verify
    assert result.exit_code == 0
    assert "Successfully logged in" in result.output
    mock_client_class.assert_called_once_with(base_url="https://bsky.social")
    mock_client.login.assert_called_once_with("test.bsky.social", "testpass")
    mock_config.save_session.assert_called_once_with("test.bsky.social", "test_session", "https://bsky.social")


@patch("atpcli.cli.Client")
@patch("atpcli.cli.Config")
def test_login_custom_pds(mock_config_class, mock_client_class, runner, temp_config):
    """Test login with custom PDS URL."""
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

    # Run login with custom PDS
    result = runner.invoke(
        cli, ["login", "https://my-pds.com", "--handle", "test.custom.social", "--password", "testpass"]
    )

    # Verify custom PDS URL was used
    assert result.exit_code == 0
    assert "Successfully logged in" in result.output
    mock_client_class.assert_called_once_with(base_url="https://my-pds.com")
    mock_config.save_session.assert_called_once_with("test.custom.social", "test_session", "https://my-pds.com")


@patch("atpcli.cli.create_client_with_session_refresh")
@patch("atpcli.cli.Config")
def test_timeline_not_logged_in(mock_config_class, mock_create_client, runner):
    """Test timeline when not logged in."""
    mock_config = MagicMock()
    mock_config.load_session.return_value = (None, None, "https://bsky.social")
    mock_config_class.return_value = mock_config

    result = runner.invoke(cli, ["bsky", "timeline"])

    assert result.exit_code == 1
    assert "Not logged in" in result.output


@patch("atpcli.cli.create_client_with_session_refresh")
@patch("atpcli.cli.Config")
def test_timeline_success(mock_config_class, mock_create_client, runner):
    """Test successful timeline fetch."""
    # Setup mocks
    mock_client = MagicMock()
    mock_create_client.return_value = mock_client

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
    mock_config.load_session.return_value = ("test.bsky.social", "test_session", "https://bsky.social")
    mock_config_class.return_value = mock_config

    # Run timeline
    result = runner.invoke(cli, ["bsky", "timeline", "--limit", "10"])

    # Verify
    assert result.exit_code == 0
    assert "Loading timeline for test.bsky.social" in result.output
    assert "Test Author" in result.output
    assert "Test post" in result.output
    assert "Showing 1 post" in result.output
    mock_create_client.assert_called_once_with(mock_config, "test.bsky.social", "test_session", "https://bsky.social")
    mock_client.get_timeline.assert_called_once_with(limit=10, cursor=None)


@patch("atpcli.cli.create_client_with_session_refresh")
@patch("atpcli.cli.Config")
def test_timeline_with_pagination(mock_config_class, mock_create_client, runner):
    """Test timeline with pagination."""
    # Setup mocks
    mock_client = MagicMock()
    mock_create_client.return_value = mock_client

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
    mock_config.load_session.return_value = ("test.bsky.social", "test_session", "https://bsky.social")
    mock_config_class.return_value = mock_config

    # Run timeline with page 2
    result = runner.invoke(cli, ["bsky", "timeline", "--limit", "5", "--p", "2"])

    # Verify
    assert result.exit_code == 0
    assert "Loading timeline for test.bsky.social" in result.output
    assert "Test post on page 2" in result.output
    assert "page 2" in result.output
    assert "--p 3" in result.output  # Should show next page hint
    mock_create_client.assert_called_once_with(mock_config, "test.bsky.social", "test_session", "https://bsky.social")
    # Should be called twice: once to skip page 1, once to get page 2
    assert mock_client.get_timeline.call_count == 2


def test_post_command_help(runner):
    """Test post command help."""
    result = runner.invoke(cli, ["bsky", "post", "--help"])
    assert result.exit_code == 0
    assert "Post a message to Bluesky" in result.output


@patch("atpcli.cli.create_client_with_session_refresh")
@patch("atpcli.cli.Config")
def test_post_not_logged_in(mock_config_class, mock_create_client, runner):
    """Test post when not logged in."""
    mock_config = MagicMock()
    mock_config.load_session.return_value = (None, None, "https://bsky.social")
    mock_config_class.return_value = mock_config

    result = runner.invoke(cli, ["bsky", "post", "--message", "Test post"])

    assert result.exit_code == 1
    assert "Not logged in" in result.output


@patch("atpcli.cli.create_client_with_session_refresh")
@patch("atpcli.cli.Config")
def test_post_success(mock_config_class, mock_create_client, runner):
    """Test successful post."""
    # Setup mocks
    mock_client = MagicMock()
    mock_create_client.return_value = mock_client

    # Mock post response
    mock_response = MagicMock()
    mock_response.uri = "at://did:plc:test123/app.bsky.feed.post/abc123xyz"
    mock_client.send_post.return_value = mock_response

    # Mock config
    mock_config = MagicMock()
    mock_config.load_session.return_value = ("test.bsky.social", "test_session", "https://bsky.social")
    mock_config_class.return_value = mock_config

    # Run post
    result = runner.invoke(cli, ["bsky", "post", "--message", "Hello Bluesky!"])

    # Verify
    assert result.exit_code == 0
    assert "Post created successfully" in result.output
    assert "https://bsky.app/profile/test.bsky.social/post/abc123xyz" in result.output
    mock_create_client.assert_called_once_with(mock_config, "test.bsky.social", "test_session", "https://bsky.social")
    mock_client.send_post.assert_called_once_with(text="Hello Bluesky!")


@patch("atpcli.cli.create_client_with_session_refresh")
@patch("atpcli.cli.Config")
def test_post_with_short_option(mock_config_class, mock_create_client, runner):
    """Test post with -m short option."""
    # Setup mocks
    mock_client = MagicMock()
    mock_create_client.return_value = mock_client

    # Mock post response
    mock_response = MagicMock()
    mock_response.uri = "at://did:plc:test123/app.bsky.feed.post/abc123xyz"
    mock_client.send_post.return_value = mock_response

    # Mock config
    mock_config = MagicMock()
    mock_config.load_session.return_value = ("test.bsky.social", "test_session", "https://bsky.social")
    mock_config_class.return_value = mock_config

    # Run post with -m short option
    result = runner.invoke(cli, ["bsky", "post", "-m", "Quick post!"])

    # Verify
    assert result.exit_code == 0
    assert "Post created successfully" in result.output
    mock_client.send_post.assert_called_once_with(text="Quick post!")


@patch("atpcli.cli.create_client_with_session_refresh")
@patch("atpcli.cli.Config")
def test_post_failure(mock_config_class, mock_create_client, runner):
    """Test post failure."""
    # Setup mocks
    mock_client = MagicMock()
    mock_create_client.return_value = mock_client
    mock_client.send_post.side_effect = Exception("Network error")

    # Mock config
    mock_config = MagicMock()
    mock_config.load_session.return_value = ("test.bsky.social", "test_session", "https://bsky.social")
    mock_config_class.return_value = mock_config

    # Run post
    result = runner.invoke(cli, ["bsky", "post", "--message", "Hello Bluesky!"])

    # Verify
    assert result.exit_code == 1
    assert "Failed to post" in result.output
    assert "Network error" in result.output


def test_feeds_command_help(runner):
    """Test feeds command help."""
    result = runner.invoke(cli, ["bsky", "feeds", "--help"])
    assert result.exit_code == 0
    assert "List your saved feeds" in result.output


def test_feed_command_help(runner):
    """Test feed command help."""
    result = runner.invoke(cli, ["bsky", "feed", "--help"])
    assert result.exit_code == 0
    assert "View posts from a specific feed" in result.output


@patch("atpcli.cli.create_client_with_session_refresh")
@patch("atpcli.cli.Config")
def test_feeds_not_logged_in(mock_config_class, mock_create_client, runner):
    """Test feeds when not logged in."""
    mock_config = MagicMock()
    mock_config.load_session.return_value = (None, None, "https://bsky.social")
    mock_config_class.return_value = mock_config

    result = runner.invoke(cli, ["bsky", "feeds"])

    assert result.exit_code == 1
    assert "Not logged in" in result.output


@patch("atpcli.cli.create_client_with_session_refresh")
@patch("atpcli.cli.Config")
def test_feeds_success_table_format(mock_config_class, mock_create_client, runner):
    """Test successful feeds fetch with table format."""
    # Setup mocks
    mock_client = MagicMock()
    mock_create_client.return_value = mock_client

    # Mock saved feeds preference
    mock_pref = MagicMock()
    mock_pref.py_type = "app.bsky.actor.defs#savedFeedsPref"
    mock_pref.saved = ["at://did:plc:test/app.bsky.feed.generator/discover"]

    mock_preferences = MagicMock()
    mock_preferences.preferences = [mock_pref]
    mock_client.app.bsky.actor.get_preferences.return_value = mock_preferences

    # Mock feed generator info
    mock_feed_view = MagicMock()
    mock_feed_view.display_name = "Discover Feed"
    mock_feed_view.description = "Discover new content"

    mock_feed_info = MagicMock()
    mock_feed_info.view = mock_feed_view
    mock_client.app.bsky.feed.get_feed_generator.return_value = mock_feed_info

    # Mock config
    mock_config = MagicMock()
    mock_config.load_session.return_value = ("test.bsky.social", "test_session", "https://bsky.social")
    mock_config_class.return_value = mock_config

    # Run feeds
    result = runner.invoke(cli, ["bsky", "feeds"])

    # Verify
    assert result.exit_code == 0
    assert "Loading saved feeds for test.bsky.social" in result.output
    assert "Discover Feed" in result.output
    assert "Saved Feeds (1)" in result.output
    mock_create_client.assert_called_once_with(mock_config, "test.bsky.social", "test_session", "https://bsky.social")
    mock_client.app.bsky.actor.get_preferences.assert_called_once()


@patch("atpcli.cli.create_client_with_session_refresh")
@patch("atpcli.cli.Config")
def test_feeds_success_uri_format(mock_config_class, mock_create_client, runner):
    """Test successful feeds fetch with URI format."""
    # Setup mocks
    mock_client = MagicMock()
    mock_create_client.return_value = mock_client

    # Mock saved feeds preference
    mock_pref = MagicMock()
    mock_pref.py_type = "app.bsky.actor.defs#savedFeedsPref"
    mock_pref.saved = [
        "at://did:plc:test/app.bsky.feed.generator/discover",
        "at://did:plc:test/app.bsky.feed.generator/popular",
    ]

    mock_preferences = MagicMock()
    mock_preferences.preferences = [mock_pref]
    mock_client.app.bsky.actor.get_preferences.return_value = mock_preferences

    # Mock config
    mock_config = MagicMock()
    mock_config.load_session.return_value = ("test.bsky.social", "test_session", "https://bsky.social")
    mock_config_class.return_value = mock_config

    # Run feeds with URI format
    result = runner.invoke(cli, ["bsky", "feeds", "--format", "uri"])

    # Verify
    assert result.exit_code == 0
    assert "at://did:plc:test/app.bsky.feed.generator/discover" in result.output
    assert "at://did:plc:test/app.bsky.feed.generator/popular" in result.output
    # Should not call get_feed_generator for URI format
    mock_client.app.bsky.feed.get_feed_generator.assert_not_called()


@patch("atpcli.cli.create_client_with_session_refresh")
@patch("atpcli.cli.Config")
def test_feeds_empty(mock_config_class, mock_create_client, runner):
    """Test feeds when no saved feeds exist."""
    # Setup mocks
    mock_client = MagicMock()
    mock_create_client.return_value = mock_client

    # Mock empty preferences
    mock_preferences = MagicMock()
    mock_preferences.preferences = []
    mock_client.app.bsky.actor.get_preferences.return_value = mock_preferences

    # Mock config
    mock_config = MagicMock()
    mock_config.load_session.return_value = ("test.bsky.social", "test_session", "https://bsky.social")
    mock_config_class.return_value = mock_config

    # Run feeds
    result = runner.invoke(cli, ["bsky", "feeds"])

    # Verify
    assert result.exit_code == 0
    assert "No saved feeds found" in result.output


@patch("atpcli.cli.create_client_with_session_refresh")
@patch("atpcli.cli.Config")
def test_feed_not_logged_in(mock_config_class, mock_create_client, runner):
    """Test feed when not logged in."""
    mock_config = MagicMock()
    mock_config.load_session.return_value = (None, None, "https://bsky.social")
    mock_config_class.return_value = mock_config

    result = runner.invoke(cli, ["bsky", "feed", "at://did:plc:test/app.bsky.feed.generator/discover"])

    assert result.exit_code == 1
    assert "Not logged in" in result.output


@patch("atpcli.cli.create_client_with_session_refresh")
@patch("atpcli.cli.Config")
def test_feed_success(mock_config_class, mock_create_client, runner):
    """Test successful feed fetch."""
    # Setup mocks
    mock_client = MagicMock()
    mock_create_client.return_value = mock_client

    # Mock feed response
    mock_post = MagicMock()
    mock_post.author.display_name = "Test Author"
    mock_post.author.handle = "test.bsky.social"
    mock_post.record.text = "Test post from feed"
    mock_post.like_count = 7
    mock_post.uri = "at://did:plc:test123/app.bsky.feed.post/xyz123"

    mock_feed_view = MagicMock()
    mock_feed_view.post = mock_post

    mock_feed_response = MagicMock()
    mock_feed_response.feed = [mock_feed_view]
    mock_feed_response.cursor = None
    mock_client.app.bsky.feed.get_feed.return_value = mock_feed_response

    # Mock config
    mock_config = MagicMock()
    mock_config.load_session.return_value = ("test.bsky.social", "test_session", "https://bsky.social")
    mock_config_class.return_value = mock_config

    # Run feed
    feed_uri = "at://did:plc:test/app.bsky.feed.generator/discover"
    result = runner.invoke(cli, ["bsky", "feed", feed_uri, "--limit", "10"])

    # Verify
    assert result.exit_code == 0
    assert f"Loading feed {feed_uri}" in result.output
    assert "Test Author" in result.output
    assert "Test post from feed" in result.output
    assert "Showing 1 post" in result.output
    mock_create_client.assert_called_once_with(mock_config, "test.bsky.social", "test_session", "https://bsky.social")
    mock_client.app.bsky.feed.get_feed.assert_called_once()


@patch("atpcli.cli.create_client_with_session_refresh")
@patch("atpcli.cli.Config")
def test_feed_with_pagination(mock_config_class, mock_create_client, runner):
    """Test feed with pagination."""
    # Setup mocks
    mock_client = MagicMock()
    mock_create_client.return_value = mock_client

    # Mock feed response for page 1
    mock_feed_page1 = MagicMock()
    mock_feed_page1.feed = []
    mock_feed_page1.cursor = "cursor_page_2"

    # Mock feed response for page 2
    mock_post = MagicMock()
    mock_post.author.display_name = "Test Author"
    mock_post.author.handle = "test.bsky.social"
    mock_post.record.text = "Test post on page 2"
    mock_post.like_count = 5
    mock_post.uri = "at://did:plc:test123/app.bsky.feed.post/abc789"

    mock_feed_view = MagicMock()
    mock_feed_view.post = mock_post

    mock_feed_page2 = MagicMock()
    mock_feed_page2.feed = [mock_feed_view]
    mock_feed_page2.cursor = "cursor_page_3"

    # Mock get_feed to return different responses
    mock_client.app.bsky.feed.get_feed.side_effect = [mock_feed_page1, mock_feed_page2]

    # Mock config
    mock_config = MagicMock()
    mock_config.load_session.return_value = ("test.bsky.social", "test_session", "https://bsky.social")
    mock_config_class.return_value = mock_config

    # Run feed with page 2
    feed_uri = "at://did:plc:test/app.bsky.feed.generator/discover"
    result = runner.invoke(cli, ["bsky", "feed", feed_uri, "--limit", "5", "--p", "2"])

    # Verify
    assert result.exit_code == 0
    assert "Test post on page 2" in result.output
    assert "page 2" in result.output
    assert "--p 3" in result.output  # Should show next page hint
    mock_create_client.assert_called_once_with(mock_config, "test.bsky.social", "test_session", "https://bsky.social")
    # Should be called twice: once to skip page 1, once to get page 2
    assert mock_client.app.bsky.feed.get_feed.call_count == 2


@patch("atpcli.cli.create_client_with_session_refresh")
@patch("atpcli.cli.Config")
def test_feed_empty(mock_config_class, mock_create_client, runner):
    """Test feed with no posts."""
    # Setup mocks
    mock_client = MagicMock()
    mock_create_client.return_value = mock_client

    # Mock empty feed response
    mock_feed_response = MagicMock()
    mock_feed_response.feed = []
    mock_feed_response.cursor = None
    mock_client.app.bsky.feed.get_feed.return_value = mock_feed_response

    # Mock config
    mock_config = MagicMock()
    mock_config.load_session.return_value = ("test.bsky.social", "test_session", "https://bsky.social")
    mock_config_class.return_value = mock_config

    # Run feed
    feed_uri = "at://did:plc:test/app.bsky.feed.generator/discover"
    result = runner.invoke(cli, ["bsky", "feed", feed_uri])

    # Verify
    assert result.exit_code == 0
    assert "This feed has no posts" in result.output
