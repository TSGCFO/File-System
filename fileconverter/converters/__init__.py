"""
File format converters for FileConverter.

This package provides converters for various file formats, organized
into modules based on format category (document, spreadsheet, etc.).

Each converter module should define one or more classes that handle
conversion between specific file formats. These classes should inherit
from the BaseConverter class and implement the required methods.

Format Categories:
- archive: Converters for archive formats (zip, tar, etc.)
- data_exchange: Converters for data exchange formats (json, xml, etc.)
- database: Converters for database formats (sqlite, csv, etc.)
- document: Converters for document formats (docx, pdf, etc.)
- font: Converters for font formats (ttf, otf, etc.)
- image: Converters for image formats (jpg, png, etc.)
- pdf: Converters for PDF-specific operations
- spreadsheet: Converters for spreadsheet formats (xlsx, csv, etc.)
- text_markup: Converters for text and markup formats (markdown, html, etc.)
"""

# Import base converter class
from fileconverter.core.registry import BaseConverter

# Define format categories
FORMAT_CATEGORIES = [
    "archive",
    "data_exchange",
    "database",
    "document",
    "font",
    "image",
    "pdf",
    "spreadsheet",
    "text_markup",
]

# Import converter modules to register them
from fileconverter.converters import (
    document,
    spreadsheet,
    image,
    data_exchange,
    archive,
    pdf,
    database,
    font,
    text_markup
)

__all__ = [
    "BaseConverter",
    "FORMAT_CATEGORIES",
    "document",
    "spreadsheet",
    "image",
    "data_exchange",
    "archive",
    "pdf",
    "database",
    "font",
    "text_markup"
]