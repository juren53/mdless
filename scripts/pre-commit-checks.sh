#!/bin/bash
# Pre-commit checks for Rust projects
# Runs formatting, linting, compilation checks, and tests

set -e

echo "Running Rust pre-commit checks..."

# Check if we're in a Rust project
if [ ! -f "Cargo.toml" ]; then
    echo "No Cargo.toml found, skipping Rust checks"
    exit 0
fi

# Fast compilation check - run first to catch basic errors quickly
echo "🔍 Running fast compilation check..."
cargo check --all-targets --all-features
if [ $? -ne 0 ]; then
    echo "❌ Compilation check failed. Please fix the errors above."
    exit 1
fi
echo "✅ Fast compilation check passed"

# Format check - ensure code is properly formatted
echo "🔍 Checking code formatting..."
cargo fmt --all -- --check
if [ $? -ne 0 ]; then
    echo "❌ Code formatting issues found. Run 'cargo fmt' to fix."
    exit 1
fi
echo "✅ Code formatting is correct"

# Lint code with clippy
echo "🔍 Running clippy linter..."
cargo clippy --all-targets --all-features -- -D warnings
if [ $? -ne 0 ]; then
    echo "❌ Clippy found issues. Please fix the warnings above."
    exit 1
fi
echo "✅ Clippy checks passed"

# Run tests
echo "🔍 Running tests..."
cargo test --all-features
if [ $? -ne 0 ]; then
    echo "❌ Tests failed. Please fix the failing tests above."
    exit 1
fi
echo "✅ All tests passed"

# Optional: Security audit (uncomment if you want this)
# echo "🔍 Running security audit..."
# cargo audit
# if [ $? -ne 0 ]; then
#     echo "⚠️  Security vulnerabilities found. Consider updating dependencies."
#     # Don't exit on audit failures as they might not be immediately fixable
# fi

echo "🎉 All pre-commit checks passed!"
