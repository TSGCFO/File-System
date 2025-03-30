"""
Utility functions for the core functionality of FileConverter.

This module provides various helper functions used by the core components.
"""

import mimetypes
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

from fileconverter.utils.logging_utils import get_logger

logger = get_logger(__name__)

# Initialize mimetypes
mimetypes.init()

# Common format groups
DOCUMENT_FORMATS = {
    "doc", "docx", "rtf", "odt", "pdf", "txt", "md", "html", "htm"
}

SPREADSHEET_FORMATS = {
    "xls", "xlsx", "csv", "tsv", "ods"
}

IMAGE_FORMATS = {
    "jpg", "jpeg", "png", "gif", "bmp", "tiff", "tif", "webp", "svg"
}

DATA_EXCHANGE_FORMATS = {
    "json", "xml", "yaml", "yml", "ini", "toml"
}

ARCHIVE_FORMATS = {
    "zip", "tar", "gz", "7z", "rar"
}

FONT_FORMATS = {
    "ttf", "otf", "woff", "woff2", "eot"
}

PDF_FORMATS = {
    "pdf"
}

# Format to MIME type mapping
FORMAT_TO_MIME: Dict[str, str] = {
    # Documents
    "doc": "application/msword",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "rtf": "application/rtf",
    "odt": "application/vnd.oasis.opendocument.text",
    "pdf": "application/pdf",
    "txt": "text/plain",
    "md": "text/markdown",
    "html": "text/html",
    "htm": "text/html",
    
    # Spreadsheets
    "xls": "application/vnd.ms-excel",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "csv": "text/csv",
    "tsv": "text/tab-separated-values",
    "ods": "application/vnd.oasis.opendocument.spreadsheet",
    
    # Images
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "bmp": "image/bmp",
    "tiff": "image/tiff",
    "tif": "image/tiff",
    "webp": "image/webp",
    "svg": "image/svg+xml",
    
    # Data Exchange
    "json": "application/json",
    "xml": "application/xml",
    "yaml": "application/x-yaml",
    "yml": "application/x-yaml",
    "ini": "text/plain",
    "toml": "application/toml",
    
    # Archives
    "zip": "application/zip",
    "tar": "application/x-tar",
    "gz": "application/gzip",
    "7z": "application/x-7z-compressed",
    "rar": "application/vnd.rar",
    
    # Fonts
    "ttf": "font/ttf",
    "otf": "font/otf",
    "woff": "font/woff",
    "woff2": "font/woff2",
    "eot": "application/vnd.ms-fontobject",
}

# MIME type to format mapping (reverse of FORMAT_TO_MIME)
MIME_TO_FORMAT: Dict[str, str] = {
    mime: fmt for fmt, mime in FORMAT_TO_MIME.items()
}


def get_format_category(format_name: str) -> Optional[str]:
    """Get the category of a file format.
    
    Args:
        format_name: Name of the format (e.g., "pdf", "xlsx").
    
    Returns:
        Category name, or None if the format is unknown.
    """
    format_lower = format_name.lower()
    
    if format_lower in DOCUMENT_FORMATS:
        return "document"
    elif format_lower in SPREADSHEET_FORMATS:
        return "spreadsheet"
    elif format_lower in IMAGE_FORMATS:
        return "image"
    elif format_lower in DATA_EXCHANGE_FORMATS:
        return "data_exchange"
    elif format_lower in ARCHIVE_FORMATS:
        return "archive"
    elif format_lower in FONT_FORMATS:
        return "font"
    elif format_lower in PDF_FORMATS:
        return "pdf"
    else:
        return None


def get_mime_type(file_path: Union[str, Path]) -> Optional[str]:
    """Get the MIME type of a file.
    
    Args:
        file_path: Path to the file.
    
    Returns:
        MIME type as a string, or None if it couldn't be determined.
    """
    file_path = Path(file_path)
    
    # Try to get MIME type from extension
    mime_type, _ = mimetypes.guess_type(str(file_path))
    
    if mime_type:
        return mime_type
    
    # If file exists, try to determine MIME type from content
    if file_path.exists() and file_path.is_file():
        try:
            import magic
            with open(file_path, "rb") as f:
                return magic.from_buffer(f.read(2048), mime=True)
        except ImportError:
            logger.warning("python-magic not available, falling back to extension-based detection")
        except Exception as e:
            logger.warning(f"Error detecting MIME type: {str(e)}")
    
    # Fallback: use extension
    ext = file_path.suffix.lower().lstrip(".")
    return FORMAT_TO_MIME.get(ext)


def get_format_from_mime(mime_type: str) -> Optional[str]:
    """Get the format name from a MIME type.
    
    Args:
        mime_type: MIME type string.
    
    Returns:
        Format name, or None if the MIME type is unknown.
    """
    return MIME_TO_FORMAT.get(mime_type)


def get_format_from_extension(extension: str) -> Optional[str]:
    """Get the format name from a file extension.
    
    Args:
        extension: File extension (with or without leading dot).
    
    Returns:
        Format name, or None if the extension is unknown.
    """
    # Remove leading dot if present
    ext = extension.lower().lstrip(".")
    
    # Direct lookup for common formats
    if ext in FORMAT_TO_MIME:
        return ext
    
    # Try to determine from MIME type
    mime_type, _ = mimetypes.guess_type(f"file.{ext}")
    if mime_type:
        return get_format_from_mime(mime_type)
    
    return None


def get_common_formats() -> Dict[str, List[str]]:
    """Get a dictionary of common file formats grouped by category.
    
    Returns:
        Dictionary mapping category names to lists of format names.
    """
    return {
        "document": sorted(DOCUMENT_FORMATS),
        "spreadsheet": sorted(SPREADSHEET_FORMATS),
        "image": sorted(IMAGE_FORMATS),
        "data_exchange": sorted(DATA_EXCHANGE_FORMATS),
        "archive": sorted(ARCHIVE_FORMATS),
        "font": sorted(FONT_FORMATS),
        "pdf": sorted(PDF_FORMATS),
    }


def get_extensions_for_format(format_name: str) -> List[str]:
    """Get the common file extensions for a format.
    
    Args:
        format_name: Name of the format (e.g., "pdf", "xlsx").
    
    Returns:
        List of file extensions (without the dot).
    """
    format_lower = format_name.lower()
    
    # Special cases
    if format_lower == "jpeg":
        return ["jpg", "jpeg"]
    elif format_lower == "tiff":
        return ["tif", "tiff"]
    elif format_lower == "html":
        return ["html", "htm"]
    elif format_lower == "yaml":
        return ["yaml", "yml"]
    
    # Default case: format name is the extension
    return [format_lower]
