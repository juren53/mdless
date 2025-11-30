"""Terminal UI navigator with less-like keybindings and clipboard support."""

import curses
import re
from typing import List, Optional, Tuple
from pathlib import Path

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

from .document import Document
from .utils import strip_ansi


class Navigator:
    """TUI navigator for viewing markdown documents."""
    
    def __init__(self, document: Document, config):
        """Initialize navigator.
        
        Args:
            document: Document to navigate
            config: Configuration object
        """
        self.document = document
        self.config = config
        self.current_line = 0
        self.top_line = 0
        self.marks = {}  # Named marks (a-z)
        self.search_pattern = None
        self.search_results = []
        self.search_index = -1
        self.visual_mode = False
        self.visual_start = None
        self.mode = "normal"  # normal, search, toc, help
        self.search_input = ""
        self.status_message = ""
        self.screen_height = 24
        self.screen_width = 80
    
    def run(self, stdscr):
        """Main loop for curses interface.
        
        Args:
            stdscr: Curses standard screen object
        """
        curses.curs_set(0)  # Hide cursor
        curses.use_default_colors()
        stdscr.keypad(True)  # Enable keypad mode for arrow keys
        stdscr.nodelay(False)  # Blocking mode
        # Set escape delay to distinguish ESC from escape sequences
        import os
        os.environ.setdefault('ESCDELAY', '25')
        
        # Initialize color pairs
        self._init_colors()
        
        stdscr.clear()
        
        while True:
            self.screen_height, self.screen_width = stdscr.getmaxyx()
            
            # Render current view
            self._render_screen(stdscr)
            
            # Get input
            try:
                key = stdscr.getch()
                
                # Handle escape sequences for arrow keys and special keys
                if key == 27:  # ESC
                    stdscr.nodelay(True)  # Non-blocking to check for sequence
                    next_key = stdscr.getch()
                    if next_key == 91:  # '[' - ANSI escape sequence
                        arrow_key = stdscr.getch()
                        stdscr.nodelay(False)  # Back to blocking
                        if arrow_key == 65:  # 'A' - Up arrow
                            key = curses.KEY_UP
                        elif arrow_key == 66:  # 'B' - Down arrow
                            key = curses.KEY_DOWN
                        elif arrow_key == 67:  # 'C' - Right arrow
                            key = curses.KEY_RIGHT
                        elif arrow_key == 68:  # 'D' - Left arrow
                            key = curses.KEY_LEFT
                        elif arrow_key == 72:  # 'H' - Home
                            key = curses.KEY_HOME
                        elif arrow_key == 70:  # 'F' - End
                            key = curses.KEY_END
                        else:
                            stdscr.nodelay(False)
                            continue
                    else:
                        stdscr.nodelay(False)  # Back to blocking
                        if next_key == -1:  # Real ESC key (no sequence followed)
                            key = 27
                        else:
                            continue  # Unknown sequence, ignore
                
                if self.mode == "search":
                    if not self._handle_search_input(key):
                        break
                elif self.mode == "toc":
                    if not self._handle_toc_input(key, stdscr):
                        break
                elif self.mode == "help":
                    if not self._handle_help_input(key):
                        break
                else:
                    if not self._handle_normal_input(key):
                        break
            except KeyboardInterrupt:
                break
    
    def _init_colors(self):
        """Initialize curses color pairs."""
        try:
            curses.start_color()
            # Status bar and special modes
            curses.init_pair(1, curses.COLOR_CYAN, -1)  # Status bar
            curses.init_pair(2, curses.COLOR_YELLOW, -1)  # Search highlight
            curses.init_pair(3, curses.COLOR_GREEN, -1)  # Visual selection
            
            # Markdown element colors (matching ANSI codes from config)
            curses.init_pair(4, curses.COLOR_BLUE, -1)    # bright_blue
            curses.init_pair(5, curses.COLOR_BLUE, -1)    # blue
            curses.init_pair(6, curses.COLOR_CYAN, -1)    # cyan (heading3-6)
            curses.init_pair(7, curses.COLOR_YELLOW, -1)  # yellow (code, code_block)
            curses.init_pair(8, curses.COLOR_CYAN, -1)    # bright_cyan (link)
            curses.init_pair(9, curses.COLOR_GREEN, -1)   # green (list_marker)
            curses.init_pair(10, curses.COLOR_MAGENTA, -1) # magenta (quote)
            curses.init_pair(11, curses.COLOR_WHITE, -1)  # white (table_border)
            curses.init_pair(12, curses.COLOR_BLACK, -1)  # bright_black (footnote)
            curses.init_pair(13, curses.COLOR_RED, -1)    # red
        except Exception:
            pass
    
    def _ansi_to_curses_attr(self, ansi_code):
        """Convert ANSI color code to curses attribute."""
        # Map basic ANSI codes to curses color pairs
        ansi_map = {
            '30': 0,  # black
            '31': 13, # red
            '32': 9,  # green
            '33': 7,  # yellow
            '34': 5,  # blue
            '35': 10, # magenta
            '36': 6,  # cyan
            '37': 11, # white
            '90': 12, # bright_black
            '91': 13, # bright_red
            '92': 9,  # bright_green
            '93': 7,  # bright_yellow
            '94': 4,  # bright_blue
            '95': 10, # bright_magenta
            '96': 8,  # bright_cyan
            '97': 11, # bright_white
            '1': curses.A_BOLD,     # bold
            '3': curses.A_DIM,      # italic (closest approximation)
            '4': curses.A_UNDERLINE, # underline
        }
        
        # Extract codes from ANSI sequence
        match = re.match(r'\033\[([0-9;]+)m', ansi_code)
        if match:
            codes = match.group(1).split(';')
            
            # Handle simple single-code sequences
            if len(codes) == 1:
                code = codes[0]
                attr = ansi_map.get(code)
                if attr is not None:
                    if isinstance(attr, int) and attr < 20:  # Color pair
                        return curses.color_pair(attr)
                    else:  # Attribute like BOLD
                        return attr
            
            # Handle 256-color sequences (38;5;N for foreground, 48;5;N for background)
            elif len(codes) == 3 and codes[0] in ('38', '48') and codes[1] == '5':
                color_num = int(codes[2])
                # Map 256 colors to basic 8 colors (simplified)
                # 0-7: standard colors, 8-15: bright colors
                if color_num <= 15:
                    basic_codes = ['30', '31', '32', '33', '34', '35', '36', '37',
                                   '90', '91', '92', '93', '94', '95', '96', '97']
                    if color_num < len(basic_codes):
                        code = basic_codes[color_num]
                        attr = ansi_map.get(code)
                        if attr and isinstance(attr, int) and attr < 20:
                            return curses.color_pair(attr)
                # For other 256 colors, use closest basic color
                else:
                    # Rough mapping of 256 colors to 8 basic colors
                    color_map = [
                        0, 13, 9, 7, 5, 10, 6, 11,  # 0-7
                        12, 13, 9, 7, 4, 10, 8, 11  # 8-15
                    ]
                    if color_num < 16:
                        return curses.color_pair(color_map[color_num])
                    # For 16-255, use a simple modulo approach
                    return curses.color_pair(color_map[color_num % 16])
        
        return 0
    
    def _render_screen(self, stdscr):
        """Render current view to screen.
        
        Args:
            stdscr: Curses screen
        """
        stdscr.clear()
        
        if self.mode == "toc":
            self._render_toc(stdscr)
        elif self.mode == "help":
            self._render_help(stdscr)
        else:
            self._render_document(stdscr)
        
        # Render status bar
        self._render_status_bar(stdscr)
        
        stdscr.refresh()
    
    def _render_line_with_ansi(self, stdscr, y, x, line, max_width):
        """Render a line with ANSI color codes as curses attributes.
        
        Args:
            stdscr: Curses screen
            y: Row position
            x: Column position  
            line: Line with ANSI codes
            max_width: Maximum width to render
        """
        # Parse ANSI escape sequences (including 256-color codes)
        ansi_pattern = re.compile(r'\033\[[0-9;]+m')
        
        current_attr = 0
        col = x
        pos = 0
        
        while pos < len(line) and col < x + max_width:
            # Look for ANSI code
            match = ansi_pattern.search(line, pos)
            
            if match and match.start() == pos:
                # Found ANSI code at current position
                ansi_code = match.group()
                if ansi_code == '\033[0m':  # Reset
                    current_attr = 0
                else:
                    # Convert to curses attribute
                    new_attr = self._ansi_to_curses_attr(ansi_code)
                    if new_attr:
                        current_attr = new_attr
                pos = match.end()
            else:
                # Regular text - find next ANSI code or end of line
                next_match = ansi_pattern.search(line, pos)
                end_pos = next_match.start() if next_match else len(line)
                
                # Extract text segment
                text_segment = line[pos:end_pos]
                
                # Truncate if needed
                remaining_width = x + max_width - col
                if len(text_segment) > remaining_width:
                    text_segment = text_segment[:remaining_width - 3] + "..."
                
                # Render text with current attribute
                try:
                    if current_attr:
                        stdscr.addstr(y, col, text_segment, current_attr)
                    else:
                        stdscr.addstr(y, col, text_segment)
                except curses.error:
                    pass
                
                col += len(text_segment)
                pos = end_pos
                
                # Stop if we've filled the line
                if col >= x + max_width:
                    break
    
    def _render_document(self, stdscr):
        """Render document content.
        
        Args:
            stdscr: Curses screen
        """
        content_height = self.screen_height - 1  # Leave room for status bar
        
        # In less, the viewport scrolls with the cursor immediately
        # The top_line follows the current_line directly
        self.top_line = self.current_line
        
        # Render visible lines
        for i in range(content_height):
            line_num = self.top_line + i
            if line_num >= len(self.document.rendered_lines):
                break
            
            line = self.document.rendered_lines[line_num]
            
            # Highlight current line in visual mode or search results
            override_attr = 0
            if self.visual_mode and self.visual_start is not None:
                start, end = sorted([self.visual_start, self.current_line])
                if start <= line_num <= end:
                    override_attr = curses.color_pair(3)
            elif self.search_pattern and line_num in [r[0] for r in self.search_results]:
                override_attr = curses.color_pair(2)
            
            # Render line with ANSI color parsing
            try:
                if override_attr:
                    # Simple mode: strip ANSI and use override color
                    clean_line = strip_ansi(line)
                    if len(clean_line) > self.screen_width - 1:
                        clean_line = clean_line[:self.screen_width - 4] + "..."
                    stdscr.addstr(i, 0, clean_line, override_attr)
                else:
                    # Parse ANSI codes and render with curses colors
                    self._render_line_with_ansi(stdscr, i, 0, line, self.screen_width - 1)
            except curses.error:
                # Ignore errors from writing to last line
                pass
    
    def _render_toc(self, stdscr):
        """Render table of contents.
        
        Args:
            stdscr: Curses screen
        """
        toc = self.document.get_toc()
        
        if not toc:
            stdscr.addstr(0, 0, "No headlines found in document")
            return
        
        title = "Table of Contents (press number to jump, q to return)"
        try:
            stdscr.addstr(0, 0, title, curses.A_BOLD)
        except curses.error:
            pass
        
        content_height = self.screen_height - 2
        for i, line in enumerate(toc[:content_height]):
            try:
                # Strip ANSI codes from TOC lines
                clean_line = strip_ansi(line)
                stdscr.addstr(i + 2, 0, clean_line)
            except curses.error:
                pass
    
    def _render_help(self, stdscr):
        """Render help screen.
        
        Args:
            stdscr: Curses screen
        """
        help_text = [
            "mdless-py - Keyboard Commands",
            "",
            "Movement:",
            "  j, ↓, Enter   - Scroll down one line",
            "  k, ↑          - Scroll up one line",
            "  d, Ctrl+D     - Scroll down half page",
            "  u, Ctrl+U     - Scroll up half page",
            "  f, Space, PgDn- Scroll down full page",
            "  b, PgUp       - Scroll up full page",
            "  g, Home       - Go to top of document",
            "  G, End        - Go to bottom of document",
            "",
            "Search:",
            "  /             - Start search",
            "  n             - Next search result",
            "  N             - Previous search result",
            "",
            "Marks & Selection:",
            "  m<letter>     - Set mark",
            "  '<letter>     - Jump to mark",
            "  v             - Toggle visual selection mode",
            "  y             - Yank (copy) selected text to clipboard",
            "",
            "Navigation:",
            "  t, H          - Show table of contents",
            "  =             - Show current position",
            "  Ctrl+G        - Show file info",
            "",
            "Other:",
            "  h, ?          - Show this help",
            "  r             - Reload file",
            "  q, Q          - Quit",
            "",
            "Press any key to return..."
        ]
        
        for i, line in enumerate(help_text):
            if i >= self.screen_height - 1:
                break
            try:
                stdscr.addstr(i, 0, line)
            except curses.error:
                pass
    
    def _render_status_bar(self, stdscr):
        """Render status bar at bottom.
        
        Args:
            stdscr: Curses screen
        """
        from .utils import get_version_info
        
        status_y = self.screen_height - 1
        
        # Get version info for right side
        version_info = get_version_info()
        
        if self.mode == "search":
            left_status = f"/{self.search_input}"
        elif self.status_message:
            left_status = self.status_message
            self.status_message = ""  # Clear after display
        else:
            # Normal status: filename, position, visual mode indicator
            filename = self.document.file_path.name
            total = len(self.document.rendered_lines)
            percent = int((self.current_line / total * 100)) if total > 0 else 0
            
            visual_indicator = " [VISUAL]" if self.visual_mode else ""
            left_status = f"{filename} | Line {self.current_line + 1}/{total} ({percent}%){visual_indicator}"
        
        # Calculate available space for left status (leave room for version on right)
        version_space = len(version_info) + 1  # +1 for spacing
        left_max_width = self.screen_width - version_space - 1
        
        # Truncate left status if needed
        if len(left_status) > left_max_width:
            left_status = left_status[:left_max_width - 3] + "..."
        
        # Build full status line with right-justified version
        padding_width = self.screen_width - len(left_status) - len(version_info) - 1
        if padding_width < 0:
            padding_width = 0
        full_status = left_status + (" " * padding_width) + version_info
        
        # Ensure it fits exactly
        if len(full_status) > self.screen_width - 1:
            full_status = full_status[:self.screen_width - 1]
        else:
            full_status = full_status.ljust(self.screen_width - 1)
        
        try:
            stdscr.attron(curses.color_pair(1) | curses.A_REVERSE)
            stdscr.addstr(status_y, 0, full_status)
            stdscr.attroff(curses.color_pair(1) | curses.A_REVERSE)
        except curses.error:
            pass
    
    def _handle_normal_input(self, key) -> bool:
        """Handle input in normal mode.
        
        Args:
            key: Key code
        
        Returns:
            False to quit, True to continue
        """
        content_height = self.screen_height - 1
        max_line = len(self.document.rendered_lines) - 1
        
        # Quit
        if key in (ord('q'), ord('Q')):
            return False
        
        # Movement - single line
        elif key in (ord('j'), curses.KEY_DOWN, 10, 13, curses.KEY_ENTER):  # j, down arrow, or Enter
            self.current_line = min(self.current_line + 1, max_line)
        elif key in (ord('k'), curses.KEY_UP):
            self.current_line = max(self.current_line - 1, 0)
        
        # Movement - half page
        elif key in (ord('d'), 4):  # d or Ctrl+D
            self.current_line = min(self.current_line + content_height // 2, max_line)
        elif key in (ord('u'), 21):  # u or Ctrl+U
            self.current_line = max(self.current_line - content_height // 2, 0)
        
        # Movement - full page
        elif key in (ord('f'), ord(' '), curses.KEY_NPAGE):  # f, Space, or Page Down
            self.current_line = min(self.current_line + content_height, max_line)
        elif key in (ord('b'), curses.KEY_PPAGE):  # b or Page Up
            self.current_line = max(self.current_line - content_height, 0)
        
        # Movement - document ends
        elif key in (ord('g'), curses.KEY_HOME):
            self.current_line = 0
        elif key in (ord('G'), curses.KEY_END):
            self.current_line = max_line
        
        # Search
        elif key == ord('/'):
            self.mode = "search"
            self.search_input = ""
        elif key == ord('n'):
            self._jump_to_next_search_result(forward=True)
        elif key == ord('N'):
            self._jump_to_next_search_result(forward=False)
        
        # Visual mode and clipboard
        elif key == ord('v'):
            if not self.visual_mode:
                self.visual_mode = True
                self.visual_start = self.current_line
                self.status_message = "-- VISUAL --"
            else:
                self.visual_mode = False
                self.visual_start = None
                self.status_message = ""
        elif key == ord('y'):
            self._yank_to_clipboard()
        
        # Marks
        elif key == ord('m'):
            # Next key will be the mark name
            self.status_message = "Mark: "
        elif key == ord("'"):
            # Next key will be the mark to jump to
            self.status_message = "Jump to mark: "
        
        # TOC and help
        elif key in (ord('t'), ord('H')):
            self.mode = "toc"
        elif key in (ord('h'), ord('?')):
            self.mode = "help"
        
        # Position info
        elif key == ord('='):
            self.status_message = f"Line {self.current_line + 1} of {max_line + 1}"
        elif key == 7:  # Ctrl+G
            size = self.document.file_path.stat().st_size
            self.status_message = f"{self.document.file_path} | {max_line + 1} lines | {size} bytes"
        
        # Reload (r)
        elif key == ord('r'):
            self.status_message = "Reload not implemented in navigator (restart viewer)"
        
        return True
    
    def _handle_search_input(self, key) -> bool:
        """Handle input in search mode.
        
        Args:
            key: Key code
        
        Returns:
            False to quit, True to continue
        """
        if key == 27:  # ESC
            self.mode = "normal"
            self.search_input = ""
            return True
        elif key in (10, 13, curses.KEY_ENTER):  # Enter
            self._perform_search()
            self.mode = "normal"
            return True
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            self.search_input = self.search_input[:-1]
        elif 32 <= key <= 126:  # Printable characters
            self.search_input += chr(key)
        
        return True
    
    def _handle_toc_input(self, key, stdscr) -> bool:
        """Handle input in TOC mode.
        
        Args:
            key: Key code
            stdscr: Curses screen
        
        Returns:
            False to quit, True to continue
        """
        if key in (ord('q'), 27):  # q or ESC
            self.mode = "normal"
        elif ord('0') <= key <= ord('9'):
            # User is typing a headline number
            self.status_message = f"Jump to headline: {chr(key)}"
            # For simplicity, single digit jump
            try:
                index = int(chr(key))
                headline = self.document.find_headline_by_index(index)
                if headline:
                    self.current_line = headline.line_number
                    self.mode = "normal"
                    self.status_message = f"Jumped to: {headline.text}"
                else:
                    self.status_message = f"Headline {index} not found"
            except ValueError:
                pass
        
        return True
    
    def _handle_help_input(self, key) -> bool:
        """Handle input in help mode.
        
        Args:
            key: Key code
        
        Returns:
            False to quit, True to continue
        """
        self.mode = "normal"
        return True
    
    def _perform_search(self):
        """Perform search with current pattern."""
        if not self.search_input:
            return
        
        self.search_pattern = self.search_input
        self.search_results = []
        
        # Search through all lines
        case_sensitive = self.config.get('navigation.search_case_sensitive', False)
        flags = 0 if case_sensitive else re.IGNORECASE
        
        try:
            pattern = re.compile(self.search_pattern, flags)
            for i, line in enumerate(self.document.rendered_lines):
                clean_line = strip_ansi(line)
                if pattern.search(clean_line):
                    self.search_results.append((i, line))
        except re.error:
            self.status_message = f"Invalid regex: {self.search_pattern}"
            return
        
        if self.search_results:
            self.search_index = 0
            self.current_line = self.search_results[0][0]
            self.status_message = f"Found {len(self.search_results)} matches"
        else:
            self.status_message = f"Pattern not found: {self.search_pattern}"
    
    def _jump_to_next_search_result(self, forward: bool = True):
        """Jump to next or previous search result.
        
        Args:
            forward: True for next, False for previous
        """
        if not self.search_results:
            self.status_message = "No search results"
            return
        
        wrap = self.config.get('navigation.wrap_search', True)
        
        if forward:
            self.search_index = (self.search_index + 1) % len(self.search_results)
            if not wrap and self.search_index == 0:
                self.status_message = "Search hit BOTTOM, no more matches"
                return
        else:
            self.search_index = (self.search_index - 1) % len(self.search_results)
            if not wrap and self.search_index == len(self.search_results) - 1:
                self.status_message = "Search hit TOP, no more matches"
                return
        
        self.current_line = self.search_results[self.search_index][0]
    
    def _yank_to_clipboard(self):
        """Copy selected text to clipboard."""
        if not CLIPBOARD_AVAILABLE:
            self.status_message = "Clipboard not available (install pyperclip)"
            return
        
        if self.visual_mode and self.visual_start is not None:
            # Copy visual selection
            start, end = sorted([self.visual_start, self.current_line])
            lines = []
            for i in range(start, end + 1):
                if i < len(self.document.rendered_lines):
                    lines.append(strip_ansi(self.document.rendered_lines[i]))
            
            text = "\n".join(lines)
            try:
                pyperclip.copy(text)
                self.status_message = f"Yanked {end - start + 1} lines to clipboard"
                # Exit visual mode after yank
                self.visual_mode = False
                self.visual_start = None
            except Exception as e:
                self.status_message = f"Clipboard error: {e}"
        else:
            # Copy current line
            if self.current_line < len(self.document.rendered_lines):
                line = strip_ansi(self.document.rendered_lines[self.current_line])
                try:
                    pyperclip.copy(line)
                    self.status_message = "Yanked current line to clipboard"
                except Exception as e:
                    self.status_message = f"Clipboard error: {e}"


def start_navigator(document: Document, config) -> None:
    """Start the navigator in curses mode.
    
    Args:
        document: Document to navigate
        config: Configuration object
    """
    navigator = Navigator(document, config)
    curses.wrapper(navigator.run)
