"""Basic integration tests for mdless-py."""

from pathlib import Path
from mdless_py.config import Config
from mdless_py.renderer import MarkdownRenderer
from mdless_py.document import Document
from mdless_py.highlighter import SyntaxHighlighter


def test_config_loading():
    """Test configuration loading."""
    config = Config()
    assert config.get('colors.heading1') == 'bright_blue'
    assert config.get('rendering.enable_tables') is True


def test_syntax_highlighter():
    """Test syntax highlighter."""
    highlighter = SyntaxHighlighter()
    code = "print('hello world')"
    result = highlighter.highlight_code(code, 'python')
    assert result  # Should return something


def test_markdown_rendering():
    """Test basic markdown rendering."""
    config = Config()
    renderer = MarkdownRenderer(config)
    
    markdown = """# Test Heading

This is a **bold** and *italic* test.

- Item 1
- Item 2

```python
print("test")
```
"""
    
    lines = renderer.render(markdown)
    assert len(lines) > 0
    assert any('Test Heading' in line for line in lines)


def test_document_headline_parsing():
    """Test headline parsing in documents."""
    config = Config()
    renderer = MarkdownRenderer(config)
    
    markdown = """# Heading 1

Some text.

## Heading 2

More text.

### Heading 3
"""
    
    lines = renderer.render(markdown)
    document = Document(Path("test.md"), lines)
    
    assert len(document.headlines) == 3
    assert document.headlines[0].text == 'Heading 1'
    assert document.headlines[1].text == 'Heading 2'
    assert document.headlines[2].text == 'Heading 3'


def test_toc_generation():
    """Test table of contents generation."""
    config = Config()
    renderer = MarkdownRenderer(config)
    
    markdown = """# Main Title

## Section 1

### Subsection 1.1

## Section 2
"""
    
    lines = renderer.render(markdown)
    document = Document(Path("test.md"), lines)
    toc = document.get_toc()
    
    assert len(toc) == 4
    assert 'Main Title' in toc[0]
    assert 'Section 1' in toc[1]


if __name__ == '__main__':
    # Run tests manually
    print("Running tests...")
    test_config_loading()
    print("✓ Config loading")
    
    test_syntax_highlighter()
    print("✓ Syntax highlighter")
    
    test_markdown_rendering()
    print("✓ Markdown rendering")
    
    test_document_headline_parsing()
    print("✓ Document headline parsing")
    
    test_toc_generation()
    print("✓ TOC generation")
    
    print("\n✓ All tests passed!")
