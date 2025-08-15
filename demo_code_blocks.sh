#!/bin/bash

echo "Building mdless with improved code blocks..."
cargo build --release

echo ""
echo "Demo: Improved Code Block Rendering"
echo "==================================="
echo ""
echo "The code blocks now feature:"
echo "• Proper syntax highlighting using syntect"
echo "• HTML-like bordered styling with box drawing characters"
echo "• Language labels for fenced code blocks"
echo "• Better visual separation from regular text"
echo "• Improved inline code styling"
echo ""
echo "Press any key to view the demo file..."
read -n 1 -s

./target/release/mdless test_code_blocks.md
