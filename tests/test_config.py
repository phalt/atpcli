"""Tests for config module."""

import tempfile
from pathlib import Path

from atpcli.config import Config


def test_config_initialization():
    """Test that config initializes properly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = Config(config_dir=Path(tmpdir))
        assert config.config_dir.exists()
        assert config.config_file.parent == config.config_dir


def test_save_and_load_session():
    """Test saving and loading session."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = Config(config_dir=Path(tmpdir))

        # Save session
        config.save_session("test.bsky.social", "test_session_string")

        # Load session
        handle, session, pds_url = config.load_session()
        assert handle == "test.bsky.social"
        assert session == "test_session_string"
        assert pds_url == "https://bsky.social"  # Default PDS URL


def test_load_session_when_no_config():
    """Test loading session when no config exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = Config(config_dir=Path(tmpdir))
        handle, session, pds_url = config.load_session()
        assert handle is None
        assert session is None
        assert pds_url == "https://bsky.social"  # Default PDS URL


def test_clear_session():
    """Test clearing session."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = Config(config_dir=Path(tmpdir))

        # Save session
        config.save_session("test.bsky.social", "test_session_string")
        assert config.config_file.exists()

        # Clear session
        config.clear_session()
        assert not config.config_file.exists()


def test_load_config_empty():
    """Test loading empty config."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = Config(config_dir=Path(tmpdir))
        data = config.load_config()
        assert data == {}


def test_save_and_load_session_with_custom_pds():
    """Test saving and loading session with custom PDS URL."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = Config(config_dir=Path(tmpdir))

        # Save session with custom PDS
        config.save_session("test.custom.social", "test_session_string", "https://my-pds.com")

        # Load session
        handle, session, pds_url = config.load_session()
        assert handle == "test.custom.social"
        assert session == "test_session_string"
        assert pds_url == "https://my-pds.com"


def test_get_pds_url():
    """Test getting PDS URL."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = Config(config_dir=Path(tmpdir))

        # Default PDS URL when no config exists
        assert config.get_pds_url() == "https://bsky.social"

        # Save session with custom PDS
        config.save_session("test.custom.social", "test_session_string", "https://my-pds.com")

        # Get saved PDS URL
        assert config.get_pds_url() == "https://my-pds.com"
