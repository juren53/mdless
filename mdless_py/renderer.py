"""Markdown to ANSI terminal renderer."""

import re
from typing import List, Optional
from pathlib import Path

try:
    import mistune
    MISTUNE_AVAILABLE = True
except ImportError:
    MISTUNE_AVAILABLE = False

from .config import Config, ANSI_COLORS
from .highlighter import SyntaxHighlighter
from .images import ImageDisplay


class ANSIRenderer(mistune.HTMLRenderer if MISTUNE_AVAILABLE else object):
    """Custom mistune renderer for ANSI terminal output."""
    
    def __init__(self, config: Config, highlighter: SyntaxHighlighter, 
                 image_display: ImageDisplay, max_width: int = 0):
        """Initialize renderer.
        
        Args:
            config: Configuration object
            highlighter: Syntax highlighter instance
            image_display: Image display handler
            max_width: Maximum line width (0 = no limit)
        """
        if MISTUNE_AVAILABLE:
            super().__init__()
        self.config = config
        self.highlighter = highlighter
        self.image_display = image_display
        self.max_width = max_width
        self.footnotes = []
        self._list_level = 0
        self._in_table = False
    
    def _color(self, element: str) -> str:
        """Get color code for element."""
        return self.config.get_color(element)
    
    def _reset(self) -> str:
        """Get reset code."""
        return ANSI_COLORS["reset"]
    
    def _wrap_text(self, text: str, width: int, indent: int = 0) -> str:
        """Wrap text to specified width with indent."""
        if width <= 0:
            return text
        
        lines = []
        indent_str = " " * indent
        words = text.split()
        current_line = indent_str
        
        for word in words:
            if len(current_line) + len(word) + 1 <= width:
                if current_line == indent_str:
                    current_line += word
                else:
                    current_line += " " + word
            else:
                if current_line.strip():
                    lines.append(current_line)
                current_line = indent_str + word
        
        if current_line.strip():
            lines.append(current_line)
        
        return "\n".join(lines)
    
    # Inline elements
    def text(self, text):
        """Render plain text."""
        return text
    
    def emphasis(self, text):
        """Render emphasized text (italic)."""
        return f"{self._color('emphasis')}{text}{self._reset()}"
    
    def strong(self, text):
        """Render strong text (bold)."""
        return f"{self._color('strong')}{text}{self._reset()}"
    
    def link(self, text, url, title=None):
        """Render link."""
        display_text = text or url
        return f"{self._color('link')}{display_text}{self._reset()} ({url})"
    
    def image(self, text, url, title=None):
        """Render image."""
        # Try to display image if possible
        if self.image_display.can_display_images():
            result = self.image_display.display_image(url)
            if result:
                return f"\n{result}\n"
        
        # Fallback to alt text or link
        alt_text = text or url
        return f"{self._color('link')}[Image: {alt_text}]{self._reset()}\n"
    
    def codespan(self, text):
        """Render inline code."""
        return f"{self._color('code')}`{text}`{self._reset()}"
    
    def linebreak(self):
        """Render line break."""
        return "\n"
    
    def softbreak(self):
        """Render soft break."""
        return "\n"
    
    # Block elements
    def paragraph(self, text):
        """Render paragraph."""
        result = text + "\n"
        
        # Add footnotes if any
        if self.footnotes:
            result += "\n" + self._color('footnote')
            for footnote in self.footnotes:
                result += f"  {footnote}\n"
            result += self._reset()
            self.footnotes = []
        
        return result + "\n"
    
    def heading(self, text, level):
        """Render heading."""
        color_key = f"heading{level}"
        color = self._color(color_key)
        # Keep the # symbols for headline detection
        prefix = "#" * level
        return f"{color}{prefix} {text}{self._reset()}\n\n"
    
    def block_code(self, code, info=None):
        """Render code block."""
        language = info.split()[0] if info else None
        
        # Highlight if possible
        highlighted = self.highlighter.highlight_code(code, language)
        
        # Create bordered block
        color = self._color('code_block')
        border_width = min(80, self.max_width or 80)
        border = "─" * border_width
        content_width = border_width - 1  # Account for space after │
        
        result = f"{color}┌{border}┐\n"
        if language:
            result += f"│ {language:<{content_width}}│\n"
            result += f"├{border}┤\n"
        
        for line in highlighted.split('\n'):
            # Strip ANSI codes to measure actual visible width
            from .utils import strip_ansi
            clean_line = strip_ansi(line)
            
            # Truncate if visible content is too long
            if len(clean_line) > content_width:
                # Need to truncate, but preserve ANSI codes
                line = clean_line[:content_width - 3] + "..."
            
            # Pad the line to align the right border
            # We need to pad based on visible length, not total length with ANSI codes
            clean_len = len(strip_ansi(line))
            padding = content_width - clean_len
            result += f"│ {line}{' ' * padding}│\n"
        
        result += f"└{border}┘{self._reset()}\n\n"
        return result
    
    def block_quote(self, text):
        """Render block quote."""
        color = self._color('quote')
        lines = text.strip().split('\n')
        result = ""
        for line in lines:
            result += f"{color}│ {line}{self._reset()}\n"
        return result + "\n"
    
    def list(self, text, ordered, **attrs):
        """Render list."""
        return text + "\n"
    
    def list_item(self, text):
        """Render list item."""
        color = self._color('list_marker')
        marker = "•"
        
        # Remove trailing newlines from text
        text = text.rstrip('\n')
        
        # Handle multi-line items
        lines = text.split('\n')
        result = f"{color}{marker}{self._reset()} {lines[0]}\n"
        for line in lines[1:]:
            result += f"  {line}\n"
        
        return result
    
    def thematic_break(self):
        """Render horizontal rule."""
        width = self.max_width or 80
        return "─" * width + "\n\n"
    
    # Table support
    def table(self, text):
        """Render table with proper borders."""
        from .utils import strip_ansi
        
        color = self._color('table_border')
        lines = text.strip().split('\n')
        
        if not lines:
            return ""
        
        # Calculate column widths based on content
        max_widths = []
        for line in lines:
            # Split by │ and measure each cell
            cells = [cell.strip() for cell in line.split('│') if cell.strip()]
            for i, cell in enumerate(cells):
                clean_cell = strip_ansi(cell)
                if i >= len(max_widths):
                    max_widths.append(len(clean_cell))
                else:
                    max_widths[i] = max(max_widths[i], len(clean_cell))
        
        # Build table with proper borders
        result = []
        total_width = sum(max_widths) + (len(max_widths) - 1) * 3 + 2  # cells + separators + borders
        
        # Top border
        result.append(f"{color}┌{'─' * (total_width - 2)}┐{self._reset()}")
        
        for idx, line in enumerate(lines):
            # Split cells
            cells = [cell.strip() for cell in line.split('│') if cell.strip()]
            
            # Build row with proper padding
            row_parts = []
            for i, cell in enumerate(cells):
                if i < len(max_widths):
                    clean_cell = strip_ansi(cell)
                    padding = max_widths[i] - len(clean_cell)
                    row_parts.append(f"{cell}{' ' * padding}")
            
            result.append(f"{color}│{self._reset()} {' │ '.join(row_parts)} {color}│{self._reset()}")
            
            # Add separator after header (first line)
            if idx == 0:
                sep_parts = ['─' * w for w in max_widths]
                result.append(f"{color}├{'─┼─'.join(sep_parts)}─┤{self._reset()}")
        
        # Bottom border
        result.append(f"{color}└{'─' * (total_width - 2)}┘{self._reset()}")
        
        return '\n'.join(result) + '\n\n'
    
    def table_head(self, text):
        """Render table header."""
        return text
    
    def table_body(self, text):
        """Render table body."""
        return text
    
    def table_row(self, text):
        """Render table row - just return cells joined."""
        return text.rstrip() + '\n'
    
    def table_cell(self, text, align=None, head=False, **attrs):
        """Render table cell - return text with separator."""
        # Don't add padding here, let table() handle it
        return f"{text} │ "


class MarkdownRenderer:
    """High-level markdown renderer."""
    
    def __init__(self, config: Config):
        """Initialize markdown renderer.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.highlighter = SyntaxHighlighter()
        
        # Initialize image display
        img_config = config.data.get('images', {})
        self.image_display = ImageDisplay(
            tool=img_config.get('display_tool', 'auto'),
            fetch_remote=img_config.get('fetch_remote', False),
            max_width=img_config.get('max_width', 80),
            max_height=img_config.get('max_height', 24)
        )
        
        # Get max width
        max_width = config.get('rendering.max_width', 0)
        
        if not MISTUNE_AVAILABLE:
            raise ImportError("mistune is required for markdown rendering")
        
        # Create renderer and markdown parser
        self.renderer = ANSIRenderer(config, self.highlighter, self.image_display, max_width)
        self.markdown = mistune.create_markdown(
            renderer=self.renderer,
            plugins=['strikethrough', 'table', 'url', 'task_lists']
        )
    
    def render(self, markdown_text: str) -> List[str]:
        """Render markdown to list of ANSI-formatted lines.
        
        Args:
            markdown_text: Markdown source text
        
        Returns:
            List of rendered lines
        """
        rendered = self.markdown(markdown_text)
        lines = rendered.split('\n')
        
        # Remove excessive blank lines (more than 2 consecutive)
        result = []
        blank_count = 0
        for line in lines:
            if not line.strip():
                blank_count += 1
                if blank_count <= 2:
                    result.append(line)
            else:
                blank_count = 0
                result.append(line)
        
        return result
    
    def render_file(self, file_path: Path) -> List[str]:
        """Render markdown file to list of ANSI-formatted lines.
        
        Args:
            file_path: Path to markdown file
        
        Returns:
            List of rendered lines
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return self.render(content)
