"""
Validation utilities for FileConverter.

This module provides functions for validating various types of data
and parameters used throughout the FileConverter package.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from fileconverter.utils.error_handling import ValidationError
from fileconverter.utils.logging_utils import get_logger

logger = get_logger(__name__)


def validate_file_path(
    path: Union[str, Path],
    must_exist: bool = False,
    must_not_exist: bool = False,
    file_size_limit_mb: Optional[float] = None
) -> Path:
    """Validate a file path.
    
    Args:
        path: Path to validate.
        must_exist: Whether the file must exist.
        must_not_exist: Whether the file must not exist.
        file_size_limit_mb: Optional file size limit in megabytes.
    
    Returns:
        Path object for the validated path.
    
    Raises:
        ValidationError: If the path is invalid.
    """
    try:
        file_path = Path(path)
        
        # Check if the path is absolute
        if not file_path.is_absolute():
            file_path = file_path.resolve()
        
        # Check existence
        if must_exist and not file_path.exists():
            raise ValidationError(f"File does not exist: {file_path}")
        
        if must_not_exist and file_path.exists():
            raise ValidationError(f"File already exists: {file_path}")
        
        # Check if it's a file
        if must_exist and file_path.exists() and not file_path.is_file():
            raise ValidationError(f"Path is not a file: {file_path}")
        
        # Check file size
        if must_exist and file_size_limit_mb is not None and file_path.exists():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            if size_mb > file_size_limit_mb:
                raise ValidationError(
                    f"File size ({size_mb:.2f} MB) exceeds limit "
                    f"({file_size_limit_mb} MB): {file_path}"
                )
        
        return file_path
    
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Invalid file path: {str(e)}")


def validate_directory_path(
    path: Union[str, Path],
    must_exist: bool = False,
    create_if_missing: bool = False
) -> Path:
    """Validate a directory path.
    
    Args:
        path: Path to validate.
        must_exist: Whether the directory must exist.
        create_if_missing: Whether to create the directory if it doesn't exist.
    
    Returns:
        Path object for the validated path.
    
    Raises:
        ValidationError: If the path is invalid.
    """
    try:
        dir_path = Path(path)
        
        # Check if the path is absolute
        if not dir_path.is_absolute():
            dir_path = dir_path.resolve()
        
        # Create directory if requested
        if create_if_missing and not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directory: {dir_path}")
        
        # Check existence
        if must_exist and not dir_path.exists():
            raise ValidationError(f"Directory does not exist: {dir_path}")
        
        # Check if it's a directory
        if dir_path.exists() and not dir_path.is_dir():
            raise ValidationError(f"Path is not a directory: {dir_path}")
        
        return dir_path
    
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Invalid directory path: {str(e)}")


def validate_parameters(
    params: Dict[str, Any],
    required_params: Optional[List[str]] = None,
    optional_params: Optional[Dict[str, Any]] = None,
    allow_extra: bool = False
) -> Dict[str, Any]:
    """Validate parameters against required and optional parameters.
    
    Args:
        params: Parameters to validate.
        required_params: List of required parameter names.
        optional_params: Dictionary of optional parameter names and default values.
        allow_extra: Whether to allow extra parameters not in required or optional.
    
    Returns:
        Dictionary with validated parameters.
    
    Raises:
        ValidationError: If the parameters are invalid.
    """
    required_params = required_params or []
    optional_params = optional_params or {}
    
    # Check for missing required parameters
    missing = [param for param in required_params if param not in params]
    if missing:
        raise ValidationError(f"Missing required parameters: {', '.join(missing)}")
    
    # Check for unexpected parameters
    if not allow_extra:
        allowed = set(required_params) | set(optional_params.keys())
        unexpected = [param for param in params if param not in allowed]
        if unexpected:
            raise ValidationError(f"Unexpected parameters: {', '.join(unexpected)}")
    
    # Create result with defaults for optional parameters
    result = {}
    
    # Add required parameters
    for param in required_params:
        result[param] = params[param]
    
    # Add optional parameters
    for param, default in optional_params.items():
        result[param] = params.get(param, default)
    
    # Add extra parameters if allowed
    if allow_extra:
        for param, value in params.items():
            if param not in result:
                result[param] = value
    
    return result


def validate_format_names(
    input_format: str,
    output_format: str,
    supported_formats: Optional[Dict[str, List[str]]] = None
) -> None:
    """Validate that the input and output formats are supported.
    
    Args:
        input_format: Input format name.
        output_format: Output format name.
        supported_formats: Dictionary mapping input formats to lists of
                          supported output formats.
    
    Raises:
        ValidationError: If a format is not supported.
    """
    if supported_formats is None:
        # If no supported formats provided, we can't validate
        return
    
    # Check input format
    if input_format not in supported_formats:
        raise ValidationError(f"Unsupported input format: {input_format}")
    
    # Check output format
    if output_format not in supported_formats[input_format]:
        raise ValidationError(
            f"Unsupported output format {output_format} for input format {input_format}"
        )
