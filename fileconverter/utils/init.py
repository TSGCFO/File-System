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
    ensure_directory,
    list_files,
)

from fileconverter.utils.error_handling import (
    ConversionError,
    ConfigError,
    ValidationError,
    handle_error,
)

from fileconverter.utils.logging_utils import (
    get_logger,
    setup_logging,
)

from fileconverter.utils.validation import (
    validate_file_path,
    validate_directory_path,
    validate_parameters,
)

__all__ = [
    # File utilities
    "get_file_format",
    "get_file_extension",
    "get_file_size_mb",
    "ensure_directory",
    "list_files",
    
    # Error handling
    "ConversionError",
    "ConfigError",
    "ValidationError",
    "handle_error",
    
    # Logging
    "get_logger",
    "setup_logging",
    
    # Validation
    "validate_file_path",
    "validate_directory_path",
    "validate_parameters",
]
