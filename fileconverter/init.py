"""
FileConverter - A comprehensive file conversion utility.

This package provides tools for converting files between various formats,
with support for documents, spreadsheets, images, data exchange formats,
and archives.
"""

from fileconverter.version import __version__, __author__, __email__

# Import core components for easier access
from fileconverter.core.engine import ConversionEngine
from fileconverter.core.registry import ConverterRegistry

# Setup logging
from fileconverter.utils.logging_utils import setup_logging
setup_logging()

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "ConversionEngine",
    "ConverterRegistry",
]
