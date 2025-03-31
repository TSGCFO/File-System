# Supported Formats in FileConverter

This document provides a comprehensive list of all file formats supported by FileConverter, along with their extensions, descriptions, and conversion capabilities.

## Table of Contents

- [Document Formats](#document-formats)
- [Spreadsheet Formats](#spreadsheet-formats)
- [Image Formats](#image-formats)
- [Data Exchange Formats](#data-exchange-formats)
- [Archive Formats](#archive-formats)
- [Font Formats](#font-formats)
- [Database Formats](#database-formats)
- [Conversion Matrix](#conversion-matrix)
- [Format Detection](#format-detection)
- [Adding New Formats](#adding-new-formats)

## Document Formats

| Format | Extensions | Description | Input | Output |
|--------|------------|-------------|:-----:|:------:|
| Microsoft Word Document (Binary) | .doc | Legacy binary format for Microsoft Word documents | ✓ | ✗ |
| Microsoft Word Document (Open XML) | .docx | Modern XML-based format for Microsoft Word documents | ✓ | ✓ |
| Rich Text Format | .rtf | Cross-platform document format that preserves formatting | ✓ | ✗ |
| OpenDocument Text | .odt | Open standard document format | ✓ | ✗ |
| Portable Document Format | .pdf | Fixed-layout document format | ✓ | ✓ |
| Plain Text | .txt | Unformatted text files | ✓ | ✓ |
| HTML Document | .html, .htm | HyperText Markup Language for web pages | ✓ | ✓ |
| Markdown | .md, .markdown | Lightweight markup language | ✓ | ✓ |

### Document Format Details

#### Microsoft Word Document (.doc, .docx)

Word documents are widely used for text documents with formatting. FileConverter supports:

- Converting .doc to .docx (requires LibreOffice)
- Converting .docx to .pdf, .html, .txt
- Preserving most formatting during conversion
- Custom templates for .docx output

#### PDF (.pdf)

Portable Document Format is designed for fixed-layout documents. FileConverter supports:

- Converting documents to PDF
- Converting PDF to text or HTML
- Customizing PDF output (page size, orientation, margins)
- PDF compression levels

#### Markdown (.md)

Markdown is a lightweight markup language. FileConverter supports:

- Converting Markdown to HTML or PDF
- Applying custom CSS for styling
- Converting HTML to Markdown
- Supporting common Markdown extensions (tables, code blocks, etc.)

## Spreadsheet Formats

| Format | Extensions | Description | Input | Output |
|--------|------------|-------------|:-----:|:------:|
| Microsoft Excel (Binary) | .xls | Legacy binary format for Excel spreadsheets | ✓ | ✗ |
| Microsoft Excel (Open XML) | .xlsx | Modern XML-based format for Excel spreadsheets | ✓ | ✓ |
| Comma-Separated Values | .csv | Text format for tabular data with comma delimiters | ✓ | ✓ |
| Tab-Separated Values | .tsv | Text format for tabular data with tab delimiters | ✓ | ✓ |
| OpenDocument Spreadsheet | .ods | Open standard spreadsheet format | ✓ | ✗ |
| JSON (tabular) | .json | JSON representation of tabular data | ✓ | ✓ |

### Spreadsheet Format Details

#### Microsoft Excel (.xls, .xlsx)

Excel spreadsheets are used for tabular data with calculations. FileConverter supports:

- Converting .xls to .xlsx (requires appropriate libraries)
- Converting .xlsx to .csv, .json, .html
- Preserving formulas when converting between spreadsheet formats
- Customizing output format (date formats, number formats)

#### CSV and TSV (.csv, .tsv)

CSV and TSV files are simple text formats for tabular data. FileConverter supports:

- Converting between CSV and other spreadsheet formats
- Customizing delimiters, quotes, and encoding
- Handling headers and data types
- Multi-sheet Excel to multiple CSV files

## Image Formats

| Format | Extensions | Description | Input | Output |
|--------|------------|-------------|:-----:|:------:|
| JPEG | .jpg, .jpeg | Lossy compression format for photographs | ✓ | ✓ |
| PNG | .png | Lossless compression with transparency | ✓ | ✓ |
| BMP | .bmp | Uncompressed bitmap format | ✓ | ✓ |
| GIF | .gif | Format for simple animations and images with limited colors | ✓ | ✓ |
| TIFF | .tiff, .tif | Flexible format for high-quality images | ✓ | ✓ |
| WebP | .webp | Modern format with efficient compression | ✓ | ✓ |
| SVG | .svg | Scalable Vector Graphics format | ✓ | ✓ |

### Image Format Details

#### JPEG (.jpg, .jpeg)

JPEG is a lossy compression format ideal for photographs. FileConverter supports:

- Converting images to JPEG with customizable quality
- Progressive JPEG option
- Metadata preservation options
- Color profile management

#### PNG (.png)

PNG is a lossless format that supports transparency. FileConverter supports:

- Converting images to PNG with various compression levels
- Transparency preservation
- Color depth options (8-bit, 24-bit, etc.)
- Metadata handling

#### WebP (.webp)

WebP is a modern format with efficient compression. FileConverter supports:

- Converting to WebP with lossy or lossless compression
- Animation support
- Transparency
- Quality settings

## Data Exchange Formats

| Format | Extensions | Description | Input | Output |
|--------|------------|-------------|:-----:|:------:|
| JSON | .json | JavaScript Object Notation | ✓ | ✓ |
| XML | .xml | Extensible Markup Language | ✓ | ✓ |
| YAML | .yaml, .yml | Human-readable data serialization format | ✓ | ✓ |
| INI | .ini | Simple configuration file format | ✓ | ✓ |
| TOML | .toml | Tom's Obvious Minimal Language for configuration | ✓ | ✓ |

### Data Exchange Format Details

#### JSON (.json)

JSON is a lightweight data interchange format. FileConverter supports:

- Converting between JSON and other data formats
- Pretty printing with customizable indentation
- Schema validation
- Various encoding options

#### XML (.xml)

XML is a flexible markup language. FileConverter supports:

- Converting between XML and other data formats
- Preserving or modifying structure
- XSLT transformations
- Namespace handling

## Archive Formats

| Format | Extensions | Description | Input | Output |
|--------|------------|-------------|:-----:|:------:|
| ZIP | .zip | Compressed archive format | ✓ | ✓ |
| TAR | .tar | Uncompressed archive format | ✓ | ✓ |
| GZIP | .gz | Compression format | ✓ | ✓ |
| 7Z | .7z | High compression archive format | ✓ | ✓ |
| RAR | .rar | Proprietary archive format | ✓ | ✗ |

### Archive Format Details

#### ZIP (.zip)

ZIP is a widely used archive format. FileConverter supports:

- Creating ZIP archives from files and directories
- Extracting ZIP archives
- Password protection (extraction only)
- Compression level customization

#### 7Z (.7z)

7Z offers high compression ratios. FileConverter supports:

- Creating 7Z archives with various compression methods
- Extracting 7Z archives
- Solid compression options
- Password handling

## Font Formats

| Format | Extensions | Description | Input | Output |
|--------|------------|-------------|:-----:|:------:|
| TrueType | .ttf | Common font format | ✓ | ✗ |
| OpenType | .otf | Advanced font format | ✓ | ✗ |
| Web Open Font Format | .woff | Compressed font for web use | ✓ | ✓ |
| WOFF2 | .woff2 | Improved compression for web fonts | ✓ | ✓ |

### Font Format Details

Font conversion capabilities include:

- Converting between web font formats
- Subsetting fonts to reduce size
- Metadata extraction and modification
- Format conversion for web optimization

## Database Formats

| Format | Extensions | Description | Input | Output |
|--------|------------|-------------|:-----:|:------:|
| SQLite | .db, .sqlite | Self-contained database file | ✓ | ✓ |
| CSV export/import | .csv | For database table import/export | ✓ | ✓ |

## Conversion Matrix

The following matrix shows which conversions are supported between different format categories:

| From / To | Document | Spreadsheet | Image | Data Exchange | Archive | Font |
|-----------|:--------:|:-----------:|:-----:|:-------------:|:-------:|:----:|
| Document | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ |
| Spreadsheet | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ |
| Image | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ |
| Data Exchange | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ |
| Archive | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| Font | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |

For a detailed list of specific format-to-format conversions, use the command:

```bash
fileconverter list-formats
```

## Format Detection

FileConverter uses several methods to detect file formats:

1. **File Extension**: The primary method is based on the file extension.

2. **Content Analysis**: For some formats, the file content is analyzed to determine the actual format.

3. **Magic Numbers**: Binary file formats are identified by their magic numbers (signature bytes).

4. **Encoding Detection**: For text-based formats, encoding is automatically detected.

When the format cannot be determined automatically, you can specify it explicitly:

```bash
fileconverter convert input.file output.xlsx --input-format csv
```

## Adding New Formats

To add support for new formats, see the [Adding Converters](./adding_converters.md) guide.

This involves:

1. Creating a new converter class that inherits from `BaseConverter`
2. Implementing the required methods
3. Registering input and output formats
4. Implementing the conversion logic

FileConverter is designed to be easily extensible with new format support.