# mdview

A fast, terminal-based markdown file viewer built with Rust.

## Features

- **Real-time rendering**: View markdown files with syntax highlighting
- **File watching**: Automatically reload when files change (with `-w` flag)
- **Keyboard navigation**: Scroll through documents with vim-like keybindings
- **Syntax highlighting**: Code blocks with proper highlighting
- **Cross-platform**: Works on Linux, macOS, and Windows

## Installation

```bash
cargo install --path .
```

## Usage

### Basic usage
```bash
mdview README.md
```

### Watch mode (auto-reload on file changes)
```bash
mdview -w README.md
```

## Keybindings

### Basic Controls
| Key | Action |
|-----|--------|
| `q` | Quit the application |
| `r` | Reload the file manually |

### Vim-Style Movement
| Key | Action |
|-----|--------|
| `j` / `↓` | Scroll down one line |
| `k` / `↑` | Scroll up one line |
| `J` | Scroll down 5 lines |
| `K` | Scroll up 5 lines |
| `d` | Scroll down half page |
| `u` | Scroll up half page |
| `D` | Scroll down 10 lines |
| `U` | Scroll up 10 lines |
| `f` / `Page Down` | Scroll down full page |
| `b` / `Page Up` | Scroll up full page |
| `g` / `Home` | Go to top of document |
| `G` / `End` | Go to bottom of document |
| `M` | Go to middle of document |

## Development

### Prerequisites

- Rust 1.70 or later
- Cargo

### Building

```bash
cargo build --release
```

### Running tests

```bash
cargo test
```

### Code formatting and linting

```bash
cargo fmt
cargo clippy
```

### Pre-commit hooks

The project includes a pre-commit hook that automatically runs formatting checks, linting, compilation verification, and tests before each commit. To install the hook:

```bash
# The hook is already installed if you're working in this repository
# To reinstall or update:
./scripts/install-hooks.sh
```

The pre-commit hook will run:
- `cargo fmt --check` - Verify code formatting
- `cargo clippy` - Run linter with warnings as errors
- `cargo check` - Verify compilation
- `cargo test` - Run all tests

To bypass the hook for a specific commit (not recommended):
```bash
git commit --no-verify
```

## License

MIT License
