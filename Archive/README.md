# Archive

This directory contains archived versions and previous implementations of the mdless project.

## rust/

Contains the original Rust implementation of mdless, including:
- Source code (`src/`)
- Build artifacts (`target/`)
- Cargo configuration files
- GitHub Actions workflows
- Build scripts
- Original Rust README (`README_RUST.md`)

The Rust version was a fast, terminal-based markdown viewer with features like:
- Real-time rendering with syntax highlighting
- File watching with auto-reload
- Vim-like keybindings for navigation
- Search functionality

### Why Archived?

The project has transitioned to a Python implementation (`mdless-py`) which offers:
- **Visual selection mode with clipboard support** (critical feature missing in Rust version)
- Full less-style navigation conventions
- Easier customization and extension
- Better cross-platform compatibility
- More flexible configuration system

The Rust implementation remains archived for reference and potential future use.

---

**Current Active Implementation:** See main project directory for the Python version (mdless-py)
