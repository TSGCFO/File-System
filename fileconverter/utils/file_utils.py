"""
File utility functions for FileConverter.

This module provides utility functions for file operations,
such as determining file formats, validating paths, etc.
"""

import os
import re
import glob
import shutil
import mimetypes
from pathlib import Path
from typing import List, Optional, Set, Tuple, Union

# Try to import optional dependencies with fallbacks
try:
    import chardet
except ImportError:
    chardet = None

try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

try:
    from pathvalidate import validate_filepath
except ImportError:
    # Define a simple fallback
    def validate_filepath(path):
        """Simple filepath validation fallback."""
        if not isinstance(path, (str, Path)):
            raise ValueError(f"Path must be a string or Path object, not {type(path)}")

from fileconverter.utils.error_handling import ValidationError
from fileconverter.utils.logging_utils import get_logger

logger = get_logger(__name__)

# Initialize mimetypes database
mimetypes.init()


def get_file_extension(path: Union[str, Path]) -> str:
    """Get the file extension from a path.
    
    Args:
        path: Path to the file.
    
    Returns:
        File extension without the dot, or empty string if no extension.
    """
    return os.path.splitext(str(path))[1].lstrip(".").lower()


def get_file_format(path: Union[str, Path]) -> Optional[str]:
    """Determine the format of a file based on its extension and content.
    
    Args:
        path: Path to the file.
    
    Returns:
        Format name, or None if the format cannot be determined.
    """
    path_str = str(path)
    
    # Get extension
    ext = get_file_extension(path_str)
    
    # Check if file exists
    if os.path.exists(path_str):
        # Try to determine format from content using python-magic if available
        if MAGIC_AVAILABLE:
            try:
                mime_type = magic.from_file(path_str, mime=True)
                
                # Map MIME type to format
                mime_format_map = {
                    "application/pdf": "pdf",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
                    "application/msword": "doc",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
                    "application/vnd.ms-excel": "xls",
                    "text/csv": "csv",
                    "text/plain": "txt",
                    "text/html": "html",
                    "text/markdown": "md",
                    "application/json": "json",
                    "application/xml": "xml",
                    "application/zip": "zip",
                    "image/jpeg": "jpeg",
                    "image/png": "png",
                    "image/gif": "gif",
                    "image/bmp": "bmp",
                    "image/tiff": "tiff",
                    "image/webp": "webp",
                }
                
                if mime_type in mime_format_map:
                    return mime_format_map[mime_type]
            
            except Exception as e:
                logger.debug(f"Error determining MIME type: {str(e)}")
        
        # Try mimetypes as a fallback
        try:
            mime_type, _ = mimetypes.guess_type(path_str)
            if mime_type:
                # Map MIME type to format
                mime_format_map = {
                    "application/pdf": "pdf",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
                    "application/msword": "doc",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
                    "application/vnd.ms-excel": "xls",
                    "text/csv": "csv",
                    "text/plain": "txt",
                    "text/html": "html",
                    "text/markdown": "md",
                    "application/json": "json",
                    "application/xml": "xml",
                    "application/zip": "zip",
                    "image/jpeg": "jpeg",
                    "image/png": "png",
                    "image/gif": "gif",
                    "image/bmp": "bmp",
                    "image/tiff": "tiff",
                    "image/webp": "webp",
                }
                
                if mime_type in mime_format_map:
                    return mime_format_map[mime_type]
        except Exception as e:
            logger.debug(f"Error using mimetypes: {str(e)}")
    
    # Fallback to extension-based detection
    ext_format_map = {
        "pdf": "pdf",
        "docx": "docx",
        "doc": "doc",
        "rtf": "rtf",
        "odt": "odt",
        "xlsx": "xlsx",
        "xls": "xls",
        "csv": "csv",
        "tsv": "tsv",
        "ods": "ods",
        "txt": "txt",
        "html": "html",
        "htm": "html",
        "md": "md",
        "markdown": "md",
        "json": "json",
        "xml": "xml",
        "yaml": "yaml",
        "yml": "yaml",
        "ini": "ini",
        "toml": "toml",
        "zip": "zip",
        "tar": "tar",
        "gz": "gz",
        "7z": "7z",
        "jpg": "jpeg",
        "jpeg": "jpeg",
        "png": "png",
        "gif": "gif",
        "bmp": "bmp",
        "tiff": "tiff",
        "tif": "tiff",
        "webp": "webp",
    }
    
    return ext_format_map.get(ext.lower())


def validate_file_path(
    path: Union[str, Path], 
    must_exist: bool = False,
    must_not_exist: bool = False,
    is_dir: bool = False
) -> None:
    """Validate a file path.
    
    Args:
        path: Path to validate.
        must_exist: Whether the path must exist.
        must_not_exist: Whether the path must not exist.
        is_dir: Whether the path is a directory.
    
    Raises:
        ValidationError: If the path is invalid.
    """
    path_str = str(path)
    
    try:
        # Validate path format
        validate_filepath(path_str)
        
        # Check existence
        if must_exist and not os.path.exists(path_str):
            raise ValidationError(f"Path does not exist: {path_str}")
        
        if must_not_exist and os.path.exists(path_str):
            raise ValidationError(f"Path already exists: {path_str}")
        
        # Check if directory
        if is_dir and os.path.exists(path_str) and not os.path.isdir(path_str):
            raise ValidationError(f"Path is not a directory: {path_str}")
        
        # Check if file
        if not is_dir and os.path.exists(path_str) and not os.path.isfile(path_str):
            raise ValidationError(f"Path is not a file: {path_str}")
    
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Invalid path: {path_str} - {str(e)}")


def get_file_size_mb(path: Union[str, Path]) -> float:
    """Get the size of a file in megabytes.
    
    Args:
        path: Path to the file.
    
    Returns:
        File size in megabytes.
    
    Raises:
        ValidationError: If the path is invalid or the file doesn't exist.
    """
    path_str = str(path)
    
    if not os.path.exists(path_str):
        raise ValidationError(f"File does not exist: {path_str}")
    
    if not os.path.isfile(path_str):
        raise ValidationError(f"Path is not a file: {path_str}")
    
    size_bytes = os.path.getsize(path_str)
    size_mb = size_bytes / (1024 * 1024)
    
    return size_mb


def copy_file(
    src_path: Union[str, Path], 
    dst_path: Union[str, Path],
    overwrite: bool = False
) -> None:
    """Copy a file from one location to another.
    
    Args:
        src_path: Source file path.
        dst_path: Destination file path.
        overwrite: Whether to overwrite the destination file if it exists.
    
    Raises:
        ValidationError: If the paths are invalid or the operation fails.
    """
    src_str = str(src_path)
    dst_str = str(dst_path)
    
    # Validate paths
    validate_file_path(src_str, must_exist=True)
    
    if os.path.exists(dst_str) and not overwrite:
        raise ValidationError(f"Destination file already exists: {dst_str}")
    
    # Create destination directory if it doesn't exist
    dst_dir = os.path.dirname(dst_str)
    if dst_dir and not os.path.exists(dst_dir):
        os.makedirs(dst_dir, exist_ok=True)
    
    try:
        shutil.copy2(src_str, dst_str)
    except Exception as e:
        raise ValidationError(f"Failed to copy file: {str(e)}")


def list_files(
    pattern: str, 
    recursive: bool = False
) -> List[str]:
    """List files matching a pattern.
    
    Args:
        pattern: Glob pattern to match files.
        recursive: Whether to search recursively.
    
    Returns:
        List of file paths matching the pattern.
    """
    if recursive:
        # Using recursive glob (Python 3.5+)
        return glob.glob(pattern, recursive=True)
    else:
        return glob.glob(pattern)


def guess_encoding(file_path: Union[str, Path]) -> str:
    """Guess the encoding of a text file.
    
    Args:
        file_path: Path to the file.
    
    Returns:
        Detected encoding, or 'utf-8' as fallback.
    """
    # Default encoding
    default_encoding = 'utf-8'
    
    if chardet is None:
        logger.debug("chardet module not available, defaulting to UTF-8")
        return default_encoding
    
    try:
        # Read a sample of the file
        with open(file_path, 'rb') as f:
            sample = f.read(4096)  # Read first 4K
        
        # Detect encoding
        result = chardet.detect(sample)
        encoding = result['encoding']
        
        # Fallback to utf-8 if detection failed or confidence is low
        if not encoding or result['confidence'] < 0.7:
            encoding = default_encoding
        
        return encoding
    
    except Exception as e:
        logger.warning(f"Error detecting encoding: {str(e)}")
        return default_encoding
