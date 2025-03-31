"""
Core functionality for the FileConverter package.

This package provides the central components for file conversion,
including the conversion engine and format registry.
"""

# Make core classes available at the package level
from fileconverter.core.engine import ConversionEngine
from fileconverter.core.registry import ConverterRegistry, BaseConverter
from fileconverter.core.utils import get_temp_dir, create_temp_file

__all__ = [
    "ConversionEngine", 
    "ConverterRegistry", 
    "BaseConverter",
    "get_temp_dir",
    "create_temp_file"
]