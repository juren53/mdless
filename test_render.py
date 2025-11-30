"""Test rendering without launching full TUI."""

from pathlib import Path
from mdless_py.config import Config
from mdless_py.renderer import MarkdownRenderer
from mdless_py.document import Document

# Test with README.md
file_path = Path("README.md")
config = Config()
renderer = MarkdownRenderer(config)

print("Rendering README.md...")
try:
    rendered_lines = renderer.render_file(file_path)
    print(f"Successfully rendered {len(rendered_lines)} lines")
    
    # Create document and test headline parsing
    document = Document(file_path, rendered_lines)
    print(f"Found {len(document.headlines)} headlines")
    
    # Show first few headlines
    toc = document.get_toc()
    if toc:
        print("\nTable of Contents (first 10):")
        for line in toc[:10]:
            print(line)
    
    # Show first 20 lines of rendered output
    print("\nFirst 20 lines of rendered output:")
    print("=" * 80)
    for i, line in enumerate(rendered_lines[:20]):
        print(f"{i+1:3}: {line}")
    print("=" * 80)
    
    print("\n✓ Rendering test passed!")
    print("\nTo view with full TUI navigation, run:")
    print("  python -m mdless_py README.md")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
