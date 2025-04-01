# FileConverter Troubleshooting Guide

This guide provides solutions to common issues you may encounter when using FileConverter.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Conversion Errors](#conversion-errors)
- [Format-Specific Problems](#format-specific-problems)
- [Performance Issues](#performance-issues)
- [GUI Problems](#gui-problems)
- [CLI Problems](#cli-problems)
- [Configuration Issues](#configuration-issues)
- [Dependency Problems](#dependency-problems)
- [Logging and Debugging](#logging-and-debugging)
- [Getting Help](#getting-help)

## Installation Issues

### Missing Dependencies

**Problem**: Installation fails with error messages about missing dependencies.

**Solution**:

1. Ensure you have the required Python version (3.10 or higher):
   ```bash
   python --version
   ```

2. Install with specific dependency groups:
   ```bash
   # Basic installation
   pip install fileconverter
   
   # With GUI support
   pip install fileconverter[gui]
   
   # Full installation with all dependencies
   pip install fileconverter[all]
   ```

3. If you encounter issues with binary dependencies, install them at the system level:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install python3-dev libjpeg-dev zlib1g-dev libmagickwand-dev
   
   # macOS
   brew install imagemagick
   
   # Windows
   # Install the appropriate binary packages from official websites
   ```

### Permission Errors

**Problem**: Installation fails due to permission errors.

**Solution**:

1. Use a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install fileconverter
   ```

2. For global installation with user permissions:
   ```bash
   pip install --user fileconverter
   ```

### Package Conflicts

**Problem**: Installation fails due to conflicting packages.

**Solution**:

1. Install in a clean virtual environment:
   ```bash
   python -m venv fresh-env
   source fresh-env/bin/activate
   pip install fileconverter
   ```

2. Specify compatible versions if needed:
   ```bash
   pip install "fileconverter<0.2.0"
   ```

## Conversion Errors

### Unsupported Format

**Problem**: Error message about unsupported input or output format.

**Solution**:

1. Check the list of supported formats:
   ```bash
   fileconverter list-formats
   ```

2. Ensure the file extension matches the actual format.

3. Try specifying the format explicitly if the extension is non-standard:
   ```bash
   fileconverter convert input.file output.pdf --input-format docx
   ```

### Maximum File Size Exceeded

**Problem**: Error message about exceeding maximum file size.

**Solution**:

1. Increase the maximum file size:
   ```bash
   # Command-line option
   fileconverter convert large_file.docx output.pdf --max-file-size 500
   
   # Environment variable
   export FILECONVERTER_GENERAL_MAX_FILE_SIZE_MB=500
   
   # Configuration file (fileconverter.yaml)
   general:
     max_file_size_mb: 500
   ```

2. Split large files into smaller chunks if possible.

### No Converter Found

**Problem**: Error message "No converter found for [format1] to [format2]".

**Solution**:

1. Check if the conversion path is supported:
   ```bash
   fileconverter list-formats
   ```

2. Consider using a multi-stage conversion with custom pipelines:
   ```yaml
   # pipeline.yaml
   stages:
     - format: docx
     - format: pdf
   ```
   ```bash
   fileconverter pipeline --config pipeline.yaml input.odt output.pdf
   ```

3. Ensure all required converter plugins are enabled in your configuration.

### Conversion Process Failed

**Problem**: Error during the conversion process itself.

**Solution**:

1. Check if all required dependencies are installed:
   ```bash
   # For document conversions
   pip install python-docx PyPDF2
   
   # For image conversions
   pip install Pillow Wand
   ```

2. Ensure external dependencies are available:
   ```bash
   # For LibreOffice-based conversions
   libreoffice --version
   
   # For ImageMagick-based conversions
   convert --version
   ```

3. Enable verbose logging to get more information:
   ```bash
   fileconverter -vv convert input.docx output.pdf
   ```

## Format-Specific Problems

### Document Conversion Issues

#### DOCX to PDF Conversion Fails

**Problem**: Converting Microsoft Word documents to PDF fails.

**Solution**:

1. Ensure you have the required dependencies:
   ```bash
   pip install python-docx docx2pdf
   ```

2. Install LibreOffice as a fallback converter:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install libreoffice-common
   
   # macOS
   brew install libreoffice
   
   # Windows
   # Install from https://www.libreoffice.org/download/
   ```

3. Check if the DOCX file is password-protected or corrupted.

#### PDF Conversion Issues

**Problem**: PDF output has formatting problems or is missing content.

**Solution**:

1. Try adjusting PDF output parameters:
   ```bash
   fileconverter convert document.docx document.pdf --params "margin=1.5" --params "orientation=portrait"
   ```

2. For HTML to PDF conversions, customize the CSS:
   ```bash
   fileconverter convert document.html document.pdf --params "css=custom.css"
   ```

### Spreadsheet Conversion Issues

#### CSV Encoding Problems

**Problem**: CSV files contain incorrect characters or encoding issues.

**Solution**:

1. Specify the encoding explicitly:
   ```bash
   fileconverter convert data.csv data.xlsx --params "encoding=utf-8"
   ```

2. For spreadsheet to CSV conversion, specify the delimiter:
   ```bash
   fileconverter convert data.xlsx data.csv --params "delimiter=;" --params "encoding=utf-8"
   ```

### Image Conversion Issues

#### Image Quality Issues

**Problem**: Converted images have poor quality or artifacts.

**Solution**:

1. Adjust quality settings for lossy formats:
   ```bash
   fileconverter convert image.png image.jpg --params "quality=95" --params "progressive=true"
   ```

2. For resizing, specify the dimensions:
   ```bash
   fileconverter convert image.jpg image_small.jpg --params "width=800" --params "height=600" --params "resize_method=lanczos"
   ```

#### Transparency Issues

**Problem**: PNG transparency is lost when converting to other formats.

**Solution**:

1. When converting to formats that support transparency (like WebP or GIF):
   ```bash
   fileconverter convert image.png image.webp --params "lossless=true"
   ```

2. When converting to formats without transparency (like JPEG), specify a background color:
   ```bash
   fileconverter convert image.png image.jpg --params "background=#FFFFFF"
   ```

## Performance Issues

### Slow Conversion

**Problem**: Conversions take too long to complete.

**Solution**:

1. For batch operations, enable parallel processing:
   ```bash
   fileconverter batch *.docx --output-dir ./pdf/ --output-format pdf --parallel 4
   ```

2. Optimize conversion parameters for speed:
   ```bash
   # For image conversions, lower quality for faster processing
   fileconverter convert image.png image.jpg --params "quality=75"
   
   # For PDF creation, use lower resolution
   fileconverter convert document.docx document.pdf --params "resolution=150"
   ```

3. Use a faster storage device for temporary files:
   ```bash
   # Set temporary directory on an SSD
   export FILECONVERTER_GENERAL_TEMP_DIR=/fast_storage/temp
   ```

### High Memory Usage

**Problem**: Conversions consume excessive memory.

**Solution**:

1. Process large files in chunks when possible:
   ```bash
   # For spreadsheet conversions
   fileconverter convert large_data.xlsx output.csv --params "chunk_size=10000"
   ```

2. Reduce image dimensions before processing:
   ```bash
   fileconverter convert large_image.tiff small_image.jpg --params "max_dimension=2000"
   ```

3. Close other memory-intensive applications during conversion.

## GUI Problems

### GUI Won't Start

**Problem**: The GUI application fails to launch.

**Solution**:

1. Ensure PyQt6 is installed:
   ```bash
   pip install PyQt6 PyQt6-QScintilla
   ```

2. Check for errors in the terminal when launching:
   ```bash
   fileconverter-gui --debug
   ```

3. Try reinstalling with GUI dependencies:
   ```bash
   pip uninstall fileconverter
   pip install fileconverter[gui]
   ```

### GUI Freezes

**Problem**: The GUI becomes unresponsive during conversion.

**Solution**:

1. Enable background processing:
   ```bash
   # In GUI settings, enable "Process in background thread"
   ```

2. For very large files, use the CLI interface instead:
   ```bash
   fileconverter convert large_file.docx output.pdf
   ```

3. Update to the latest version, which may include performance improvements.

## CLI Problems

### Command Not Found

**Problem**: The `fileconverter` command is not found.

**Solution**:

1. Ensure the package is installed:
   ```bash
   pip show fileconverter
   ```

2. Check if the installation directory is in your PATH:
   ```bash
   # Add to PATH temporarily
   export PATH=$PATH:~/.local/bin
   
   # Add to PATH permanently (add to ~/.bashrc or equivalent)
   echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
   ```

3. Try using the module directly:
   ```bash
   python -m fileconverter convert input.docx output.pdf
   ```

### Wildcards Not Working

**Problem**: Wildcards in batch mode don't match the expected files.

**Solution**:

1. Use quotes around wildcard patterns:
   ```bash
   fileconverter batch "*.docx" --output-dir ./pdf/ --output-format pdf
   ```

2. For recursive matching, use the `--recursive` flag:
   ```bash
   fileconverter batch "**/*.docx" --output-dir ./pdf/ --output-format pdf --recursive
   ```

3. On Windows, you may need to use backslashes and different quotes:
   ```bash
   fileconverter batch "documents\*.docx" --output-dir pdf --output-format pdf
   ```

## Configuration Issues

### Configuration Not Applied

**Problem**: Custom configuration settings are not being applied.

**Solution**:

1. Check the configuration file location:
   ```bash
   # System-wide: /etc/fileconverter/config.yaml
   # User-specific: ~/.config/fileconverter/config.yaml
   # Project-specific: ./fileconverter.yaml
   ```

2. Specify the configuration file explicitly:
   ```bash
   fileconverter --config my_config.yaml convert input.docx output.pdf
   ```

3. Use environment variables to verify settings:
   ```bash
   export FILECONVERTER_LOGGING_LEVEL=DEBUG
   fileconverter convert input.docx output.pdf
   ```

### Conflicting Configuration

**Problem**: Configuration settings from different sources conflict.

**Solution**:

1. Remember the configuration precedence:
   - Command-line arguments (highest)
   - Environment variables
   - Custom config file (--config)
   - Project config (./fileconverter.yaml)
   - User config (~/.config/fileconverter/config.yaml)
   - System config (/etc/fileconverter/config.yaml)
   - Default configuration (lowest)

2. To override a specific setting, use a more specific source:
   ```bash
   # Override configuration with command-line
   fileconverter --max-file-size 500 convert large_file.docx output.pdf
   ```

## Dependency Problems

### Missing External Dependencies

**Problem**: Errors about missing external programs or libraries.

**Solution**:

1. Install required system dependencies:

   **For document conversions**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install libreoffice-common wkhtmltopdf
   
   # macOS
   brew install libreoffice wkhtmltopdf
   
   # Windows
   # Install from official websites
   ```

   **For image conversions**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install imagemagick
   
   # macOS
   brew install imagemagick
   
   # Windows
   # Install from https://imagemagick.org/script/download.php
   ```

2. Ensure the external dependencies are in your PATH.

3. Try alternative conversion methods that don't require external dependencies:
   ```bash
   fileconverter convert document.docx document.html --params "converter=python-only"
   ```

### Python Package Compatibility

**Problem**: Errors about incompatible Python packages.

**Solution**:

1. Create an isolated environment:
   ```bash
   python -m venv fileconverter-env
   source fileconverter-env/bin/activate
   pip install fileconverter
   ```

2. Install specific versions if needed:
   ```bash
   pip install "pillow>=9.0.0,<10.0.0"
   ```

3. Update all dependencies:
   ```bash
   pip install --upgrade fileconverter[all]
   ```

## Logging and Debugging

### Enabling Debug Logs

To get more detailed information about what's happening:

```bash
# Enable verbose output
fileconverter -v convert input.docx output.pdf

# Enable debug logging
fileconverter -vv convert input.docx output.pdf

# Save logs to a file
fileconverter --log-file debug.log -vv convert input.docx output.pdf
```

### Preserving Temporary Files

To investigate intermediate files during conversion:

```bash
# Through command-line
fileconverter --preserve-temp convert input.docx output.pdf

# Through configuration
general:
  preserve_temp_files: true
```

The location of temporary files will be printed in the debug logs.

### Tracking Conversion Process

To understand the conversion workflow:

```bash
# Enable tracing of converter selection
export FILECONVERTER_LOGGING_LEVEL=DEBUG
fileconverter convert input.docx output.pdf
```

## Getting Help

If you encounter issues not covered in this guide:

1. **Check the documentation**:
   - Review all documentation in the `docs/` directory
   - Check the README.md file for basic usage

2. **Search existing issues**:
   - Browse the [GitHub Issues](https://github.com/tsgfulfillment/fileconverter/issues)
   - Search for specific error messages or keywords

3. **Create a new issue**:
   - Include FileConverter version (`fileconverter --version`)
   - Include operating system and Python version
   - Provide steps to reproduce the issue
   - Attach sample files if possible (make sure they don't contain sensitive information)
   - Include command output and error messages
   - If possible, include logs with `-vv` enabled

4. **Community Help**:
   - Use the [Discussions](https://github.com/tsgfulfillment/fileconverter/discussions) tab for general questions
   - Join the community chat (if available)

For urgent issues or professional support, contact the TSG Fulfillment IT team directly.