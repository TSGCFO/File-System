"""
Conversion engine for FileConverter.

This module provides the main conversion engine that orchestrates
the file conversion process.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from fileconverter.config import get_config
from fileconverter.core.registry import ConverterRegistry
from fileconverter.utils.error_handling import ConversionError
from fileconverter.utils.file_utils import get_file_format, get_file_size_mb
from fileconverter.utils.logging_utils import get_logger
from fileconverter.utils.validation import validate_file_path

logger = get_logger(__name__)


class ConversionEngine:
    """Main engine for converting files between formats."""

    def __init__(self, config_path: Optional[str] = None) -> None:
        """Initialize the conversion engine.
        
        Args:
            config_path: Optional path to a configuration file.
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
        
        Args:
            input_path: Path to the input file.
            output_path: Path where the output file will be saved.
            parameters: Optional parameters for the conversion.
        
        Returns:
            Dictionary with information about the conversion.
            
        Raises:
            ConversionError: If the conversion fails.
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
            raise ConversionError(f"Could not determine format of input file: {input_path}")
        
        if not output_format:
            raise ConversionError(f"Could not determine format of output file: {output_path}")
        
        logger.info(f"Converting {input_path} ({input_format}) to {output_path} ({output_format})")
        
        # Find converter for the formats
        converter = self.registry.get_converter(input_format, output_format)
        if not converter:
            raise ConversionError(
                f"No converter found for {input_format} to {output_format}"
            )
        
        # Create temporary directory for conversion
        try:
            temp_dir = self._create_temp_dir()
            
            # Perform conversion
            result = converter.convert(
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
        """Get information about a specific conversion.
        
        Args:
            input_format: Input file format.
            output_format: Output file format.
        
        Returns:
            Dictionary with information about the conversion, or None if
            the conversion is not supported.
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
        
        Returns:
            Dictionary mapping input formats to lists of supported output formats.
        """
        return self.registry.get_conversion_map()
    
    def _create_temp_dir(self) -> Path:
        """Create a temporary directory for the conversion process.
        
        Returns:
            Path to the temporary directory.
        """
        base_temp = self.temp_dir or tempfile.gettempdir()
        temp_dir = Path(tempfile.mkdtemp(prefix="fileconverter_", dir=base_temp))
        logger.debug(f"Created temporary directory: {temp_dir}")
        return temp_dir
    
    def _cleanup_temp_dir(self, temp_dir: Path) -> None:
        """Clean up the temporary directory.
        
        Args:
            temp_dir: Path to the temporary directory.
        """
        if temp_dir.exists():
            try:
                shutil.rmtree(temp_dir)
                logger.debug(f"Removed temporary directory: {temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary directory {temp_dir}: {str(e)}")
