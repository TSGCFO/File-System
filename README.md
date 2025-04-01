# FileConverter

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)

A comprehensive file conversion utility designed for IT administrators at TSG Fulfillment. This tool provides a robust and extensible framework for converting files between different formats, with support for a wide range of file types including documents, spreadsheets, images, data exchange formats, and archives.

FileConverter simplifies the often complex process of converting files between formats, making it accessible both through an intuitive command-line interface and a user-friendly graphical application. Its modular architecture allows easy extension to support additional file formats as needed.

## 📋 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Command Line Interface](#command-line-interface)
  - [Graphical User Interface](#graphical-user-interface)
  - [Custom Conversion Pipelines](#custom-conversion-pipelines)
- [Supported Formats](#supported-formats)
- [Configuration](#configuration)
- [Architecture](#architecture)
- [Development](#development)
  - [Setup Development Environment](#setup-development-environment)
  - [Adding New Converters](#adding-new-converters)
  - [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## ✨ Features

- **Comprehensive Format Support**: Convert between various document, spreadsheet, image, data exchange, and archive formats
- **Batch Processing**: Convert multiple files in a single operation with parallel processing for improved performance
- **Custom Conversion Pipelines**: Create and save custom conversion workflows for multi-stage conversions
- **Dual Interfaces**: Choose between command-line interface for automation or GUI for interactive usage
- **Extensible Architecture**: Easily add support for new file formats through the plugin system
- **Robust Error Handling**: Detailed logging and error reporting to facilitate troubleshooting
- **Cross-Platform Compatibility**: Works seamlessly on Windows, macOS, and Linux
- **Python 3.12 Compatible**: Leverages the latest Python features for improved performance and reliability
- **Configurable**: Extensive configuration options through command-line arguments, configuration files, or environment variables
- **Format Detection**: Intelligent format detection based on file extensions and content analysis
- **Conversion Parameters**: Fine-tuned control of conversion processes through customizable parameters
- **Progress Tracking**: Real-time progress reporting for long-running conversions
- **Conversion History**: Track and manage previous conversion operations
- **File Validation**: Validate files before conversion to ensure compatibility

## 🚀 Installation

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

## 🔧 Usage

### Command Line Interface

The command line interface provides powerful batch processing capabilities and is ideal for automation scripts and server environments.

#### Basic Conversion

Convert a single file from one format to another:

```bash
fileconverter convert input.docx output.pdf
```

#### Conversion with Parameters

Specify conversion parameters for fine-tuned control:

```bash
fileconverter convert input.docx output.pdf --params "margin=1.0" --params "orientation=landscape"
```

#### Batch Conversion

Convert multiple files in a single operation:

```bash
fileconverter batch *.csv --output-dir ./json_files/ --output-format json
```

Use wildcards to process files matching a pattern:

```bash
fileconverter batch "documents/*.docx" --output-dir ./pdf_files/ --output-format pdf --recursive
```

#### Help and Information

Get detailed help for any command:

```bash
# General help
fileconverter --help

# Command-specific help
fileconverter convert --help
fileconverter batch --help

# List supported formats
fileconverter list-formats

# List formats by category
fileconverter list-formats --category document
```

### Graphical User Interface

The GUI provides an intuitive interface for interactive file conversion and is recommended for desktop users.

Launch the graphical interface:

```bash
# Using the dedicated command
fileconverter-gui

# Or using the main command with --gui flag
fileconverter --gui

# Alternative: Direct launcher (no installation required)
python launch_gui.py
```

If you encounter issues with the installation or the GUI commands, use the alternative direct launcher script included in the repository.

The GUI features:

- Drag-and-drop file support
- Format detection and conversion suggestions
- Visual progress indicators
- Conversion history tracking
- Custom parameter configuration
- Settings management

### Custom Conversion Pipelines

Create multi-stage conversion pipelines for complex workflows:

```bash
# Using a pipeline configuration file
fileconverter pipeline --config pipeline.yaml input.docx output.pdf

# Example pipeline.yaml:
# stages:
#   - format: html
#     parameters: { css: style.css }
#   - format: pdf
#     parameters: { margin: 1.0 }
```

See the [examples/custom_pipeline.py](examples/custom_pipeline.py) for detailed usage.

## 📁 Supported Formats

FileConverter supports a wide range of file formats, grouped by category:

### Document Formats

- Microsoft Word (.doc, .docx)
- PDF (.pdf)
- Rich Text Format (.rtf)
- OpenDocument Text (.odt)
- Markdown (.md)
- HTML (.html, .htm)
- Plain Text (.txt)

### Spreadsheet Formats

- Microsoft Excel (.xls, .xlsx)
- CSV (.csv)
- TSV (.tsv)
- OpenDocument Spreadsheet (.ods)
- JSON (.json) - for tabular data

### Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- GIF (.gif)
- TIFF (.tiff, .tif)
- WebP (.webp)
- SVG (.svg)

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
- RAR (.rar) - extraction only

### Font Formats

- TrueType (.ttf)
- OpenType (.otf)
- WOFF (.woff)
- WOFF2 (.woff2)

### Database Formats

- SQLite (.db, .sqlite)
- CSV export/import

## ⚙️ Configuration

FileConverter offers flexible configuration options to customize its behavior.

### Configuration Files

Configuration can be specified in YAML format at different locations (in order of precedence):

1. Custom path specified with `--config` option
2. Project-specific: `./fileconverter.yaml`
3. User-specific: `~/.config/fileconverter/config.yaml`
4. System-wide: `/etc/fileconverter/config.yaml`

### Example Configuration

```yaml
general:
  temp_dir: /path/to/temp
  max_file_size_mb: 200
  preserve_temp_files: false

logging:
  level: INFO
  file: fileconverter.log
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

converters:
  document:
    enabled: true
    pdf:
      resolution: 300
      compression: medium
  
  spreadsheet:
    enabled: true
    excel:
      date_format: "YYYY-MM-DD"
  
  image:
    enabled: true
    jpeg:
      quality: 85
      progressive: true

gui:
  theme: system
  recent_files_limit: 10
  show_tooltips: true
```

### Environment Variables

Configuration can also be specified via environment variables with the prefix `FILECONVERTER_`:

```bash
# Set maximum file size to 500MB
export FILECONVERTER_GENERAL_MAX_FILE_SIZE_MB=500

# Set logging level to DEBUG
export FILECONVERTER_LOGGING_LEVEL=DEBUG
```

## 🏗 Architecture

FileConverter is built on a modular architecture consisting of several key components:

- **Core Engine**: Orchestrates the conversion process
- **Converter Registry**: Manages available converter plugins
- **Converter Plugins**: Handle specific format conversions
- **CLI Module**: Provides command-line interface
- **GUI Module**: Provides graphical user interface
- **Configuration System**: Manages user preferences and settings
- **Utility Modules**: Provide common functionality

For a detailed architecture overview, see the [Architecture Documentation](docs/architecture.md).

## 👨‍💻 Development

### Setup Development Environment

1. Clone the repository:

   ```bash
   git clone https://github.com/tsgfulfillment/fileconverter.git
   cd fileconverter
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:

   ```bash
   pip install -e ".[dev,gui]"
   ```

4. Alternative simplified installation:

   If you encounter issues with the standard installation, use the installation helper script:

   ```bash
   # Quick installation and test
   python install_and_test.py
   
   # Or run the tests to verify your setup
   python direct_test.py
   ```

### Adding New Converters

To add support for a new file format:

1. Create a new module in the `fileconverter/converters` directory
2. Implement a converter class that inherits from `BaseConverter`
3. Register input and output formats
4. Implement the conversion logic

Example structure:

```python
from fileconverter.core.registry import BaseConverter

class MyFormatConverter(BaseConverter):
    @classmethod
    def get_input_formats(cls):
        return ["format1", "format2"]
    
    @classmethod
    def get_output_formats(cls):
        return ["format3", "format4"]
    
    @classmethod
    def get_format_extensions(cls, format_name):
        if format_name == "format1":
            return ["fmt1", "f1"]
        # ...
    
    def convert(self, input_path, output_path, temp_dir, parameters):
        # Implement conversion logic
        return {
            "input_format": "format1",
            "output_format": "format3",
            # ...
        }
    
    def get_parameters(self):
        return {
            "format3": {
                "quality": {
                    "type": "number",
                    "description": "Output quality",
                    "default": 85,
                    "min": 1,
                    "max": 100
                },
                # ...
            }
        }
```

For detailed documentation, see [Adding New Converters](docs/development/adding_converters.md).

### Testing

FileConverter uses pytest for testing. To run the test suite:

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=fileconverter

# Run specific test modules
pytest tests/test_core.py
pytest tests/test_converters/

# Test the GUI launcher
python test_launcher.py

# Test installation and setup
python direct_test.py
```

### Troubleshooting

If you encounter issues with installation or launching the GUI:

1. **Installation Issues**:
   - Try the direct installation script: `python install_and_test.py`
   - Install dependencies manually: `pip install PyQt6 Pillow pyyaml click`
   - Check error messages for missing dependencies

2. **GUI Launch Issues**:
   - Use the direct launcher: `python launch_gui.py`
   - Verify PyQt6 is installed: `pip install PyQt6`
   - Run the test script: `python test_launcher.py`
   - Check if the icon is generated: `python -c "from fileconverter.gui.resources.icon_generator import generate_icon; generate_icon()"`

3. **Path Issues**:
   - If commands like `fileconverter` or `fileconverter-gui` aren't found, verify your Python Scripts directory is in your PATH
   - On Windows: Add `%USERPROFILE%\AppData\Local\Programs\Python\Python3x\Scripts` to your PATH
   - On Linux/macOS: Ensure `~/.local/bin` is in your PATH

For more troubleshooting help, see the [Troubleshooting Guide](docs/troubleshooting.md).

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Report bugs**: Open an issue if you find a bug. Please include:
   - A clear, descriptive title
   - Steps to reproduce the issue
   - Expected and actual results
   - FileConverter version and environment details

2. **Suggest features**: Open an issue for feature requests. Please include:
   - A clear description of the feature
   - Use cases and benefits
   - Any implementation ideas you may have

3. **Submit pull requests**: Implement new features or fix bugs. Please ensure:
   - Your code addresses a specific issue or adds a valuable feature
   - You've discussed major changes in an issue before implementation
   - Your branch is based on the latest main/master branch

Please follow these guidelines when contributing:

- Follow the coding style (use Black for formatting with a line length of 88 characters)
- Write clear, descriptive commit messages
- Add tests for new functionality with good coverage
- Update documentation for your changes
- Follow the pull request template

The project follows a code review process where maintainers will review your contribution before merging. Be responsive to feedback and be prepared to make adjustments if needed.

### CI/CD Pipeline

FileConverter uses GitHub Actions for continuous integration and deployment. The pipeline provides comprehensive testing and automatic deployments.

#### How the Workflow Works

1. **Trigger**: The workflow runs when:
   - Code is pushed to the `roo` branch
   - A pull request is created targeting the `main` branch

2. **Test Execution Process**:
   - Tests run in parallel across all configured platforms and Python versions
   - Each test phase must pass for the workflow to succeed
   - Results and logs are saved as artifacts for later review
   - A test summary is generated for quick overview of results

3. **Test Requirements**:
   - **Code Coverage**: Minimum 80% test coverage required
   - **All Test Types**: Unit, integration, installation, and dependency tests must pass
   - **Cross-Platform**: Tests must pass on Windows, macOS, and Ubuntu

#### Test Suite Components

- **Phase 1: Unit Tests with Coverage**
  - Runs all unit tests with code coverage measurement
  - Enforces 80% minimum code coverage
  - Generates coverage reports in XML and terminal formats

- **Phase 2: Cross-Platform Integration Tests**
  - Executes the comprehensive test suite with `run_tests.py`
  - Tests core functionality across all platforms
  - Generates detailed logs of test execution

- **Phase 3: Installation Testing**
  - Validates the package installation process
  - Tests entry points, shortcut creation, and executable generation
  - Ensures environment variables and paths are correctly set

- **Phase 4: Dependency Management Testing**
  - Tests the dependency detection and installation system
  - Validates offline installation capabilities
  - Checks platform-specific dependency handling

#### Artifacts and Logs

- Detailed logs are generated for each test phase
- Test logs, coverage reports, and execution results are saved as artifacts
- Artifacts are attached to each workflow run for easy access and debugging

#### Automatic Deployment

- If all tests pass on the `roo` branch, changes are automatically merged to `main`
- Merge commits include [CI] tag for easy identification
- The `main` branch always contains stable, fully tested code
- **Branch Strategy**:
  - `roo`: Development branch where all contributions should be targeted
  - `main`: Stable release branch (don't submit PRs directly to main)

Contributors should:
1. Create feature branches from `roo`
2. Submit PRs targeting the `roo` branch
3. Wait for CI tests to complete successfully
4. Address any test failures before changes can be merged

The CI pipeline runs all tests with the `--no-gui` flag to ensure compatibility in non-GUI environments.

For more detailed information, see [CONTRIBUTING.md](CONTRIBUTING.md).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- All the open-source libraries that make this project possible:
  - [Click](https://click.palletsprojects.com/) for the CLI interface
  - [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) for the GUI interface
  - [Pillow](https://python-pillow.org/) for image processing
  - [python-docx](https://python-docx.readthedocs.io/) for Word document handling
  - [PyPDF2](https://pypdf2.readthedocs.io/) for PDF manipulation
  - [pandas](https://pandas.pydata.org/) for data processing
  - And many others listed in the requirements.txt file
- TSG Fulfillment IT team for their support, feedback, and testing
- Contributors who have helped improve this project through code, documentation, and feedback
- Open source community for inspiration and shared knowledge

---

© 2023-2025 TSG Fulfillment | [Website](https://tsgfulfillment.com) | [GitHub](https://github.com/tsgfulfillment)
