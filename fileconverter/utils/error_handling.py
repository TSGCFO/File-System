"""
Error handling utilities for FileConverter.

This module defines custom exception classes and error handling functions
for the FileConverter package.
"""

import sys
import traceback
from typing import Any, Dict, List, Optional, Type, Union

from fileconverter.utils.logging_utils import get_logger

logger = get_logger(__name__)


class FileConverterError(Exception):
    """Base exception class for all FileConverter errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the exception.
        
        Args:
            message: Error message.
            details: Optional dictionary with additional error details.
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        """Return string representation of the error."""
        if not self.details:
            return self.message
        
        details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
        return f"{self.message} ({details_str})"


class ConversionError(FileConverterError):
    """Exception raised when a file conversion fails."""
    
    def __init__(
        self, 
        message: str, 
        input_format: Optional[str] = None,
        output_format: Optional[str] = None,
        input_path: Optional[str] = None,
        output_path: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize the exception.
        
        Args:
            message: Error message.
            input_format: Optional input format.
            output_format: Optional output format.
            input_path: Optional input file path.
            output_path: Optional output file path.
            details: Optional dictionary with additional error details.
        """
        error_details = details or {}
        
        if input_format:
            error_details["input_format"] = input_format
        
        if output_format:
            error_details["output_format"] = output_format
        
        if input_path:
            error_details["input_path"] = input_path
        
        if output_path:
            error_details["output_path"] = output_path
        
        super().__init__(message, error_details)


class ConfigError(FileConverterError):
    """Exception raised when there is a configuration error."""
    pass


class ValidationError(FileConverterError):
    """Exception raised when validation fails."""
    pass


def handle_error(
    error: Exception, 
    logger: Any, 
    exit_on_error: bool = False
) -> None:
    """Handle an exception by logging it and optionally exiting.
    
    Args:
        error: The exception to handle.
        logger: Logger to use for logging the error.
        exit_on_error: Whether to exit the program on error.
    """
    if isinstance(error, FileConverterError):
        logger.error(str(error))
        if hasattr(error, "details") and error.details:
            logger.debug(f"Error details: {error.details}")
    else:
        logger.error(f"Error: {str(error)}")
    
    logger.debug("".join(traceback.format_exception(
        type(error), error, error.__traceback__
    )))
    
    if exit_on_error:
        sys.exit(1)


def format_error_for_user(error: Exception) -> str:
    """Format an error message for display to the user.
    
    Args:
        error: The exception to format.
    
    Returns:
        A user-friendly error message.
    """
    if isinstance(error, ConversionError):
        message = f"Conversion error: {error.message}"
        
        # Add relevant details if available
        details = []
        if "input_format" in error.details and "output_format" in error.details:
            details.append(
                f"Converting from {error.details['input_format']} "
                f"to {error.details['output_format']}"
            )
        
        if "input_path" in error.details:
            details.append(f"Input file: {error.details['input_path']}")
        
        if details:
            message += f"\n{' - '.join(details)}"
        
        return message
    
    elif isinstance(error, ConfigError):
        return f"Configuration error: {error.message}"
    
    elif isinstance(error, ValidationError):
        return f"Validation error: {error.message}"
    
    else:
        return f"Error: {str(error)}"
