#!/bin/bash
# Install git hooks for the mdview project

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Installing git hooks for mdview..."

# Create hooks directory if it doesn't exist
mkdir -p "$PROJECT_ROOT/.git/hooks"

# Copy pre-commit hook
cp "$PROJECT_ROOT/.git/hooks/pre-commit" "$PROJECT_ROOT/.git/hooks/pre-commit.backup" 2>/dev/null || true
cat > "$PROJECT_ROOT/.git/hooks/pre-commit" << 'EOF'
#!/bin/bash
# Pre-commit hook for Rust projects
# Runs formatting, linting, compilation checks, and tests

set -e

echo "Running Rust pre-commit checks..."

# Check if we're in a Rust project
if [ ! -f "Cargo.toml" ]; then
    echo "No Cargo.toml found, skipping Rust checks"
    exit 0
fi

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

# Check compilation
echo "🔍 Checking compilation..."
cargo check --all-targets --all-features
if [ $? -ne 0 ]; then
    echo "❌ Compilation failed. Please fix the errors above."
    exit 1
fi
echo "✅ Compilation successful"

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
EOF

chmod +x "$PROJECT_ROOT/.git/hooks/pre-commit"

echo "✅ Pre-commit hook installed successfully!"
echo ""
echo "The hook will now run automatically before each commit and will:"
echo "  - Check code formatting (cargo fmt --check)"
echo "  - Run clippy linter (cargo clippy)"
echo "  - Verify compilation (cargo check)"
echo "  - Run all tests (cargo test)"
echo ""
echo "To bypass the hook for a specific commit, use: git commit --no-verify"
