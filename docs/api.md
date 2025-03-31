# FileConverter API Reference

This document provides comprehensive documentation for the FileConverter API, detailing the core components, classes, methods, and functions available for developers.

## Table of Contents

- [Core Components](#core-components)
  - [ConversionEngine](#conversionengine)
  - [ConverterRegistry](#converterregistry)
  - [BaseConverter](#baseconverter)
- [Converters](#converters)
  - [DocumentConverter](#documentconverter)
  - [SpreadsheetConverter](#spreadsheetconverter)
  - [ImageConverter](#imageconverter)
  - [DataExchangeConverter](#dataexchangeconverter)
  - [ArchiveConverter](#archiveconverter)
- [Utilities](#utilities)
  - [File Utilities](#file-utilities)
  - [Error Handling](#error-handling)
  - [Logging](#logging)
  - [Validation](#validation)
- [Configuration System](#configuration-system)
- [CLI Interface](#cli-interface)
- [GUI Interface](#gui-interface)

## Core Components

### ConversionEngine
The `ConversionEngine` is the central component of FileConverter that orchestrates the conversion process. It supports both direct conversions and multi-step conversions through intermediate formats when no direct converter is available.

#### Class: `ConversionEngine`

```python
class ConversionEngine:
    def __init__(self, config_path: Optional[str] = None) -> None:
        """Initialize the conversion engine.
        
        Args:
            config_path: Optional path to a configuration file. If None,
                the default configuration will be used, which is determined by
                looking for configuration files in standard locations:
                1. ./fileconverter.yaml (current directory)
                2. ~/.config/fileconverter/config.yaml (user config)
                3. /etc/fileconverter/config.yaml (system-wide config)
                
                Environment variables with the prefix FILECONVERTER_ can also
                override configuration values.
        
        Raises:
            ConfigError: If the configuration file exists but cannot be parsed.
                This exception includes details about the parsing error.
        """
        
    def convert_file(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Convert a file from one format to another.
        
        This method handles the entire conversion process, including:
        - Validating the input file existence and readability
        - Checking file size against configured restrictions
        - Determining input and output formats based on file extensions
        - Finding an appropriate converter or multi-step conversion path
        - Creating a temporary workspace for the conversion
        - Executing the conversion through the selected converters
        - Cleaning up temporary files unless preservation is requested
        
        Args:
            input_path: Path to the input file. Can be provided as a string
                or a Path object. The file must exist and be readable.
            
            output_path: Path where the output file will be saved. Can be
                provided as a string or a Path object. The directory must exist
                and be writable. If the file already exists, it will be overwritten.
            
            parameters: Optional parameters for the conversion. These parameters
                are passed directly to the converter and their meaning depends on
                the specific conversion being performed.
                
                If None, default parameters will be used based on the converter.
            
        Returns:
            Dictionary with information about the conversion, including:
            - input_format: The detected input format (e.g., "docx", "csv")
            - output_format: The detected output format (e.g., "pdf", "xlsx")
            - input_path: The absolute path to the input file
            - output_path: The absolute path to the output file
            - conversion_time: Time taken for the conversion (in seconds)
            - Additional converter-specific information, which varies by converter
            
        Raises:
            ConversionError: If the conversion fails. The exception message provides
                detailed information about the failure reason, which can be one of:
                - Invalid input file (file doesn't exist or isn't readable)
                - File size exceeding the maximum allowed limit
                - Unsupported input or output format
                - No available converter or conversion path for the format pair
                - Error during the conversion process
        """
        
    def get_conversion_info(
        self,
        input_format: str,
        output_format: str
    ) -> Optional[Dict[str, Any]]:
        """Get information about a specific conversion path.
        
        This method provides detailed information about a conversion path,
        including the converter that would be used and its supported parameters.
        It's useful for discovering what parameters are available for a specific
        conversion before performing it.
        
        Args:
            input_format: Input file format (e.g., "docx", "csv", "jpg").
                Format names are case-insensitive.
            
            output_format: Output file format (e.g., "pdf", "xlsx", "png").
                Format names are case-insensitive.
        
        Returns:
            Optional[Dict[str, Any]]: Dictionary with information about the conversion,
            or None if the conversion is not supported. When a conversion is supported,
            the dictionary includes:
            - input_format: The input format (normalized to lowercase)
            - output_format: The output format (normalized to lowercase)
            - converter_name: The name of the converter class that would be used
            - description: A description of the converter from its docstring
            - parameters: Dictionary of supported parameters with their descriptions,
              organized by output format.
        """
        
    def get_supported_conversions(self) -> Dict[str, List[str]]:
        """Get all supported conversion combinations.
        
        Provides a comprehensive map of all available conversion paths in the system,
        including both direct conversions and those possible through multi-step paths.
        This is useful for discovering what conversions are possible with the
        currently loaded converters.
        
        Returns:
            Dict[str, List[str]]: Dictionary mapping input formats to lists of
            supported output formats. The keys are input format names (lowercase)
            and the values are lists of output format names (lowercase) that
            the input can be converted to.
        """
```
```

#### Usage Examples

```python
from fileconverter import ConversionEngine

# Initialize the engine
engine = ConversionEngine()

# Convert a file with default parameters
result = engine.convert_file("document.docx", "document.pdf")

# Convert with custom parameters
result = engine.convert_file(
    "image.png", 
    "image.jpg", 
    parameters={"quality": 90, "progressive": True}
)

# Check if a conversion is supported
info = engine.get_conversion_info("xlsx", "csv")
if info:
    print(f"XLSX to CSV conversion is supported using {info['converter_name']}")
    print(f"Supported parameters: {info['parameters']}")

# Get all supported conversions
conversions = engine.get_supported_conversions()
for input_format, output_formats in conversions.items():
    print(f"{input_format} can be converted to: {', '.join(output_formats)}")
```

### ConverterRegistry

The `ConverterRegistry` is responsible for discovering, registering, and providing access to converter implementations. It also handles finding conversion paths between formats that may require multiple steps.

#### Class: `ConverterRegistry`

```python
class ConverterRegistry:
    def __init__(self) -> None:
        """Initialize the converter registry.
        
        This method scans the converters package for modules containing
        converter implementations, imports each module, and registers any
        classes that implement the BaseConverter interface. It uses Python's
        introspection capabilities to dynamically discover converters without
        requiring explicit registration.
        
        The method checks the configuration to determine if specific converter
        categories are enabled or disabled. If a category is disabled in the
        configuration, its converters will not be registered.
        """
        
    def get_converter(
        self,
        input_format: str,
        output_format: str
    ) -> Optional[BaseConverter]:
        """Get a converter instance for the specified formats.
        
        This method finds and returns a converter capable of converting from
        the specified input format to the specified output format. If multiple
        converters are available for the format pair, the first one registered
        is returned (in future versions, this might be based on priority).
        
        The method normalizes format names to lowercase to ensure case-insensitive
        matching. It also implements a caching mechanism to reuse converter
        instances for better performance and memory efficiency.
        
        Args:
            input_format: Input file format (e.g., "docx", "csv").
                Format names are case-insensitive.
            output_format: Output file format (e.g., "pdf", "xlsx").
                Format names are case-insensitive.
        
        Returns:
            Optional[BaseConverter]: A converter instance capable of performing
                the requested conversion, or None if no suitable converter is found.
        """
    
    def find_conversion_path(
        self,
        input_format: str,
        output_format: str
    ) -> Optional[List[BaseConverter]]:
        """Find a conversion path between the specified formats.
        
        This method searches for a path from the input format to the output format,
        potentially through intermediate formats if a direct converter is not available.
        It uses a breadth-first search algorithm to find the shortest path.
        
        Args:
            input_format: Input file format (e.g., "docx", "csv").
                Format names are case-insensitive.
            output_format: Output file format (e.g., "pdf", "xlsx").
                Format names are case-insensitive.
        
        Returns:
            Optional[List[BaseConverter]]: A list of converter instances forming a
                conversion path from input to output, or None if no path is found.
                For direct conversions, the list will contain a single converter.
                For multi-step conversions, the list will contain multiple converters
                chained together.
        """
        
    def get_conversion_map(self) -> Dict[str, List[str]]:
        """Get a mapping of all supported conversion combinations.
        
        This method returns a dictionary mapping each input format to a list of
        output formats that it can be converted to, either directly or through
        intermediate formats.
        
        Returns:
            Dictionary mapping input formats to lists of supported output formats.
        """
        
    def get_supported_formats(
        self,
        category: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """Get all supported file formats.
        
        Args:
            category: Optional category to filter formats.
            
        Returns:
            Dictionary mapping format categories to lists of format names.
        """
        
    def get_format_extensions(self, format_name: str) -> List[str]:
        """Get the file extensions for a specific format.
        
        Args:
            format_name: Name of the format.
            
        Returns:
            List of file extensions (without the dot).
        """
```

### BaseConverter

The `BaseConverter` class defines the interface that all converter implementations must adhere to.

#### Class: `BaseConverter`

```python
class BaseConverter:
    @classmethod
    def get_input_formats(cls) -> List[str]:
        """Get the list of input formats supported by this converter."""
        
    @classmethod
    def get_output_formats(cls) -> List[str]:
        """Get the list of output formats supported by this converter."""
        
    @classmethod
    def get_format_extensions(cls, format_name: str) -> List[str]:
        """Get the list of file extensions for a specific format."""
        
    def convert(
        self, 
        input_path: Any, 
        output_path: Any, 
        temp_dir: Any,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert a file from one format to another."""
        
    def get_parameters(self) -> Dict[str, Dict[str, Any]]:
        """Get the parameters supported by this converter."""
```

## Converters

FileConverter includes several converter implementations, each specialized for a specific category of file formats.

### DocumentConverter

The `DocumentConverter` handles conversions between document formats like DOCX, PDF, HTML, and Markdown.

#### Supported Input Formats

- `doc`: Microsoft Word Document (binary format)
- `docx`: Microsoft Word Document (Open XML format)
- `rtf`: Rich Text Format
- `odt`: OpenDocument Text
- `txt`: Plain Text
- `html`/`htm`: HTML Document
- `md`: Markdown

#### Supported Output Formats

- `docx`: Microsoft Word Document (Open XML format)
- `pdf`: Portable Document Format
- `txt`: Plain Text
- `html`: HTML Document
- `md`: Markdown

#### Parameters

For PDF output:
- `page_size`: Page size (e.g., "A4", "Letter")
- `orientation`: Page orientation ("portrait" or "landscape")
- `margin`: Page margin in inches
- `compression`: PDF compression level

For HTML output:
- `css`: CSS file path or CSS content
- `template`: HTML template file path
- `title`: Document title

For DOCX output:
- `template`: Template file path
- `style`: Style to apply

For TXT output:
- `encoding`: Text encoding
- `line_ending`: Line ending style

### SpreadsheetConverter

The `SpreadsheetConverter` handles conversions between spreadsheet formats like XLSX, CSV, and JSON.

#### Supported Input Formats

- `xlsx`: Microsoft Excel Spreadsheet (Open XML format)
- `xls`: Microsoft Excel Spreadsheet (binary format)
- `csv`: Comma-Separated Values
- `tsv`: Tab-Separated Values
- `ods`: OpenDocument Spreadsheet

#### Supported Output Formats

- `xlsx`: Microsoft Excel Spreadsheet (Open XML format)
- `csv`: Comma-Separated Values
- `json`: JavaScript Object Notation (for tabular data)
- `html`: HTML Table

#### Parameters

For CSV output:
- `delimiter`: Field delimiter character
- `quotechar`: Character used to quote fields
- `encoding`: Text encoding

For XLSX output:
- `sheet_name`: Name of the sheet
- `date_format`: Format for date values

For JSON output:
- `indent`: Indentation level for pretty printing
- `orient`: Orientation of the JSON structure

### ImageConverter

*(Similar sections for other converter types...)*

## Utilities

FileConverter provides several utility modules to support the conversion process.

### File Utilities

The `file_utils` module provides functions for file operations and format detection.

```python
def get_file_format(file_path: Union[str, Path]) -> Optional[str]:
    """Get the format of a file based on its extension."""
    
def get_file_extension(file_path: Union[str, Path]) -> str:
    """Get the extension of a file without the dot."""
    
def get_file_size_mb(file_path: Union[str, Path]) -> float:
    """Get the size of a file in megabytes."""
    
def guess_encoding(file_path: Union[str, Path]) -> str:
    """Guess the encoding of a text file."""
    
def copy_file(
    source_path: Union[str, Path], 
    target_path: Union[str, Path]
) -> None:
    """Copy a file from source to target."""
    
def list_files(
    pattern: str, 
    recursive: bool = False
) -> List[str]:
    """List files matching a pattern."""
```

### Error Handling

The `error_handling` module provides classes and functions for handling conversion errors.

```python
class ConversionError(Exception):
    """Exception raised when a conversion fails."""
    
def handle_error(error: Exception, logger) -> None:
    """Handle an error during conversion."""
```

### Logging

The `logging_utils` module provides logging functionality.

```python
def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the specified name."""
    
def configure_logging(level: str, file: Optional[str] = None) -> None:
    """Configure logging with the specified level and optional file."""
```

### Validation

The `validation` module provides functions for validating inputs.

```python
def validate_file_path(
    path: Union[str, Path], 
    must_exist: bool = False
) -> None:
    """Validate a file path."""
```

## Configuration System

FileConverter uses a comprehensive configuration system that supports multiple configuration sources with a clear precedence order.

### Configuration Sources (in order of precedence)

1. Command-line arguments (highest precedence)
2. Environment variables (with `FILECONVERTER_` prefix)
3. Configuration files:
   - Custom path specified with `--config` option
   - Project-specific: `./fileconverter.yaml`
   - User-specific: `~/.config/fileconverter/config.yaml`
   - System-wide: `/etc/fileconverter/config.yaml`
4. Default built-in values (lowest precedence)

The configuration system merges settings from these different sources, with later sources taking precedence over earlier ones. This layered approach allows administrators to set system defaults, while users can override specific settings for their needs, and individual projects can have customized settings without affecting other projects.

### Configuration API

```python
from fileconverter.config import get_config, create_default_config_file

# Get the global configuration instance
config = get_config()  # Uses default search paths
config = get_config("/path/to/custom/config.yaml")  # Uses specified file

# Access configuration values
max_file_size = config.get("general", "max_file_size_mb", default=100)
jpeg_quality = config.get("converters", "image", "jpeg", "quality", default=85)

# Modify configuration values
config.set(500, "general", "max_file_size_mb")
config.set(90, "converters", "image", "jpeg", "quality")

# Save configuration
config.save()  # Save to the loaded path
config.save("/path/to/output/config.yaml")  # Save to a new path

# Create a default configuration file with documentation
default_config_path = create_default_config_file()
```

### Configuration Format

Configuration is specified in YAML format with support for hierarchical settings and comments for documentation. Here's an example:

```yaml
# FileConverter Configuration
# This file contains settings for the FileConverter application.
# Modify as needed to customize the behavior of the converter.

general:
  # Directory for temporary files (leave empty to use system default)
  temp_dir: null
  
  # Whether to preserve temporary files after conversion (useful for debugging)
  preserve_temp_files: false
  
  # Maximum file size in MB that can be converted
  max_file_size_mb: 200

logging:
  # Logging level: DEBUG, INFO, WARNING, ERROR, or CRITICAL
  level: INFO
  
  # Path to log file (leave empty for console logging only)
  file: fileconverter.log
  
  # Log message format
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

converters:
  # Document converter settings (DOCX, PDF, TXT, etc.)
  document:
    # Whether the document converter is enabled
    enabled: true
    
    # PDF output settings
    pdf:
      # Resolution in DPI
      resolution: 300
      
      # Compression level: none, low, medium, high
      compression: medium
  
  # Spreadsheet converter settings (XLSX, CSV, etc.)
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
  
  # Image converter settings (JPEG, PNG, etc.)
  image:
    # Whether the image converter is enabled
    enabled: true
    
    # JPEG output settings
    jpeg:
      # Quality (1-100)
      quality: 85
      
      # Whether to use progressive rendering
      progressive: true

# GUI settings
gui:
  # Theme: system, light, dark
  theme: system
  
  # Maximum number of recent files to remember
  recent_files_limit: 10
  
  # Whether to show tooltips
  show_tooltips: true
```

### Environment Variables

Configuration can be specified via environment variables with the prefix `FILECONVERTER_`. The variable names should follow the hierarchical structure of the configuration, with levels separated by underscores.

Examples:
- `FILECONVERTER_GENERAL_MAX_FILE_SIZE_MB=500`
- `FILECONVERTER_LOGGING_LEVEL=DEBUG`
- `FILECONVERTER_CONVERTERS_IMAGE_JPEG_QUALITY=90`

## CLI Interface

FileConverter provides a command-line interface for file conversion operations.

### Commands

- `convert`: Convert a single file
- `batch`: Convert multiple files
- `list-formats`: List supported formats
- `pipeline`: Perform multi-stage conversion

### Examples

```bash
# Convert a single file
fileconverter convert input.docx output.pdf

# Convert with parameters
fileconverter convert input.docx output.pdf --params "margin=1.0" --params "orientation=landscape"

# Batch conversion
fileconverter batch *.csv --output-dir ./json_files/ --output-format json

# List supported formats
fileconverter list-formats

# List formats by category
fileconverter list-formats --category document
```

## GUI Interface

FileConverter includes a graphical user interface for interactive usage.

### Features

- Drag-and-drop file support
- Format detection and conversion suggestions
- Visual progress indicators
- Conversion history tracking
- Custom parameter configuration
- Settings management

### Usage

```bash
# Launch the GUI
fileconverter-gui

# Or using the main command with --gui flag
fileconverter --gui
```

For more details on the GUI components and usage, see the [GUI Documentation](./gui.md).