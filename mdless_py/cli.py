"""Command-line interface for mdless-py."""

import argparse
import sys
from pathlib import Path

# Initialize colorama for Windows ANSI support
try:
    import colorama
    colorama.just_fix_windows_console()
except ImportError:
    pass

from .config import Config
from .renderer import MarkdownRenderer
from .document import Document
from .navigator import start_navigator


def main():
    """Main entry point for mdless-py CLI."""
    parser = argparse.ArgumentParser(
        description="mdless-py: A cross-platform CLI Markdown viewer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mdless-py README.md              View a markdown file
  mdless-py -c config.yaml doc.md  Use custom config file
  mdless-py --create-config        Create default config file

Keyboard shortcuts:
  h or ?  - Show help
  q       - Quit
  /       - Search
  v       - Visual selection mode
  y       - Copy to clipboard
        """
    )
    
    parser.add_argument(
        'file',
        type=str,
        nargs='?',
        help='Markdown file to view'
    )
    
    parser.add_argument(
        '-c', '--config',
        type=str,
        help='Path to config file'
    )
    
    parser.add_argument(
        '--create-config',
        action='store_true',
        help='Create default config file and exit'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='store_true',
        help='Show version and exit'
    )
    
    args = parser.parse_args()
    
    # Handle version
    if args.version:
        from . import __version__
        print(f"mdless-py version {__version__}")
        return 0
    
    # Handle config creation
    if args.create_config:
        config = Config()
        config.create_default_config()
        return 0
    
    # Require file argument
    if not args.file:
        parser.print_help()
        return 1
    
    # Check if file exists
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        return 1
    
    if not file_path.is_file():
        print(f"Error: Not a file: {file_path}", file=sys.stderr)
        return 1
    
    try:
        # Load configuration
        config_file = Path(args.config) if args.config else None
        config = Config(config_file)
        
        # Render markdown
        renderer = MarkdownRenderer(config)
        rendered_lines = renderer.render_file(file_path)
        
        # Create document
        document = Document(file_path, rendered_lines)
        
        # Start navigator
        start_navigator(document, config)
        
        return 0
        
    except KeyboardInterrupt:
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
