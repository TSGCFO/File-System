# FileConverter Usage Guide

This document provides detailed instructions for using FileConverter, including command-line operations, GUI usage, and advanced features like custom conversion pipelines.

## Table of Contents

- [Installation](#installation)
- [Command Line Interface](#command-line-interface)
  - [Basic Conversion](#basic-conversion)
  - [Conversion with Parameters](#conversion-with-parameters)
  - [Batch Conversion](#batch-conversion)
  - [Format Information](#format-information)
  - [Help and Documentation](#help-and-documentation)
- [Graphical User Interface](#graphical-user-interface)
  - [Launching the GUI](#launching-the-gui)
  - [Single File Conversion](#single-file-conversion)
  - [Batch Processing](#batch-processing)
  - [Customizing Conversion Parameters](#customizing-conversion-parameters)
  - [Managing Conversion History](#managing-conversion-history)
  - [GUI Settings](#gui-settings)
- [Advanced Usage](#advanced-usage)
  - [Custom Conversion Pipelines](#custom-conversion-pipelines)
  - [Conversion Parameters by Format](#conversion-parameters-by-format)
  - [Working with Configuration](#working-with-configuration)
  - [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
  - [Logging and Debugging](#logging-and-debugging)
  - [Getting Help](#getting-help)

## Installation

### From PyPI (Recommended)

The easiest way to install FileConverter is via pip:

```bash
# Basic installation
pip install fileconverter

# With GUI support
pip install fileconverter[gui]

# With development tools
pip install fileconverter[dev]

# Full installation (all dependencies)
pip install fileconverter[all]
```

### From Source

For the latest development version:

```bash
# Clone the repository
git clone https://github.com/tsgfulfillment/fileconverter.git
cd fileconverter

# Basic installation
pip install -e .

# With GUI support
pip install -e ".[gui]"

# With development tools
pip install -e ".[dev]"

# Full installation (all dependencies)
pip install -e ".[all]"
```

### System Requirements

- Python 3.10 or higher
- For GUI: PyQt6
- Additional dependencies for specific file formats:
  - Document conversion: python-docx, PyPDF2, etc.
  - Image conversion: Pillow, Wand (requires ImageMagick)
  - Spreadsheet conversion: pandas, openpyxl, etc.

## Command Line Interface

FileConverter provides a powerful command-line interface (CLI) that can be used for various conversion tasks, batch processing, and automation.

### Basic Conversion

To convert a single file from one format to another, use the `convert` command:

```bash
fileconverter convert [INPUT_FILE] [OUTPUT_FILE]
```

Examples:

```bash
# Convert a Word document to PDF
fileconverter convert document.docx document.pdf

# Convert a CSV file to Excel
fileconverter convert data.csv data.xlsx

# Convert a PNG image to JPEG
fileconverter convert image.png image.jpg
```

The converter automatically determines the input and output formats based on file extensions.

### Conversion with Parameters

You can specify conversion parameters to customize the output:

```bash
fileconverter convert [INPUT_FILE] [OUTPUT_FILE] --params "param1=value1" --params "param2=value2"
```

Examples:

```bash
# Convert a Word document to PDF with custom margins and orientation
fileconverter convert document.docx document.pdf --params "margin=0.5" --params "orientation=landscape"

# Convert a CSV to Excel with custom delimiter and sheet name
fileconverter convert data.csv data.xlsx --params "delimiter=;" --params "sheet_name=ImportedData"

# Convert a PNG to JPEG with custom quality setting
fileconverter convert image.png image.jpg --params "quality=85" --params "progressive=true"
```

### Batch Conversion

For converting multiple files at once, use the `batch` command:

```bash
fileconverter batch [INPUT_FILES] --output-dir [DIRECTORY] --output-format [FORMAT]
```

Examples:

```bash
# Convert all CSV files in the current directory to Excel
fileconverter batch *.csv --output-dir ./excel_files/ --output-format xlsx

# Convert all images in a directory to JPEG
fileconverter batch "images/*.png" --output-dir ./jpeg_images/ --output-format jpg

# Convert all documents with parameters
fileconverter batch "docs/*.docx" --output-dir ./pdf_files/ --output-format pdf --params "margin=0.5"
```

You can use the `--recursive` flag to process files in subdirectories:

```bash
fileconverter batch "documents/**/*.doc" --output-dir ./converted/ --output-format docx --recursive
```

### Format Information

To see which formats are supported, use the `list-formats` command:

```bash
# List all supported formats
fileconverter list-formats

# List formats in a specific category
fileconverter list-formats --category document
```

This command displays the supported formats along with their file extensions.

### Help and Documentation

For help with any command, use the `--help` option:

```bash
# General help
fileconverter --help

# Help for a specific command
fileconverter convert --help
fileconverter batch --help
```

## Graphical User Interface

FileConverter includes a user-friendly graphical interface for those who prefer visual interaction.

### Launching the GUI

To start the graphical interface:

```bash
# Using the dedicated command
fileconverter-gui

# Or using the main command with --gui flag
fileconverter --gui
```

### Single File Conversion

1. **Open the FileConverter GUI**
2. **Add a file for conversion:**
   - Click the "Add File" button, or
   - Drag and drop a file onto the application window
3. **Select the output format** from the dropdown menu
4. **Choose the output location:**
   - By default, the output file will be saved in the same directory as the input file
   - Click "Browse" to select a different output location
5. **Configure conversion parameters** (optional):
   - Click the "Parameters" button to open the parameters dialog
   - Adjust parameters specific to the selected output format
6. **Click "Convert"** to start the conversion
7. **Monitor progress** in the status bar
8. **Access the converted file:**
   - A notification will appear when the conversion is complete
   - Click "Open" to view the converted file, or
   - Click "Open Folder" to open the containing directory

### Batch Processing

1. **Open the FileConverter GUI**
2. **Switch to the "Batch" tab**
3. **Add files for conversion:**
   - Click "Add Files" to select multiple files, or
   - Drag and drop multiple files onto the batch list
4. **Select the output format** from the dropdown menu
5. **Choose the output directory** where all converted files will be saved
6. **Configure conversion parameters** (optional):
   - Click "Parameters" to set parameters that will apply to all conversions
7. **Click "Start Batch"** to begin the batch conversion
8. **Monitor progress:**
   - The batch progress bar shows overall progress
   - Individual file progress is shown in the status column
9. **Review results:**
   - Successful conversions are marked with a green checkmark
   - Failed conversions are marked with a red X
   - Click on any file to see detailed information

### Customizing Conversion Parameters

Different file formats support different conversion parameters. When you click the "Parameters" button, a dialog appears with format-specific options:

For PDF output:
- Page size (A4, Letter, etc.)
- Orientation (portrait or landscape)
- Margins (in inches)
- Compression level

For image output:
- Quality (for lossy formats like JPEG)
- Resolution (DPI)
- Color mode (RGB, CMYK, grayscale)
- Compression options

For spreadsheet output:
- Sheet name
- Header options
- Delimiter (for CSV) - Now with an improved dropdown selection for common delimiters:
  - Comma (,)
  - Semicolon (;)
  - Tab (\\t)
  - Pipe (|)
  - Space ( )
- Cell formatting options

### Cross-Format Conversion

FileConverter now supports automatic multi-step conversion for formats that don't have direct converters. For example, you can convert from Format A to Format C even if there's no direct converter, as long as there's a path through Format B (A → B → C).

The system automatically:
1. Identifies the optimal conversion path with the fewest steps
2. Creates necessary temporary files for intermediate conversions
3. Chains the conversions together seamlessly
4. Cleans up the intermediate files when complete

This feature works transparently in both the GUI and command-line interfaces without requiring any special syntax.

### Cross-Domain Conversion

FileConverter now supports enhanced cross-domain conversions between document, spreadsheet, and data exchange formats. This powerful feature allows you to seamlessly convert between different domains:

#### Document to Data Exchange Examples:

```bash
# Convert a Word document to JSON
fileconverter convert report.docx data.json

# Convert a Markdown file to YAML
fileconverter convert documentation.md config.yaml

# Convert HTML to XML
fileconverter convert webpage.html data.xml

# Convert a PDF to JSON with extraction parameters
fileconverter convert financial-report.pdf financial-data.json --params "structure=table" --params "extract_tables=true"
```

#### Data Exchange to Document Examples:

```bash
# Convert JSON to a formatted PDF
fileconverter convert api-response.json report.pdf --params "template=report-template.html"

# Convert YAML to Markdown
fileconverter convert configuration.yaml documentation.md

# Convert XML to DOCX with styling
fileconverter convert data-feed.xml report.docx --params "style=Corporate"

# Convert structured data to HTML with custom CSS
fileconverter convert product-data.json product-catalog.html --params "css=catalog-style.css"
```

#### Spreadsheet to Document Examples:

```bash
# Convert Excel spreadsheet to PDF with specific layout
fileconverter convert financial-data.xlsx financial-report.pdf --params "orientation=landscape" --params "page_size=A3"

# Convert CSV to HTML report
fileconverter convert monthly-sales.csv sales-report.html --params "template=sales-template.html"
```

#### Document to Spreadsheet Examples:

```bash
# Extract tables from PDF to Excel
fileconverter convert annual-report.pdf financial-data.xlsx --params "extract_tables=true"

# Convert structured Markdown to CSV
fileconverter convert product-list.md products.csv
```

#### Use Cases for Cross-Domain Conversion:

1. **Data Extraction**: Extract structured data from documents for analysis or processing
2. **Report Generation**: Convert data files (JSON, XML, CSV) into formatted documents for presentation
3. **Content Migration**: Move content between different systems that require different formats
4. **API Integration**: Process API responses (JSON/XML) into human-readable documents
5. **Document Archiving**: Convert documents to structured data formats for long-term storage
6. **Content Transformation**: Transform content for different audiences and consumption methods

The system intelligently maps content between domains, preserving structure and formatting where appropriate. For document-to-data conversions, tables, lists, and structured content are mapped to appropriate data structures. For data-to-document conversions, JSON objects and arrays are represented as formatted sections, tables, or lists.

### Managing Conversion History

The GUI keeps track of your recent conversions:

1. **Access history:** Click the "History" button or navigate to the "History" tab
2. **View past conversions:**
   - See input and output files, formats, and conversion dates
   - Sort by any column by clicking the column header
3. **Repeat a conversion:**
   - Select an item in the history
   - Click "Repeat" to set up the same conversion with the same parameters
4. **Clear history:**
   - Click "Clear History" to remove all historical entries, or
   - Right-click an entry and select "Remove" to delete just that entry

### GUI Settings

Customize the GUI behavior through the Settings dialog:

1. **Open Settings:** Click the gear icon or select "Settings" from the menu
2. **General settings:**
   - Theme (light, dark, or system)
   - Language
   - Default output directory
   - History retention
3. **Conversion settings:**
   - Default parameters for each format
   - Temporary file handling
   - Error handling behavior
4. **Advanced settings:**
   - Log level and log file location
   - Maximum file size
   - Number of parallel processes for batch conversion

## Advanced Usage

### Custom Conversion Pipelines

For complex conversions that require multiple steps, you can define custom conversion pipelines:

```bash
# Using a pipeline configuration file to convert from Markdown to PDF via HTML with custom styling
fileconverter pipeline --config pipeline.yaml input.docx output.pdf
```

Example pipeline.yaml:
```yaml
stages:
  - format: html
    parameters:
      css: style.css
  - format: pdf
    parameters:
      margin: 1.0
      orientation: landscape
```

This pipeline first converts the input file to HTML with a custom CSS file, then converts the HTML to PDF with specific margin and orientation settings. This approach is particularly useful for complex cross-domain conversions that benefit from customization at each step.

You can also create pipelines programmatically:

```python
from fileconverter import ConversionEngine, Pipeline

engine = ConversionEngine()
pipeline = Pipeline(engine)

# Add conversion stages
pipeline.add_stage("html", {"css": "style.css"})
pipeline.add_stage("pdf", {"margin": 1.0, "orientation": "landscape"})

# Execute the pipeline
result = pipeline.execute("input.docx", "output.pdf")
```

### Conversion Parameters by Format

Each format supports specific parameters:

#### Document Formats:

**PDF output parameters:**
- `page_size`: Page size (e.g., "A4", "Letter")
- `orientation`: Page orientation ("portrait", "landscape")
- `margin`: Page margin in inches
- `compression`: PDF compression level ("none", "low", "normal", "high")

**HTML output parameters:**
- `css`: CSS file path or CSS content
- `template`: HTML template file path
- `title`: Document title

**DOCX output parameters:**
- `template`: Template file path
- `style`: Style to apply

#### Spreadsheet Formats:

**CSV output parameters:**
- `delimiter`: Field delimiter character
- `quotechar`: Character used to quote fields
- `encoding`: Text encoding

**XLSX output parameters:**
- `sheet_name`: Name of the sheet
- `date_format`: Format for date values

#### Image Formats:

**JPEG output parameters:**
- `quality`: Image quality (1-100)
- `progressive`: Whether to create a progressive JPEG
- `optimize`: Whether to optimize the output file

**PNG output parameters:**
- `compression`: Compression level (0-9)
- `transparent`: Whether to preserve transparency

### Working with Configuration

FileConverter uses a comprehensive configuration system with multiple layers, each with its own precedence:

1. **Default configuration:** Built-in defaults hardcoded in the application
2. **System configuration:** `/etc/fileconverter/config.yaml` (system-wide settings)
3. **User configuration:** `~/.config/fileconverter/config.yaml` (user-specific settings)
4. **Project configuration:** `./fileconverter.yaml` (project-specific settings)
5. **Custom configuration:** Path specified with `--config` option (explicit settings file)
6. **Environment variables:** Variables with `FILECONVERTER_` prefix
7. **Command-line arguments:** Highest precedence (overrides all other settings)

The configuration system automatically merges settings from these different sources, with later sources taking precedence over earlier ones. This allows for flexible configuration that can be tailored to system, user, and project needs.

#### Creating a Configuration File

You can create a default configuration file with recommended settings using the GUI (Settings → Export Configuration) or with the following command:

```bash
fileconverter config --create-default ~/fileconverter.yaml
```

#### Example Configuration File

```yaml
general:
  # Directory for temporary files (null for system default)
  temp_dir: null
  
  # Maximum file size in MB that can be converted
  max_file_size_mb: 200
  
  # Whether to preserve temporary files after conversion (for debugging)
  preserve_temp_files: false

logging:
  # Logging level: DEBUG, INFO, WARNING, ERROR, or CRITICAL
  level: INFO
  
  # Log file path (null for console only)
  file: fileconverter.log
  
  # Log message format
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

converters:
  document:
    # Whether the document converter is enabled
    enabled: true
    
    # PDF output settings
    pdf:
      # Resolution in DPI
      resolution: 300
      
      # Compression level: none, low, medium, high
      compression: medium
  
  spreadsheet:
    # Whether the spreadsheet converter is enabled
    enabled: true
    
    # Excel output settings
    excel:
      # Date format for Excel files
      date_format: "YYYY-MM-DD"
    
    # CSV output settings
    csv:
      # Field delimiter (comma, semicolon, tab, etc.)
      delimiter: ","
      
      # Quote character
      quotechar: "\""
      
      # Text encoding
      encoding: "utf-8"
  
  image:
    # Whether the image converter is enabled
    enabled: true
    
    # JPEG output settings
    jpeg:
      # Quality (1-100)
      quality: 85
      
      # Whether to use progressive rendering
      progressive: true

gui:
  # Theme: system, light, dark
  theme: system
  
  # Maximum number of recent files to remember
  recent_files_limit: 10
  
  # Whether to show tooltips
  show_tooltips: true
```

### Environment Variables

You can configure FileConverter using environment variables:

```bash
# Set maximum file size to 500MB
export FILECONVERTER_GENERAL_MAX_FILE_SIZE_MB=500

# Set logging level to DEBUG
export FILECONVERTER_LOGGING_LEVEL=DEBUG

# Disable document converters
export FILECONVERTER_CONVERTERS_DOCUMENT_ENABLED=false

# Set default JPEG quality to 90
export FILECONVERTER_CONVERTERS_IMAGE_JPEG_QUALITY=90
```

## Troubleshooting

### Common Issues

#### Missing Dependencies

If you see an error about missing dependencies:

```
Failed to convert DOCX to PDF: No module named 'docx2pdf'.
Please install python-docx-pdf or LibreOffice.
```

Install the required dependency:

```bash
pip install docx2pdf
```

Or for system-level dependencies:

```bash
# Ubuntu/Debian
sudo apt-get install libreoffice-common

# macOS
brew install libreoffice

# Windows
# Install LibreOffice from https://www.libreoffice.org/download/
```

#### File Size Limits

By default, FileConverter limits file sizes to 100MB. For larger files:

```bash
# Command-line option
fileconverter convert large_file.docx output.pdf --max-file-size 500

# Environment variable
export FILECONVERTER_GENERAL_MAX_FILE_SIZE_MB=500

# Configuration file
# In fileconverter.yaml:
general:
  max_file_size_mb: 500
```

#### Unsupported Formats

If you see an error about unsupported formats:

```
Unsupported input format: xyz
```

Check the list of supported formats:

```bash
fileconverter list-formats
```

### Logging and Debugging

FileConverter provides detailed logging to help diagnose issues:

```bash
# Enable verbose output
fileconverter -v convert input.docx output.pdf

# Enable debug logging
fileconverter -vv convert input.docx output.pdf

# Save logs to a file
fileconverter --log-file debug.log -vv convert input.docx output.pdf
```

The log file includes information about:
- Input and output file paths
- Detected formats
- Selected converter
- Conversion parameters
- Detailed error messages

### Getting Help

If you encounter issues not covered in this documentation:

1. Check the [Troubleshooting Guide](./troubleshooting.md) for common issues and solutions
2. Search for similar issues in the [GitHub Issues](https://github.com/tsgfulfillment/fileconverter/issues)
3. Create a new issue with:
   - FileConverter version
   - Operating system and Python version
   - Detailed description of the problem
   - Steps to reproduce
   - Relevant logs or error messages

For general questions, use the [Discussions](https://github.com/tsgfulfillment/fileconverter/discussions) tab on GitHub.