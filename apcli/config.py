"""Configuration management for apcli."""

import json
from pathlib import Path
from typing import Optional


class Config:
    """Manage apcli configuration and session state."""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize config with optional custom directory."""
        if config_dir is None:
            config_dir = Path.home() / ".config" / "apcli"
        self.config_dir = config_dir
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def save_session(self, handle: str, session_string: str) -> None:
        """Save session information to config file."""
        config_data = self.load_config()
        config_data["handle"] = handle
        config_data["session"] = session_string
        with open(self.config_file, "w") as f:
            json.dump(config_data, f, indent=2)

    def load_session(self) -> tuple[Optional[str], Optional[str]]:
        """Load session information from config file."""
        config_data = self.load_config()
        return config_data.get("handle"), config_data.get("session")

    def load_config(self) -> dict:
        """Load the entire config file."""
        if not self.config_file.exists():
            return {}
        with open(self.config_file, "r") as f:
            return json.load(f)

    def clear_session(self) -> None:
        """Clear the saved session."""
        if self.config_file.exists():
            self.config_file.unlink()
