"""Document model for markdown files with headline parsing."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class Headline:
    """Represents a markdown headline."""
    level: int  # 1-6 for h1-h6
    text: str
    line_number: int  # Line number in rendered output


class Document:
    """Markdown document with parsed content and structure."""
    
    def __init__(self, file_path: Path, rendered_lines: List[str]):
        """Initialize document.
        
        Args:
            file_path: Path to the markdown file
            rendered_lines: List of rendered output lines
        """
        self.file_path = file_path
        self.rendered_lines = rendered_lines
        self.headlines: List[Headline] = []
        self._parse_headlines()
    
    def _parse_headlines(self):
        """Parse headlines from rendered lines."""
        # Pattern to match ANSI-colored headings (they start with escape codes)
        # We'll look for lines that appear to be headings based on common patterns
        
        for i, line in enumerate(self.rendered_lines):
            # Remove ANSI codes for analysis
            clean_line = self._strip_ansi(line).strip()
            
            # Check if this looks like a heading
            # Headings are typically short, don't end with punctuation (except ?!), 
            # and may have leading # symbols if we kept them
            if clean_line:
                # Detect ATX-style headings (### Heading)
                atx_match = re.match(r'^(#{1,6})\s+(.+)$', clean_line)
                if atx_match:
                    level = len(atx_match.group(1))
                    text = atx_match.group(2).strip()
                    self.headlines.append(Headline(level=level, text=text, line_number=i))
    
    def _strip_ansi(self, text: str) -> str:
        """Remove ANSI escape codes."""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def get_toc(self) -> List[str]:
        """Get table of contents as formatted lines.
        
        Returns:
            List of TOC lines with indentation based on heading level
        """
        toc = []
        for i, headline in enumerate(self.headlines):
            indent = "  " * (headline.level - 1)
            toc.append(f"{i+1:3}. {indent}{headline.text} (line {headline.line_number + 1})")
        return toc
    
    def find_headline_by_index(self, index: int) -> Optional[Headline]:
        """Find headline by TOC index (1-based).
        
        Args:
            index: TOC index (1-based)
        
        Returns:
            Headline or None if not found
        """
        if 0 < index <= len(self.headlines):
            return self.headlines[index - 1]
        return None
    
    def find_headline_by_pattern(self, pattern: str) -> Optional[Headline]:
        """Find first headline matching pattern.
        
        Args:
            pattern: Text pattern to search for (case-insensitive)
        
        Returns:
            First matching headline or None
        """
        pattern_lower = pattern.lower()
        for headline in self.headlines:
            if pattern_lower in headline.text.lower():
                return headline
        return None
    
    def get_section_lines(self, start_line: int, end_line: Optional[int] = None) -> List[str]:
        """Get lines for a specific section.
        
        Args:
            start_line: Starting line number (0-based)
            end_line: Ending line number (0-based), or None for rest of document
        
        Returns:
            List of lines in the section
        """
        if end_line is None:
            return self.rendered_lines[start_line:]
        return self.rendered_lines[start_line:end_line]
    
    def get_headline_section(self, headline: Headline) -> List[str]:
        """Get all lines from headline to next same-or-higher level heading.
        
        Args:
            headline: The headline to get section for
        
        Returns:
            List of lines in the section
        """
        start_line = headline.line_number
        
        # Find next headline at same or higher level
        end_line = None
        found_start = False
        for h in self.headlines:
            if h.line_number == start_line:
                found_start = True
                continue
            if found_start and h.level <= headline.level:
                end_line = h.line_number
                break
        
        return self.get_section_lines(start_line, end_line)
    
    def total_lines(self) -> int:
        """Get total number of lines in document."""
        return len(self.rendered_lines)
