# Supported Formats

FileConverter supports conversion between a wide range of file formats, organized into the following categories:

## Document Formats

- **Microsoft Word (.doc, .docx)** - Proprietary document formats by Microsoft
- **Rich Text Format (.rtf)** - Cross-platform document format
- **OpenDocument Text (.odt)** - Open standard document format
- **PDF (.pdf)** - Portable Document Format for fixed-layout documents
- **Plain Text (.txt)** - Unformatted text files
- **HTML (.html, .htm)** - HyperText Markup Language for web pages
- **Markdown (.md)** - Lightweight markup language

## Spreadsheet Formats

- **Microsoft Excel (.xls, .xlsx)** - Proprietary spreadsheet formats by Microsoft
- **CSV (.csv)** - Comma-Separated Values format for tabular data
- **TSV (.tsv)** - Tab-Separated Values format for tabular data
- **JSON (.json)** - JavaScript Object Notation for structured data
- **XML (.xml)** - eXtensible Markup Language for structured data
- **HTML (.html)** - HTML table representation of tabular data

## Data Exchange Formats

- **JSON (.json)** - JavaScript Object Notation for structured data
- **XML (.xml)** - eXtensible Markup Language for structured data
- **YAML (.yaml, .yml)** - YAML Ain't Markup Language for human-readable data serialization
- **INI (.ini, .conf, .cfg)** - Configuration file format
- **TOML (.toml)** - Tom's Obvious, Minimal Language for configuration files
- **CSV (.csv)** - Comma-Separated Values format for tabular data
- **TSV (.tsv)** - Tab-Separated Values format for tabular data

## Image Formats

- **JPEG (.jpg, .jpeg)** - Joint Photographic Experts Group format for lossy compressed images
- **PNG (.png)** - Portable Network Graphics format for lossless compressed images
- **GIF (.gif)** - Graphics Interchange Format for simple animations
- **BMP (.bmp)** - Bitmap image format for uncompressed images
- **TIFF (.tif, .tiff)** - Tagged Image File Format for high-quality images
- **WebP (.webp)** - Modern image format by Google with better compression

## Archive Formats

- **ZIP (.zip)** - Common archive format with compression
- **TAR (.tar)** - Tape Archive format without compression
- **GZ (.gz)** - Gzip compressed files
- **7Z (.7z)** - 7-Zip archive format with high compression ratio

## Database Formats

- **SQLite (.sqlite, .db)** - Self-contained, serverless, zero-configuration database
- **CSV (.csv)** - Comma-Separated Values for tabular data export/import
- **JSON (.json)** - JavaScript Object Notation for structured data export/import
- **XML (.xml)** - eXtensible Markup Language for structured data export/import

## Font Formats

- **TrueType (.ttf)** - Font format developed by Apple and Microsoft
- **OpenType (.otf)** - Font format based on TrueType
- **WOFF (.woff)** - Web Open Font Format for web use
- **WOFF2 (.woff2)** - Web Open Font Format 2 with better compression

## Cross-Domain Conversions

FileConverter now supports comprehensive conversions between all non-image formats. This means you can convert:

- Any document format to any spreadsheet or data exchange format
- Any spreadsheet format to any document or data exchange format  
- Any data exchange format to any document or spreadsheet format

These cross-domain conversions enable powerful workflows such as:

- Converting XLSX spreadsheets directly to PDF or DOCX documents
- Transforming JSON or XML data into formatted documents
- Converting document formats to structured data formats for analysis or processing
- Creating data visualizations from various source formats

## Conversion Quality

The quality and fidelity of conversions can vary depending on the specific formats involved:

- **Direct Conversions**: Conversions between similar formats (e.g., DOCX to PDF) typically preserve most formatting and structure.
- **Cross-Domain Conversions**: When converting between different domain types (e.g., JSON to DOCX), the system creates appropriate representations based on the data structure.
- **Complex Conversions**: Highly formatted documents converted to data formats will preserve content but may lose some formatting.

## Dependency Requirements

Some conversions require additional dependencies:

- **Document Conversions**: May require `python-docx`, `pypdf`, `markdown`, `weasyprint` or `pdfkit`
- **Spreadsheet Conversions**: Require `pandas` and optional `openpyxl` for Excel support
- **Data Exchange Conversions**: May require `pyyaml`, `toml`, `dicttoxml`, or `xmltodict`
- **Image Conversions**: Require `Pillow` and optional format-specific libraries

See the [installation documentation](installation.md) for details on installing required dependencies.