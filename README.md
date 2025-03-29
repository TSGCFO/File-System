# Universal File Format Converter

A comprehensive Python utility for converting files between various formats across multiple categories.

## Features

- Supports conversions across 9 different file format categories
- Modular architecture for easy extension with new converters
- Command-line interface with helpful options
- Detailed logging and error reporting
- Automatic dependency checking

## File Format Categories

1. **Document formats**: doc, docx, odt, rtf, txt, html, md, pdf
2. **Spreadsheet formats**: xls, xlsx, ods, csv, tsv
3. **Image formats**: jpg, jpeg, png, gif, bmp, tiff, tif, webp, svg
4. **Archive formats**: zip, tar, gz, bz2, 7z, rar
5. **Database formats**: sql, sqlite, db, json, xml, csv
6. **Text and markup formats**: txt, html, xml, json, yaml, yml, md, rst
7. **Data exchange formats**: json, xml, yaml, yml, csv, toml, pb
8. **Font formats**: ttf, otf, woff, woff2, eot
9. **PDF, XPS, and similar formats**: pdf, xps, djvu, epub

## Installation

### Prerequisites

- Python 3.6 or higher

### Basic Setup

1. Clone or download this repository:
   ```bash
   git clone https://github.com/tsg-fulfillment/format-converter.git
   cd format-converter
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Dependencies

The script uses various Python libraries for different format conversions. Install them as needed:

```bash
# Basic dependencies
pip install Pillow python-docx openpyxl PyPDF2 PyYAML lxml markdown chardet

# Optional dependencies for additional formats
pip install html2text toml reportlab
```

## Usage

### Basic Usage

Convert a file from one format to another:

```bash
python format_converter.py input_file output_file
```

Example:
```bash
python format_converter.py document.docx document.pdf
```

### Command-line Options

```
usage: format_converter.py [-h] [--force] [--list-formats] [--list-categories] [--verbose] [--check-deps] [input] [output]

Convert files between different formats.

positional arguments:
  input                 Input file path
  output                Output file path

optional arguments:
  -h, --help            show this help message and exit
  --force, -f           Force overwrite of existing output file
  --list-formats, -l    List supported formats and exit
  --list-categories, -c List format categories and exit
  --verbose, -v         Enable verbose output
  --check-deps, -d      Check dependencies and exit
```

### Examples

1. Convert a DOCX document to PDF:
   ```bash
   python format_converter.py document.docx document.pdf
   ```

2. Convert a JSON file to XML:
   ```bash
   python format_converter.py data.json data.xml
   ```

3. Convert a PNG image to JPEG:
   ```bash
   python format_converter.py image.png image.jpg
   ```

4. List all supported formats:
   ```bash
   python format_converter.py --list-formats
   ```

5. Check dependencies:
   ```bash
   python format_converter.py --check-deps
   ```

## Extending the Converter

You can easily add your own converters to support additional formats or improve existing conversions.

### Creating a Custom Converter Module

1. Create a new Python file in the `converters` directory:
   ```bash
   touch converters/my_custom_converters.py
   ```

2. Implement your converter functions and register them:
   ```python
   """
   My Custom Converters
   """
   import logging
   from format_converter import register_converter

   logger = logging.getLogger(__name__)

   def my_format_to_target(input_path, output_path):
       """Convert my_format to target_format."""
       try:
           # Conversion logic here
           logger.info(f"Converted {input_path} to {output_path}")
       except Exception as e:
           logger.error(f"Error converting: {str(e)}")
           raise

   # Register the converter
   register_converter('my_format', 'target_format', my_format_to_target)
   ```

3. Your converter will be automatically discovered and loaded when the script runs.

## Limitations

- Some conversions may require external dependencies
- Quality of conversion depends on the libraries used
- Some formats may have limited feature support
- Large files may require significant memory

## Troubleshooting

If you encounter issues:

1. Run with verbose logging:
   ```bash
   python format_converter.py input_file output_file --verbose
   ```

2. Check dependencies:
   ```bash
   python format_converter.py --check-deps
   ```

3. Make sure the input file exists and is in the expected format

4. Check that you have permission to write to the output location

## License

This tool is developed for internal use at TSG Fulfillment.
