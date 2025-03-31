"""
FileConverter - A comprehensive file conversion utility.

This package provides tools for converting files between different formats,
with support for documents, spreadsheets, images, data exchange formats,
and archives.
"""

from fileconverter.version import __version__, __author__, __email__

# Import main components for easier access
from fileconverter.core.engine import ConversionEngine
from fileconverter.core.registry import ConverterRegistry
from fileconverter.config import get_config

__all__ = [
    'ConversionEngine', 
    'ConverterRegistry',
    'get_config', 
    '__version__', 
    '__author__', 
    '__email__'
]