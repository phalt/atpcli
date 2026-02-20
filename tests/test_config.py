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
        handle, session = config.load_session()
        assert handle == "test.bsky.social"
        assert session == "test_session_string"


def test_load_session_when_no_config():
    """Test loading session when no config exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = Config(config_dir=Path(tmpdir))
        handle, session = config.load_session()
        assert handle is None
        assert session is None


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
