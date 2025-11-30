"""Syntax highlighting for code blocks."""

from typing import Optional

try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, guess_lexer
    from pygments.formatters import Terminal256Formatter
    from pygments.util import ClassNotFound
    PYGMENTS_AVAILABLE = True
except ImportError:
    PYGMENTS_AVAILABLE = False


class SyntaxHighlighter:
    """Syntax highlighter for code blocks."""
    
    def __init__(self, enabled: bool = True):
        """Initialize syntax highlighter.
        
        Args:
            enabled: Whether to enable syntax highlighting (requires Pygments)
        """
        self.enabled = enabled and PYGMENTS_AVAILABLE
        if self.enabled:
            self.formatter = Terminal256Formatter(style='monokai')
    
    def highlight_code(self, code: str, language: Optional[str] = None) -> str:
        """Highlight code with syntax highlighting.
        
        Args:
            code: The code to highlight
            language: Programming language (e.g., 'python', 'javascript')
        
        Returns:
            Highlighted code string with ANSI escape codes, or plain code if highlighting unavailable
        """
        if not self.enabled:
            return code
        
        try:
            if language:
                # Try to get lexer by language name
                lexer = get_lexer_by_name(language, stripall=True)
            else:
                # Try to guess the language
                lexer = guess_lexer(code)
            
            return highlight(code, lexer, self.formatter).rstrip('\n')
        except (ClassNotFound, Exception):
            # Fallback to plain code if language not found or error occurs
            return code
    
    @staticmethod
    def is_available() -> bool:
        """Check if Pygments is available."""
        return PYGMENTS_AVAILABLE
