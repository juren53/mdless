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

| Key | Action |
|-----|--------|
| `q` | Quit the application |
| `r` | Reload the file manually |
| `↑` / `k` | Scroll up |
| `↓` / `j` | Scroll down |
| `Page Up` | Scroll up 10 lines |
| `Page Down` | Scroll down 10 lines |
| `Home` | Go to top |
| `End` | Go to bottom |

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

## License

MIT License
