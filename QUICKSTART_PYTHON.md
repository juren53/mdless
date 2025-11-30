# mdless-py Quick Start

## Installation Complete! ✓

The Python implementation of mdless has been successfully installed.

## Quick Test

```powershell
# View the main README
python -m mdless_py README.md

# View the Python-specific README
python -m mdless_py README_PYTHON.md

# View this quick start guide
python -m mdless_py QUICKSTART_PYTHON.md
```

## Essential Keyboard Shortcuts

Once you open a file, use these keys to navigate:

### Movement
- `j` or `↓` - Move down one line
- `k` or `↑` - Move up one line  
- `Space` or `f` - Page down
- `b` - Page up
- `g` - Go to top
- `G` - Go to end

### Visual Selection & Clipboard (NEW!)
- `v` - Enter visual selection mode
- Move with `j`/`k` to select text
- `y` - Copy (yank) selected text to clipboard
- `v` again - Exit visual mode

### Search
- `/` - Start search (type your pattern and press Enter)
- `n` - Next match
- `N` - Previous match

### Other Features
- `t` or `H` - Show table of contents
- `h` or `?` - Show full help
- `q` - Quit

## Features

✅ **All Less Navigation Conventions** - Full vim-like keyboard navigation
✅ **Clipboard Support** - Visual selection mode with copy to clipboard (v + y)
✅ **Syntax Highlighting** - Code blocks with Pygments
✅ **Table Rendering** - Proper GitHub Flavored Markdown tables
✅ **Image Display** - Support for imgcat, chafa, viu, timg
✅ **Search** - Regex search with highlighting
✅ **Configurable** - Customizable colors and options

## Configuration

Create a default config file:

```powershell
python -m mdless_py --create-config
```

Config location:
- Windows: `%APPDATA%\mdless-py\config.yaml`
- Linux/Mac: `~/.config/mdless-py/config.yaml`

## What Makes This Better?

Compared to the Rust version, mdless-py adds:

1. **Visual Selection Mode** - Press `v`, move to select, `y` to copy
2. **Full Less Navigation** - All standard less keybindings
3. **Clipboard Integration** - Native clipboard support with pyperclip
4. **Easy Customization** - Python codebase for easy extension
5. **Flexible Configuration** - YAML-based configuration system

## Testing Different Features

### Test Syntax Highlighting
```powershell
python -m mdless_py test_code_blocks.md
```

### Test Search
```powershell
# Open a file, then press `/` and type a search term
python -m mdless_py README.md
```

### Test Table of Contents
```powershell
# Open a file, then press `t` to see all headings
python -m mdless_py README.md
```

## Troubleshooting

**Clipboard not working?**
- pyperclip is installed, but it may need system clipboard utilities
- Windows: Should work out of the box
- Linux: May need `xclip` or `xsel` installed
- macOS: Should work out of the box

**Colors not showing?**
- Make sure your terminal supports ANSI colors
- Try Windows Terminal or a modern terminal emulator

**Pygments not working?**
- Install with: `pip install Pygments`

## Next Steps

- Read the full documentation in `README_PYTHON.md`
- Customize your config file
- Try viewing your own markdown files!

Enjoy your enhanced markdown viewing experience! 🎉
