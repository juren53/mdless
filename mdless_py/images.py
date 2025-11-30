"""Image display handler for inline images in markdown."""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse

from .utils import which


class ImageDisplay:
    """Handle image display in terminal using various tools."""
    
    # Priority order for image display tools
    TOOLS = ['imgcat', 'chafa', 'viu', 'timg']
    
    def __init__(self, tool: str = "auto", fetch_remote: bool = False, 
                 max_width: int = 80, max_height: int = 24):
        """Initialize image display handler.
        
        Args:
            tool: Image display tool to use ('auto', 'imgcat', 'chafa', 'viu', 'timg', 'none')
            fetch_remote: Whether to fetch and display remote images
            max_width: Maximum width for displayed images
            max_height: Maximum height for displayed images
        """
        self.tool = tool
        self.fetch_remote = fetch_remote
        self.max_width = max_width
        self.max_height = max_height
        self._detected_tool = None
        
        if tool != "none":
            self._detect_tool()
    
    def _detect_tool(self):
        """Detect available image display tool."""
        if self.tool == "auto":
            for tool in self.TOOLS:
                if which(tool):
                    self._detected_tool = tool
                    return
        else:
            if which(self.tool):
                self._detected_tool = self.tool
    
    def can_display_images(self) -> bool:
        """Check if image display is available."""
        return self._detected_tool is not None
    
    def display_image(self, image_path: str) -> Optional[str]:
        """Display an image and return terminal output or placeholder.
        
        Args:
            image_path: Path to image file (local or URL)
        
        Returns:
            Terminal output string or placeholder message, None if failed
        """
        if not self._detected_tool:
            return f"[Image: {image_path}]"
        
        # Check if it's a URL
        parsed = urlparse(image_path)
        if parsed.scheme in ('http', 'https'):
            if not self.fetch_remote:
                return f"[Remote image (disabled): {image_path}]"
            
            # Download remote image
            local_path = self._download_image(image_path)
            if not local_path:
                return f"[Failed to download: {image_path}]"
            image_path = local_path
        
        # Verify local file exists
        if not Path(image_path).exists():
            return f"[Image not found: {image_path}]"
        
        # Display using detected tool
        return self._display_with_tool(image_path)
    
    def _download_image(self, url: str) -> Optional[str]:
        """Download remote image to temp file.
        
        Args:
            url: Image URL
        
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            import requests
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Create temp file with appropriate extension
            suffix = Path(urlparse(url).path).suffix or '.png'
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
                f.write(response.content)
                return f.name
        except Exception:
            return None
    
    def _display_with_tool(self, image_path: str) -> Optional[str]:
        """Display image using the detected tool.
        
        Args:
            image_path: Local path to image
        
        Returns:
            Terminal output or error message
        """
        try:
            if self._detected_tool == 'imgcat':
                # imgcat outputs image directly
                result = subprocess.run(['imgcat', image_path], 
                                       capture_output=True, text=True, timeout=5)
                return result.stdout if result.returncode == 0 else None
            
            elif self._detected_tool == 'chafa':
                # chafa with size constraints
                result = subprocess.run([
                    'chafa',
                    '--size', f'{self.max_width}x{self.max_height}',
                    image_path
                ], capture_output=True, text=True, timeout=5)
                return result.stdout if result.returncode == 0 else None
            
            elif self._detected_tool == 'viu':
                # viu with width constraint
                result = subprocess.run([
                    'viu',
                    '-w', str(self.max_width),
                    image_path
                ], capture_output=True, text=True, timeout=5)
                return result.stdout if result.returncode == 0 else None
            
            elif self._detected_tool == 'timg':
                # timg with size constraints
                result = subprocess.run([
                    'timg',
                    '-g', f'{self.max_width}x{self.max_height}',
                    image_path
                ], capture_output=True, text=True, timeout=5)
                return result.stdout if result.returncode == 0 else None
            
        except Exception as e:
            return f"[Error displaying image: {e}]"
        
        return None
    
    def get_tool_name(self) -> str:
        """Get the name of the detected/configured tool."""
        return self._detected_tool or "none"
