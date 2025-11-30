# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

**mdless-py** is a cross-platform CLI Markdown viewer written in Python. It provides a less-like terminal interface for viewing Markdown files with advanced features including syntax highlighting, visual selection, clipboard support, and table of contents navigation.

The project is in **production-ready** state with comprehensive test coverage on Windows 11, Linux, and macOS.

## Development Commands

### Installation
```bash
# Install in editable mode (development)
pip install -e .

# Install with all optional dependencies
pip install -e ".[all]"
```

### Running the Application
```bash
# Run as module
python -m mdless_py README.md

# Run specific entry point
mdless-py README.md

# With custom config
python -m mdless_py -c config.yaml document.md

# Create default config
python -m mdless_py --create-config
```

### Testing
```bash
# Run all tests with pytest
python -m pytest tests/

# Run tests manually (without pytest)
python tests/test_basic.py

# Test rendering directly
python test_render.py

# Test specific markdown files in the TUI
python -m mdless_py test_code_blocks.md
python -m mdless_py border_test.md
python -m mdless_py search_demo.md
```

### Linting and Type Checking
Note: This project does not currently have configured linting or type checking. If adding these:
- Use `black` for code formatting
- Use `mypy` for type checking
- Use `pylint` or `flake8` for linting

## Architecture

### Core Component Flow
```
CLI (cli.py) 
  → Config (config.py) - Loads YAML configuration
  → Renderer (renderer.py) - Mistune AST → ANSI text
    → Highlighter (highlighter.py) - Pygments integration
    → ImageDisplay (images.py) - Image tool detection
  → Document (document.py) - Parsed structure + TOC
  → Navigator (navigator.py) - Curses TUI + clipboard
```

### Key Design Patterns

**Renderer Architecture:**
- Custom `mistune.HTMLRenderer` subclass (`ANSIRenderer`) converts Markdown AST to ANSI-colored text
- ANSI codes are stripped before display in curses (curses doesn't support ANSI)
- Clean text is preserved for clipboard operations

**Document Model:**
- Parses ATX-style headings (`# Heading`) from rendered output
- Builds hierarchical table of contents with line numbers
- Supports section navigation and headline jumping

**Navigator (TUI):**
- Built on Python's `curses` library (with `windows-curses` on Windows)
- Implements less-like keybindings (j/k, d/u, f/b, g/G, etc.)
- Visual selection mode tracks start/end lines for clipboard copy
- Search uses compiled regex patterns with match highlighting

### Critical Implementation Details

1. **ANSI Code Handling:**
   - Renderer generates ANSI codes for colors
   - Navigator strips ANSI before curses display using `strip_ansi()`
   - Code block borders must measure visible width (stripped) for alignment

2. **Code Block Borders:**
   - Borders use box-drawing characters (┌─┐│└┘)
   - Width calculation strips ANSI codes to measure visible content
   - Padding is based on clean text length, not total string length with codes

3. **Clipboard Integration:**
   - Uses `pyperclip` for cross-platform clipboard access
   - Visual mode selects line ranges
   - Yank operation copies ANSI-stripped text

4. **Platform Differences:**
   - Windows: Requires `windows-curses` and `colorama`
   - Linux/macOS: Native curses, may need `xclip`/`xsel` for clipboard
   - Config paths differ by platform (handled in `config.py`)

## File Structure

```
mdless_py/
├── __init__.py          # Package version info
├── __main__.py          # Module entry point (python -m mdless_py)
├── cli.py               # CLI argument parsing + colorama init
├── config.py            # YAML config management + defaults
├── renderer.py          # Mistune → ANSI renderer (ANSIRenderer)
├── highlighter.py       # Pygments integration (optional)
├── images.py            # Image tool detection (imgcat/chafa/viu/timg)
├── document.py          # Document model + headline parsing + TOC
├── navigator.py         # Curses TUI + keybindings + clipboard
└── utils.py             # Helper functions (strip_ansi, etc.)

tests/
└── test_basic.py        # Integration tests for core functionality
```

## Dependencies

**Required:**
- `mistune>=3.0.0` - Markdown parsing (v3.x with AST renderer API)
- `PyYAML>=6.0` - Configuration file support
- `pyperclip>=1.8.0` - Clipboard integration
- `windows-curses>=2.3.0` - Windows TUI support (Windows only)
- `colorama>=0.4.6` - ANSI support (Windows only)

**Optional:**
- `Pygments>=2.14.0` - Syntax highlighting for code blocks
- `requests>=2.28.0` - Remote image fetching

## Configuration

Config file locations:
- Windows: `%APPDATA%\mdless-py\config.yaml`
- Linux/macOS: `~/.config/mdless-py/config.yaml`

Configuration sections:
- `colors` - ANSI color names for each element type
- `rendering` - Markdown rendering options (tables, footnotes, width)
- `images` - Image display preferences (tool, fetch remote, max width)
- `navigation` - Search behavior (case sensitivity, wrap)

## Known Issues and Limitations

1. **File Watching:** No auto-reload on file changes (unlike Rust version)
2. **Startup Speed:** Python initialization slower than compiled Rust binary
3. **Mark System:** Mark functionality (`m<letter>`, `'<letter>`) is stubbed but not fully implemented

## Testing Strategy

Tests verify:
- Configuration loading and defaults
- Markdown rendering with various elements
- Headline parsing and TOC generation
- Syntax highlighting integration
- Clean ANSI code stripping

Manual TUI testing required for:
- Navigation keybindings
- Visual selection and clipboard
- Search functionality
- Cross-platform curses behavior

## Common Development Tasks

### Adding New Markdown Elements
1. Add renderer method in `renderer.py` (override mistune method)
2. Add color configuration in `config.py` defaults
3. Update tests in `tests/test_basic.py`

### Modifying Keybindings
1. Update `_handle_normal_input()` in `navigator.py`
2. Update help screen in `_render_help()`
3. Update README keyboard shortcuts section

### Extending Configuration
1. Add default values in `config.py` `DEFAULT_CONFIG`
2. Access via `config.get('section.key')` in relevant module
3. Document in README configuration section

### Fixing Display Issues
- Check ANSI stripping in `navigator.py` before curses display
- Verify width calculations use `strip_ansi()` for measurements
- Test on all platforms (Windows curses behaves differently)
