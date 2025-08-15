#!/bin/bash
# Install git hooks for the project

set -e

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Installing git hooks for mdless project..."

# Create the pre-commit hook
cat > "$REPO_ROOT/.git/hooks/pre-commit" << 'EOF'
#!/bin/bash
# Pre-commit hook that runs the pre-commit checks script

# Get the directory of the git repository
REPO_ROOT=$(git rev-parse --show-toplevel)

# Run the pre-commit checks script
exec "$REPO_ROOT/scripts/pre-commit-checks.sh"
EOF

# Make the hook executable
chmod +x "$REPO_ROOT/.git/hooks/pre-commit"

echo "✅ Pre-commit hook installed successfully!"
echo ""
echo "The hook will run the following checks before each commit:"
echo "  1. cargo check (fast compilation check)"
echo "  2. cargo fmt --check (code formatting)"
echo "  3. cargo clippy (linting)"
echo "  4. cargo test (run all tests)"
echo ""
echo "To bypass the hook for a specific commit (not recommended):"
echo "  git commit --no-verify"
echo ""
echo "To run the checks manually:"
echo "  ./scripts/pre-commit-checks.sh"
