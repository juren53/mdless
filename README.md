# mdless-py

A cross-platform CLI Markdown viewer built with Python, featuring advanced navigation, syntax highlighting, and clipboard support.

## Features

- **Rich Markdown Rendering**: Full support for GitHub Flavored Markdown including tables, code blocks, and more
- **Syntax Highlighting**: Code blocks with Pygments support (optional)
- **Less-like Navigation**: Full keyboard navigation with vim-like keybindings
- **Visual Selection & Clipboard**: Select text and copy to clipboard with `v` and `y`
- **Image Display**: Inline image viewing with imgcat, chafa, viu, or timg (optional)
- **Table of Contents**: Navigate by document sections with `t` or `H`
- **Search**: Regex search with `/`, navigate results with `n`/`N`
- **Configurable**: Customizable colors and rendering options via YAML config
- **Cross-platform**: Works on Windows, macOS, and Linux

## Installation

### From Source

```bash
# Clone or navigate to the repository
cd mdless

# Install with pip
pip install -e .

# Or install with all optional dependencies
pip install -e ".[all]"
```

### Requirements

**Required:**
- Python 3.8+
- mistune (Markdown parser)
- PyYAML (configuration)
- pyperclip (clipboard support)
- windows-curses (Windows only, for TUI)

**Optional:**
- Pygments (syntax highlighting)
- requests (remote image fetching)
- imgcat/chafa/viu/timg (image display in terminal)

## Usage

### Basic Usage

```bash
mdless-py README.md
```

### With Custom Config

```bash
mdless-py -c config.yaml document.md
```

### Create Default Config

```bash
mdless-py --create-config
```

Config will be created at:
- Windows: `%APPDATA%\mdless-py\config.yaml`
- Linux/macOS: `~/.config/mdless-py/config.yaml`

## Keyboard Shortcuts

### Movement
- `j`, `↓` - Scroll down one line
- `k`, `↑` - Scroll up one line
- `d`, `Ctrl+D` - Scroll down half page
- `u`, `Ctrl+U` - Scroll up half page
- `f`, `Space`, `Page Down` - Scroll down full page
- `b`, `Page Up` - Scroll up full page
- `g`, `Home` - Go to top of document
- `G`, `End` - Go to bottom of document

### Search
- `/` - Start search
- `n` - Next search result
- `N` - Previous search result

### Visual Selection & Clipboard
- `v` - Toggle visual selection mode
- `y` - Yank (copy) selected text to clipboard

### Navigation
- `t`, `H` - Show table of contents
- `=` - Show current position
- `Ctrl+G` - Show file info

### Other
- `h`, `?` - Show help
- `r` - Reload file
- `q`, `Q` - Quit

## Configuration

Example `config.yaml`:

```yaml
colors:
  heading1: bright_blue
  heading2: blue
  heading3: cyan
  code: yellow
  link: bright_cyan
  emphasis: italic
  strong: bold

rendering:
  enable_tables: true
  enable_footnotes: true
  max_width: 100

images:
  display_tool: auto  # auto, imgcat, chafa, viu, timg, none
  fetch_remote: false
  max_width: 80

navigation:
  search_case_sensitive: false
  wrap_search: true
```

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Running from Source

```bash
python -m mdless_py README.md
```

## License

Apache License 2.0 - See LICENSE file for details

## Comparison with Rust Version

This Python implementation offers:
- ✅ All basic less navigation conventions
- ✅ Visual selection mode with clipboard support
- ✅ More flexible configuration system
- ✅ Easier to extend and customize

The Rust version offers:
- ⚡ Faster startup and performance
- 📦 Smaller binary size
- 🔄 File watching with auto-reload
