"""Utility functions for mdless-py."""

import os
import sys
import shutil
from pathlib import Path
from typing import Optional


def get_terminal_size():
    """Get terminal size with fallback."""
    try:
        size = shutil.get_terminal_size()
        return size.columns, size.lines
    except Exception:
        return 80, 24


def get_config_dir() -> Path:
    """Get platform-appropriate config directory."""
    if sys.platform == "win32":
        config_home = os.environ.get("APPDATA")
        if config_home:
            return Path(config_home) / "mdless-py"
    
    config_home = os.environ.get("XDG_CONFIG_HOME")
    if config_home:
        return Path(config_home) / "mdless-py"
    
    return Path.home() / ".config" / "mdless-py"


def which(command: str) -> Optional[str]:
    """Find command in PATH, cross-platform."""
    return shutil.which(command)


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to max_length with suffix."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text."""
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)
