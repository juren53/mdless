# Changelog for mdless-py

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.4] - 2025-11-30

### Added
- Interactive config editor script (`edit_config.py`) for easy color customization
- Color documentation (`colors.md`) with complete list of available colors and examples
- Task list support for GitHub-style checkboxes in markdown
- Enter key for line-down navigation (matching traditional `less` behavior)

### Fixed
- Task lists now render as `[✓]` for checked items and `[ ]` for unchecked items
- Removed raw HTML output for task list items (no more `<li class="task-list-item">`)
- Config-driven color mapping in navigator (removed hardcoded overrides)
- Config file loading now respects user color choices properly

### Changed
- Navigator color system now fully respects user configuration
- Improved task list rendering with proper checkbox symbols

## [0.1.3] - 2025-11-30

### Added
- Version and last commit date displayed right-justified in status bar
- `get_version_info()` utility function to fetch version and git commit date

### Changed
- Status bar now shows version info (e.g., "v0.1.3 (2025-11-30)") on the right side
- Left side of status bar truncates if needed to make room for version info

## [0.1.2] - 2025-11-30

### Added
- Full color support in curses display with ANSI code parsing
- Colors now properly displayed for all markdown elements:
  - Headings (blue/cyan shades)
  - Code blocks and inline code (yellow)
  - List markers (green)
  - Links (bright cyan)
  - Block quotes (magenta)
  - Bold and italic text styling
- Support for both basic ANSI color codes and 256-color codes from Pygments

### Fixed
- Colors from config.yaml now properly rendered in terminal display
- Added `curses.start_color()` initialization for color support
- ANSI escape sequences now parsed and converted to curses color attributes

## [0.1.1] - 2025-11-30

### Fixed
- Arrow key navigation (↑/↓/←/→) now properly detected via ANSI escape sequence handling
- Home and End key navigation now work correctly
- Line-by-line scrolling (j/k) now scrolls the viewport immediately, matching true `less` behavior
- Added `stdscr.keypad(True)` to enable curses keypad mode
- Set `ESCDELAY=25` for faster escape sequence detection

### Changed
- Viewport rendering now scrolls immediately with cursor position for responsive navigation

## [0.1.0] - 2025-11-30

### Added
- Complete Python implementation (mdless-py) replacing Rust version
- **Visual selection mode** with `v` key for selecting text
- **Clipboard support** with `y` key to copy selected text (critical new feature)
- Full less-like navigation with comprehensive keybindings:
  - Line movement: `j`/`k`, `↑`/`↓`
  - Half-page scrolling: `d`/`u`, `Ctrl+D`/`Ctrl+U`
  - Full-page scrolling: `f`/`b`, `Space`, `Page Down`/`Page Up`
  - Document navigation: `g`/`G`, `Home`/`End`
- Search functionality with `/` to search, `n`/`N` to navigate results
- Table of contents with `t` or `H` key
- Position tracking with `=` key and file info with `Ctrl+G`
- Help screen accessible with `h` or `?`
- Markdown rendering with mistune v3:
  - GitHub Flavored Markdown (GFM) support
  - Proper table formatting with aligned borders
  - Code blocks with bordered boxes
  - Syntax highlighting via Pygments (optional)
  - Bold, italic, and emphasis rendering
  - Colored bullet lists
  - Block quotes
  - Horizontal rules
  - Link formatting
- Image display support:
  - Auto-detection of terminal image tools (imgcat, chafa, viu, timg)
  - Local image support
  - Optional remote image fetching
  - Configurable image display preferences
- YAML-based configuration system:
  - Customizable colors for all markdown elements
  - Rendering options (tables, footnotes, max width)
  - Navigation preferences (scroll offset, search options)
  - Platform-specific config paths (Windows: %APPDATA%, Unix: ~/.config)
- Document model with headline parsing and TOC generation
- Cross-platform support:
  - Windows (with windows-curses)
  - Linux
  - macOS
- Command-line interface:
  - `--version` flag to show version
  - `--create-config` to generate default configuration
  - `-c/--config` to specify custom config file
- Comprehensive documentation:
  - README.md with full feature documentation
  - QUICKSTART_PYTHON.md for quick start guide
  - IMPLEMENTATION_SUMMARY.md with technical details
  - TEST_RESULTS.md with test results
- Basic test suite with unit and integration tests
- Package metadata (pyproject.toml, requirements.txt)

### Fixed
- ANSI escape code display issues in Windows PowerShell by stripping codes before curses display
- Code block border alignment by calculating visible width without ANSI codes
- Table rendering with proper column width calculation and border alignment

### Changed
- Project rewritten from Rust to Python for easier customization and extension
- Archived Rust implementation to `Archive/rust/` (local only, gitignored)
- Updated .gitignore for Python project structure

### Technical Details
- **Language**: Python 3.8+
- **Dependencies**: mistune, PyYAML, pyperclip, windows-curses (Windows), Pygments (optional), requests (optional)
- **Architecture**: Modular design with separate components for CLI, config, rendering, navigation, syntax highlighting, and image display
- **Lines of Code**: ~2,600 lines added

## [0.2.3] - Previous Rust Implementation
*(Archived - See Archive/rust/ for Rust version history)*

---

## Version Comparison

### Python (0.1.0+)
- ✅ Visual selection mode and clipboard copy
- ✅ Complete less navigation conventions
- ✅ YAML configuration system
- ✅ Easier to customize and extend
- ❌ Slower startup than Rust
- ❌ No file watching/auto-reload yet

### Rust (0.2.x - Archived)
- ✅ Fast startup and performance
- ✅ File watching with auto-reload
- ✅ Smaller binary size
- ❌ No clipboard support
- ❌ Missing some less navigation keys
- ❌ Harder to customize

---

[Unreleased]: https://github.com/juren53/mdless/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/juren53/mdless/releases/tag/v0.1.0
