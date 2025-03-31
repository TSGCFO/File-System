"""
Conversion engine for FileConverter.

This module provides the main conversion engine that orchestrates
the file conversion process. The ConversionEngine class is the central
component responsible for managing file conversions between different formats.

The conversion workflow includes:
1. Validating input files and determining formats
2. Finding an appropriate converter from the registry
3. Creating a temporary workspace for the conversion
4. Executing the conversion process
5. Cleaning up temporary files

The engine handles the entire conversion process, including error handling,
format detection, and temporary file management. It acts as a facade to the
underlying converter implementations, providing a clean and consistent
interface for file conversion operations.

Key features of the ConversionEngine:
- Automatic format detection based on file extensions
- File size validation to prevent processing excessively large files
- Temporary directory management for conversion operations
- Comprehensive error handling with detailed error messages
- Configuration through multiple sources (file, environment variables)

Example usage:
    from fileconverter import ConversionEngine
    
    # Initialize the engine with default configuration
    engine = ConversionEngine()
    
    # Perform a basic conversion
    result = engine.convert_file(
        input_path="document.docx",
        output_path="document.pdf"
    )
    
    # Conversion with custom parameters
    result = engine.convert_file(
        input_path="spreadsheet.xlsx",
        output_path="spreadsheet.csv",
        parameters={"delimiter": ";", "encoding": "utf-8"}
    )
    
    # Get information about available conversions
    conversions = engine.get_supported_conversions()
    
    # Get detailed information about a specific conversion path
    info = engine.get_conversion_info("docx", "pdf")
    if info:
        print(f"Parameters: {info['parameters']}")

Notes:
    - The engine uses the ConverterRegistry to find appropriate converters
    - All paths can be provided as strings or Path objects
    - Temporary files are automatically cleaned up unless preserve_temp is set
    - Error messages are designed to be user-friendly and actionable
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from fileconverter.config import get_config
from fileconverter.core.registry import ConverterRegistry, BaseConverter
from fileconverter.utils.error_handling import ConversionError
from fileconverter.utils.file_utils import get_file_format, get_file_size_mb
from fileconverter.utils.logging_utils import get_logger
from fileconverter.utils.validation import validate_file_path

logger = get_logger(__name__)


class ConversionEngine:
    """Main engine for converting files between formats.
    
    The ConversionEngine is responsible for orchestrating the conversion process,
    including format detection, converter selection, and temporary file management.
    It provides a unified interface for all file conversion operations, handling
    the complexities of format detection, converter selection, and error management.
    
    This class follows the Facade design pattern, providing a simplified interface
    to the complex subsystem of converters and file handling utilities. It abstracts
    away the details of the conversion process, allowing users to perform conversions
    with minimal code.
    
    Attributes:
        config (Config): Configuration object with settings for the engine.
            This is loaded from the configuration file specified during initialization
            or from the default configuration sources if no file is specified.
        
        registry (ConverterRegistry): Registry of available converters.
            This is automatically populated with all converters found in the
            converters package during initialization.
        
        max_file_size_mb (int): Maximum allowed file size in MB.
            Files larger than this limit will be rejected to prevent
            excessive resource usage. Default is 100MB but can be
            configured through the configuration system.
        
        preserve_temp (bool): Whether to preserve temporary files after conversion.
            When set to True, temporary files created during the conversion process
            will not be deleted, which can be useful for debugging or for
            multi-stage conversion processes. Default is False.
        
        temp_dir (str): Custom temporary directory path, if specified.
            If provided, this directory will be used for storing temporary files
            during conversion instead of the system's default temporary directory.
    
    Note:
        The engine is thread-safe and can be used concurrently from multiple threads.
        Each conversion operation uses its own isolated temporary directory.
    
    TODO:
        - Add support for conversion cancellation
        - Implement progress reporting for long-running conversions
        - Add support for batch conversion with a single engine instance
        - Enhance logging with more detailed conversion metrics
    """

    def __init__(self, config_path: Optional[str] = None) -> None:
        """Initialize the conversion engine.
        
        Creates a new ConversionEngine instance with the specified configuration.
        During initialization, the engine:
        1. Loads the configuration from the specified file or default sources
        2. Initializes the converter registry, which discovers all available converters
        3. Sets up internal state based on the configuration
        
        Args:
            config_path (Optional[str]): Path to a configuration file. If None,
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
        
        Example:
            # Initialize with default configuration
            engine = ConversionEngine()
            
            # Initialize with custom configuration
            engine = ConversionEngine(config_path="/path/to/config.yaml")
            
            # After initialization, the engine is ready to perform conversions
            result = engine.convert_file("input.docx", "output.pdf")
        """
        self.config = get_config(config_path)
        self.registry = ConverterRegistry()
        
        # Get general configuration
        self.max_file_size_mb = self.config.get("general", "max_file_size_mb", default=100)
        self.preserve_temp = self.config.get("general", "preserve_temp_files", default=False)
        self.temp_dir = self.config.get("general", "temp_dir")
        
        logger.debug(f"Initialized ConversionEngine with max file size: {self.max_file_size_mb}MB")
    
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
        - Finding an appropriate converter in the registry
        - Creating a temporary workspace for the conversion
        - Executing the conversion through the selected converter
        - Cleaning up temporary files unless preservation is requested
        
        The method is the primary interface for file conversion operations
        and is designed to be simple to use while providing detailed information
        about the conversion process.
        
        Args:
            input_path (Union[str, Path]): Path to the input file. Can be provided
                as a string or a Path object. The file must exist and be readable.
            
            output_path (Union[str, Path]): Path where the output file will be saved.
                Can be provided as a string or a Path object. The directory must exist
                and be writable. If the file already exists, it will be overwritten.
            
            parameters (Optional[Dict[str, Any]]): Optional parameters for the conversion.
                These parameters are passed directly to the converter and their meaning
                depends on the specific conversion being performed. Common parameters
                include:
                - For PDF: "margin", "orientation", "page_size"
                - For spreadsheets: "delimiter", "encoding", "sheet_name"
                - For images: "quality", "resolution", "format_options"
                
                If None, default parameters will be used based on the converter.
        
        Returns:
            Dict[str, Any]: Dictionary with information about the conversion, including:
            - input_format: The detected input format (e.g., "docx", "csv")
            - output_format: The detected output format (e.g., "pdf", "xlsx")
            - input_path: The absolute path to the input file
            - output_path: The absolute path to the output file
            - conversion_time: Time taken for the conversion (in seconds)
            - Additional converter-specific information, which varies by converter
              but may include details like page count, word count, or other metrics
            
        Raises:
            ConversionError: If the conversion fails. The exception message provides
                detailed information about the failure reason, which can be one of:
                - Invalid input file (file doesn't exist or isn't readable)
                - File size exceeding the maximum allowed limit
                - Unsupported input or output format
                - No available converter for the format pair
                - Error during the conversion process
                The exception also includes suggestions for resolving the issue.
        
        Example:
            # Convert a Word document to PDF with default parameters
            result = engine.convert_file(
                input_path="document.docx",
                output_path="document.pdf"
            )
            print(f"Converted from {result['input_format']} to {result['output_format']}")
            
            # Convert a Word document to PDF with custom parameters
            result = engine.convert_file(
                input_path="document.docx",
                output_path="document.pdf",
                parameters={
                    "margin": 1.0,
                    "orientation": "landscape",
                    "page_size": "A4"
                }
            )
            
            # Convert a CSV file to Excel with custom parameters
            result = engine.convert_file(
                input_path="data.csv",
                output_path="data.xlsx",
                parameters={
                    "delimiter": ";",
                    "sheet_name": "Data",
                    "encoding": "utf-8"
                }
            )
            
            # Convert an image with quality settings
            result = engine.convert_file(
                input_path="image.png",
                output_path="image.jpg",
                parameters={"quality": 85, "progressive": True}
            )
        """
        input_path = Path(input_path)
        output_path = Path(output_path)
        parameters = parameters or {}
        
        # Validate input file
        validate_file_path(input_path, must_exist=True)
        
        # Check file size
        file_size_mb = get_file_size_mb(input_path)
        if file_size_mb > self.max_file_size_mb:
            raise ConversionError(
                f"File size ({file_size_mb:.2f}MB) exceeds maximum allowed "
                f"({self.max_file_size_mb}MB)"
            )
        
        # Determine input and output formats
        input_format = get_file_format(input_path)
        output_format = get_file_format(output_path)
        
        if not input_format:
            raise ConversionError(
                f"Could not determine format of input file: {input_path}. "
                f"Please ensure the file has a recognized extension."
            )
        
        if not output_format:
            raise ConversionError(
                f"Could not determine format of output file: {output_path}. "
                f"Please ensure the file has a recognized extension."
            )
        
        logger.info(f"Converting {input_path} ({input_format}) to {output_path} ({output_format})")
        
        # Find converter or multi-step conversion path
        conversion_path = self.registry.find_conversion_path(input_format, output_format)
        if not conversion_path:
            raise ConversionError(
                f"No conversion path found for {input_format} to {output_format}. "
                f"This conversion path is not supported."
            )
            
        logger.debug(f"Found conversion path with {len(conversion_path)} steps")
        
        # Create temporary directory for conversion
        try:
            temp_dir = self._create_temp_dir()
            
            # Perform direct or multi-step conversion
            if len(conversion_path) == 1:
                # Single-step (direct) conversion
                result = conversion_path[0].convert(
                    input_path=input_path,
                    output_path=output_path,
                    temp_dir=temp_dir,
                    parameters=parameters
                )
            else:
                # Multi-step conversion
                result = self._perform_multi_step_conversion(
                    conversion_path=conversion_path,
                    input_path=input_path,
                    output_path=output_path,
                    temp_dir=temp_dir,
                    parameters=parameters
                )
            
            # Clean up
            if not self.preserve_temp:
                self._cleanup_temp_dir(temp_dir)
            
            return result
        
        except Exception as e:
            logger.exception(f"Error during conversion: {str(e)}")
            raise ConversionError(f"Conversion failed: {str(e)}")
    
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
            input_format (str): Input file format (e.g., "docx", "csv", "jpg").
                Format names are case-insensitive.
            
            output_format (str): Output file format (e.g., "pdf", "xlsx", "png").
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
              organized by output format. Each parameter includes:
              * type: The parameter type (string, number, boolean, etc.)
              * description: A description of the parameter
              * default: The default value if not specified
              * Additional type-specific metadata (e.g., min/max for numbers,
                options for string enums)
        
        Example:
            # Get information about DOCX to PDF conversion
            info = engine.get_conversion_info("docx", "pdf")
            if info:
                print(f"Converter: {info['converter_name']}")
                print("Parameters:")
                for name, details in info['parameters'].get("pdf", {}).items():
                    print(f"  {name}: {details['description']}")
                    print(f"    Default: {details['default']}")
            else:
                print("Conversion from DOCX to PDF is not supported")
            
            # Check if a conversion is supported before attempting it
            if engine.get_conversion_info("csv", "json"):
                result = engine.convert_file("data.csv", "data.json")
            else:
                print("CSV to JSON conversion is not supported")
        """
        converter = self.registry.get_converter(input_format, output_format)
        if not converter:
            return None
        
        return {
            "input_format": input_format,
            "output_format": output_format,
            "converter_name": converter.__class__.__name__,
            "description": converter.__doc__ or "No description available",
            "parameters": converter.get_parameters(),
        }
    
    def get_supported_conversions(self) -> Dict[str, List[str]]:
        """Get all supported conversion combinations.
        
        Provides a comprehensive map of all available conversion paths in the system.
        This is useful for discovering what conversions are possible with the
        currently loaded converters.
        
        Returns:
            Dict[str, List[str]]: Dictionary mapping input formats to lists of
            supported output formats. The keys are input format names (lowercase)
            and the values are lists of output format names (lowercase) that
            the input can be converted to.
            
        Example:
            # Get all supported conversions
            conversions = engine.get_supported_conversions()
            
            # Print all available conversion paths
            for input_format, output_formats in conversions.items():
                print(f"{input_format} can be converted to: {', '.join(output_formats)}")
            
            # Check if a specific conversion path exists
            if "docx" in conversions and "pdf" in conversions["docx"]:
                print("DOCX to PDF conversion is supported")
            
            # Find all formats that can be converted to PDF
            pdf_sources = [fmt for fmt, outputs in conversions.items() if "pdf" in outputs]
            print(f"These formats can be converted to PDF: {', '.join(pdf_sources)}")
            
            # Print available output formats for DOCX files
            if "docx" in conversions:
                print(f"DOCX can be converted to: {', '.join(conversions['docx'])}")
        """
        return self.registry.get_conversion_map()
    
    def _create_temp_dir(self) -> Path:
        """Create a temporary directory for the conversion process.
        
        Creates a temporary directory that will be used to store intermediate
        files during the conversion process. If a custom temporary directory
        is specified in the configuration, it will be used as the base directory.
        
        Each conversion operation gets its own isolated temporary directory
        to prevent conflicts between concurrent conversions and to simplify
        cleanup.
        
        Returns:
            Path: Path to the created temporary directory as a Path object.
            This directory is guaranteed to exist and be writable.
        
        Note:
            The directory is created with a "fileconverter_" prefix for easier
            identification and cleanup. The directory will be automatically
            cleaned up after the conversion unless preserve_temp is set to True
            in the configuration.
            
        TODO:
            - Add support for custom temp directory naming schemes
            - Implement periodic cleanup of abandoned temp directories
        """
        base_temp = self.temp_dir or tempfile.gettempdir()
        temp_dir = Path(tempfile.mkdtemp(prefix="fileconverter_", dir=base_temp))
        logger.debug(f"Created temporary directory: {temp_dir}")
        return temp_dir
        
    def _perform_multi_step_conversion(
        self,
        conversion_path: List[BaseConverter],
        input_path: Path,
        output_path: Path,
        temp_dir: Path,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform a multi-step conversion through intermediate formats.
        
        This method handles conversions that require multiple steps because
        a direct converter is not available. It creates temporary files for
        each intermediate step and chains the conversions together.
        
        Args:
            conversion_path: List of converters forming the conversion path.
            input_path: Path to the input file.
            output_path: Path where the final output will be saved.
            temp_dir: Directory for temporary files.
            parameters: Conversion parameters.
            
        Returns:
            Dictionary with information about the conversion.
            
        Raises:
            ConversionError: If any step of the conversion fails.
        """
        if not conversion_path:
            raise ConversionError("Empty conversion path")
            
        # Path must have at least 2 steps for multi-step conversion
        if len(conversion_path) < 2:
            raise ConversionError("Not a multi-step conversion path")
            
        logger.info(f"Performing multi-step conversion with {len(conversion_path)} steps")
        
        # Create temporary files for intermediate steps
        current_input = input_path
        steps_info = []
        final_result = None
        
        # Get all formats in the path
        formats = []
        for i, converter in enumerate(conversion_path):
            if i == 0:  # First converter
                in_fmt = converter.get_input_formats()[0]  # Use first supported format
                out_fmt = converter.get_output_formats()[0]  # Use first supported format
                formats.extend([in_fmt, out_fmt])
            else:  # Subsequent converters
                out_fmt = converter.get_output_formats()[0]  # Use first supported format
                formats.append(out_fmt)
                
        # Ensure each converter in the path can handle the expected formats
        for i, converter in enumerate(conversion_path):
            in_fmt = formats[i]
            out_fmt = formats[i+1]
            if in_fmt not in converter.get_input_formats():
                raise ConversionError(f"Converter {converter.__class__.__name__} cannot handle input format {in_fmt}")
            if out_fmt not in converter.get_output_formats():
                raise ConversionError(f"Converter {converter.__class__.__name__} cannot handle output format {out_fmt}")
        
        try:
            # Perform each conversion step
            for i, converter in enumerate(conversion_path):
                # Last step writes to the final output path, others to temp files
                is_last_step = (i == len(conversion_path) - 1)
                current_output = output_path if is_last_step else temp_dir / f"step_{i}.{formats[i+1]}"
                
                # Perform conversion for this step
                step_result = converter.convert(
                    input_path=current_input,
                    output_path=current_output,
                    temp_dir=temp_dir,
                    parameters=parameters
                )
                
                steps_info.append({
                    "step": i + 1,
                    "converter": converter.__class__.__name__,
                    "input_format": step_result["input_format"],
                    "output_format": step_result["output_format"],
                })
                
                # Save the final result
                if is_last_step:
                    final_result = step_result
                
                # Update input for next step
                current_input = current_output
                
            # Create composite result
            if final_result:
                final_result["steps"] = steps_info
                final_result["multi_step"] = True
                final_result["step_count"] = len(conversion_path)
                return final_result
            else:
                raise ConversionError("Multi-step conversion failed: No final result")
                
        except Exception as e:
            logger.exception(f"Error during multi-step conversion: {str(e)}")
            raise ConversionError(f"Multi-step conversion failed: {str(e)}")
    
    def _cleanup_temp_dir(self, temp_dir: Path) -> None:
        """Clean up the temporary directory.
        
        Removes the temporary directory and all its contents after a conversion
        has completed. This ensures that no unnecessary temporary files are
        left on the user's system, conserving disk space and maintaining tidiness.
        
        The cleanup is skipped if the preserve_temp configuration option is
        set to True, which can be useful for debugging or for examining
        intermediate files.
        
        Args:
            temp_dir (Path): Path to the temporary directory to clean up.
                This should be a directory created by _create_temp_dir().
        
        Note:
            If cleanup fails for any reason (e.g., permission issues, file locks),
            a warning will be logged but no exception will be raised to allow
            the conversion operation to complete successfully. The warning includes
            the path to the directory so the user can manually clean it up later.
            
        TODO:
            - Add a method to bulk clean up all preserved temp directories
            - Improve handling of file locks on Windows systems
        """
        if temp_dir.exists():
            try:
                shutil.rmtree(temp_dir)
                logger.debug(f"Removed temporary directory: {temp_dir}")
            except OSError as e:
                logger.warning(f"Failed to remove temporary directory {temp_dir}: {str(e)}")
                logger.warning("The directory will need to be manually cleaned up.")
            except Exception as e:
                logger.warning(f"Unexpected error cleaning up {temp_dir}: {str(e)}")
                logger.warning("The directory may need to be manually cleaned up.")
