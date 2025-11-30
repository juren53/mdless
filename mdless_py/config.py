"""Configuration management for mdless-py."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

from .utils import get_config_dir


DEFAULT_CONFIG = {
    "colors": {
        "heading1": "bright_blue",
        "heading2": "blue",
        "heading3": "cyan",
        "heading4": "cyan",
        "heading5": "cyan",
        "heading6": "cyan",
        "code": "yellow",
        "code_block": "yellow",
        "link": "bright_cyan",
        "emphasis": "italic",
        "strong": "bold",
        "list_marker": "green",
        "quote": "magenta",
        "table_border": "white",
        "footnote": "bright_black",
    },
    "rendering": {
        "enable_tables": True,
        "enable_footnotes": True,
        "max_width": 0,  # 0 means use terminal width
        "tab_width": 4,
        "line_numbers": False,
    },
    "images": {
        "display_tool": "auto",  # auto, imgcat, chafa, viu, timg, none
        "fetch_remote": False,
        "max_width": 80,
        "max_height": 24,
    },
    "navigation": {
        "scroll_offset": 3,  # Keep N lines visible when scrolling
        "search_case_sensitive": False,
        "wrap_search": True,
    },
}


# ANSI color codes mapping
ANSI_COLORS = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "bright_black": "\033[90m",
    "bright_red": "\033[91m",
    "bright_green": "\033[92m",
    "bright_yellow": "\033[93m",
    "bright_blue": "\033[94m",
    "bright_magenta": "\033[95m",
    "bright_cyan": "\033[96m",
    "bright_white": "\033[97m",
    "bold": "\033[1m",
    "italic": "\033[3m",
    "underline": "\033[4m",
    "reset": "\033[0m",
}


class Config:
    """Configuration manager."""
    
    def __init__(self, config_file: Optional[Path] = None):
        """Initialize configuration."""
        self.config_file = config_file
        self.data = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        config = DEFAULT_CONFIG.copy()
        
        if self.config_file and self.config_file.exists():
            config_path = self.config_file
        else:
            config_dir = get_config_dir()
            config_path = config_dir / "config.yaml"
        
        if config_path.exists() and YAML_AVAILABLE:
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                    if user_config:
                        config = self._merge_configs(config, user_config)
            except Exception as e:
                print(f"Warning: Could not load config from {config_path}: {e}")
        
        return config
    
    def _merge_configs(self, base: Dict, override: Dict) -> Dict:
        """Recursively merge override config into base config."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by dot-separated key (e.g., 'colors.heading1')."""
        parts = key.split('.')
        value = self.data
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
                if value is None:
                    return default
            else:
                return default
        return value
    
    def get_color(self, element: str) -> str:
        """Get ANSI color code for element."""
        color_name = self.get(f"colors.{element}", "white")
        return ANSI_COLORS.get(color_name, ANSI_COLORS["white"])
    
    def create_default_config(self):
        """Create default config file."""
        if not YAML_AVAILABLE:
            print("Warning: PyYAML not installed. Cannot create config file.")
            return
        
        config_dir = get_config_dir()
        config_dir.mkdir(parents=True, exist_ok=True)
        config_path = config_dir / "config.yaml"
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False, sort_keys=False)
        
        print(f"Created default config at: {config_path}")
