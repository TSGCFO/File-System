"""
GUI resources for FileConverter.

This module provides access to resources like icons and stylesheets
used in the FileConverter GUI.
"""

import os
from pathlib import Path

# Get the resources directory path
RESOURCES_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
ICONS_DIR = RESOURCES_DIR / "icons"
STYLES_DIR = RESOURCES_DIR / "styles"

def get_icon_path(icon_name: str) -> str:
    """Get the absolute path to an icon.
    
    Args:
        icon_name: Name of the icon file (with extension).
    
    Returns:
        Absolute path to the icon file.
    """
    return str(ICONS_DIR / icon_name)

def get_style_path(style_name: str) -> str:
    """Get the absolute path to a stylesheet.
    
    Args:
        style_name: Name of the stylesheet file (with extension).
    
    Returns:
        Absolute path to the stylesheet file.
    """
    return str(STYLES_DIR / style_name)

def load_stylesheet(style_name: str = "default.qss") -> str:
    """Load a stylesheet from the styles directory.
    
    Args:
        style_name: Name of the stylesheet file (default: default.qss).
    
    Returns:
        Contents of the stylesheet file.
    """
    style_path = get_style_path(style_name)
    try:
        with open(style_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error loading stylesheet {style_name}: {str(e)}")
        return ""