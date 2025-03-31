### 4. README.md

```markdown
# FileConverter

A comprehensive file conversion utility designed for IT administrators at TSG Fulfillment. This tool provides a robust and extensible framework for converting files between different formats, with support for a wide range of file types.

## Features

- **Comprehensive Format Support**: Convert between various document, spreadsheet, image, data exchange, and archive formats
- **Batch Processing**: Convert multiple files in a single operation
- **Custom Conversion Pipelines**: Create and save custom conversion workflows
- **Both CLI and GUI Interfaces**: Use command-line for automation or GUI for interactive usage
- **Extensible Architecture**: Easily add support for new file formats
- **Error Handling**: Robust error handling with detailed logging
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Python 3.12 Compatible**: Leverages the latest Python features for improved performance and reliability

## Installation

### From PyPI (Recommended)

```bash
pip install fileconverter
```

### From Source

```bash
git clone https://github.com/tsgfulfillment/fileconverter.git
cd fileconverter
pip install -e .
```

For development installation with additional tools:

```bash
pip install -e ".[dev]"
```

For GUI support:

```bash
pip install -e ".[gui]"
```

## Usage

### Command Line Interface

Basic usage:

```bash
fileconverter convert input.docx output.pdf
```

Convert multiple files:

```bash
fileconverter batch *.csv --output-dir ./json_files/ --output-format json
```

Get help:

```bash
fileconverter --help
fileconverter convert --help
```

### GUI Interface

Launch the graphical interface:

```bash
fileconverter-gui
```

## Supported Formats

### Document Formats
- Microsoft Word (.doc, .docx)
- PDF (.pdf)
- Rich Text Format (.rtf)
- Markdown (.md)
- HTML (.html, .htm)
- Plain Text (.txt)

### Spreadsheet Formats
- Microsoft Excel (.xls, .xlsx)
- CSV (.csv)
- TSV (.tsv)
- OpenDocument Spreadsheet (.ods)

### Image Formats
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- GIF (.gif)
- TIFF (.tiff, .tif)
- WebP (.webp)

### Data Exchange Formats
- JSON (.json)
- XML (.xml)
- YAML (.yaml, .yml)
- INI (.ini)
- TOML (.toml)

### Archive Formats
- ZIP (.zip)
- TAR (.tar)
- GZIP (.gz)
- 7Z (.7z)

## Configuration

Configuration can be specified via command-line arguments, configuration files, or environment variables.

Default configuration file locations:
- System-wide: `/etc/fileconverter/config.yaml`
- User-specific: `~/.config/fileconverter/config.yaml`
- Project-specific: `./fileconverter.yaml`

## Development

### Adding New Converters

To add support for a new file format, create a new module in the `fileconverter/converters` directory.

### Testing

Run the test suite:

```bash
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
```

