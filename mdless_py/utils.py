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


def wrap_text_with_ansi(text: str, width: int) -> str:
    """Wrap text to specified width while preserving ANSI codes.
    
    Args:
        text: Text with ANSI escape codes
        width: Maximum width for wrapping
    
    Returns:
        Wrapped text with ANSI codes preserved
    """
    if width <= 0:
        return text
    
    import re
    
    # Pattern to match ANSI escape sequences
    ansi_pattern = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
    # Split text into tokens (ANSI codes and regular text)
    tokens = []
    pos = 0
    for match in ansi_pattern.finditer(text):
        if match.start() > pos:
            tokens.append(('text', text[pos:match.start()]))
        tokens.append(('ansi', match.group()))
        pos = match.end()
    if pos < len(text):
        tokens.append(('text', text[pos:]))
    
    # Track current formatting state
    current_format = []
    lines = []
    current_line = ""
    current_width = 0
    
    # Process tokens
    i = 0
    while i < len(tokens):
        token_type, token_value = tokens[i]
        
        if token_type == 'ansi':
            # Add ANSI code to current line
            current_line += token_value
            # Track format changes
            if '\x1B[0m' in token_value:  # Reset
                current_format = []
            else:
                current_format.append(token_value)
            i += 1
        else:
            # Process text - split by words
            words = token_value.split(' ')
            
            for j, word in enumerate(words):
                if not word:
                    # Handle multiple spaces
                    if j > 0:  # Not the first word, add space
                        if current_width + 1 <= width:
                            current_line += ' '
                            current_width += 1
                        else:
                            # Start new line
                            lines.append(current_line)
                            current_line = ''.join(current_format)
                            current_width = 0
                    continue
                
                word_len = len(word)
                
                # Check if we need to add a space before this word
                if current_width > 0 and j > 0:
                    if current_width + 1 + word_len <= width:
                        current_line += ' ' + word
                        current_width += 1 + word_len
                    else:
                        # Start new line with current formatting
                        lines.append(current_line)
                        current_line = ''.join(current_format) + word
                        current_width = word_len
                else:
                    # First word on line
                    if current_width + word_len <= width:
                        current_line += word
                        current_width += word_len
                    else:
                        # Word is too long, break it
                        if current_width == 0:
                            # Start of line, just truncate
                            current_line += word[:width]
                            current_width = width
                        else:
                            # Start new line
                            lines.append(current_line)
                            current_line = ''.join(current_format) + word
                            current_width = word_len
            
            i += 1
    
    # Add the last line if any
    if current_line.strip() or current_width > 0:
        lines.append(current_line)
    
    return '\n'.join(lines)


def get_version_info() -> str:
    """Get version and last commit date.
    
    Returns:
        String like "v0.1.2 (2025-11-30)" or just "v0.1.2" if git not available
    """
    from . import __version__
    
    # Try to get git commit date
    try:
        import subprocess
        from pathlib import Path
        
        # Find the git repo root (look for .git directory)
        current_dir = Path(__file__).parent
        while current_dir != current_dir.parent:
            if (current_dir / '.git').exists():
                result = subprocess.run(
                    ['git', 'log', '-1', '--format=%cd', '--date=short'],
                    cwd=current_dir,
                    capture_output=True,
                    text=True,
                    timeout=1
                )
                if result.returncode == 0:
                    date = result.stdout.strip()
                    return f"v{__version__} ({date})"
                break
            current_dir = current_dir.parent
    except Exception:
        pass
    
    return f"v{__version__}"
