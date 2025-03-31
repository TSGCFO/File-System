"""
Utility functions for the FileConverter package.

This package provides various helper functions and utilities used throughout
the FileConverter package.
"""

# Import commonly used utility functions for easier access
from fileconverter.utils.file_utils import (
    get_file_format,
    get_file_extension,
    get_file_size_mb,
    list_files,
    validate_file_path,
    copy_file,
    guess_encoding
)

from fileconverter.utils.error_handling import (
    FileConverterError,
    ConversionError,
    ConfigError,
    ValidationError,
    handle_error,
    format_error_for_user
)

from fileconverter.utils.logging_utils import (
    get_logger,
)

from fileconverter.utils.validation import (
    validate_file_path,
)

__all__ = [
    # File utilities
    "get_file_format",
    "get_file_extension",
    "get_file_size_mb",
    "list_files",
    "copy_file",
    "guess_encoding",
    
    # Error handling
    "FileConverterError",
    "ConversionError",
    "ConfigError", 
    "ValidationError",
    "handle_error",
    "format_error_for_user",
    
    # Logging
    "get_logger",
    
    # Validation
    "validate_file_path",
]