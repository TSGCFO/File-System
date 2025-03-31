"""
Converter registry for FileConverter.

This module provides a registry for file format converters,
allowing the system to discover and manage available converters.
"""

import importlib
import inspect
import pkgutil
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Type, Tuple, Union, cast

from fileconverter.config import get_config
from fileconverter.utils.logging_utils import get_logger

logger = get_logger(__name__)

# Type for a converter class (abstract definition)
class BaseConverter:
    """Base class for format converters."""
    
    @classmethod
    def get_input_formats(cls) -> List[str]:
        """Get the list of input formats supported by this converter."""
        raise NotImplementedError
    
    @classmethod
    def get_output_formats(cls) -> List[str]:
        """Get the list of output formats supported by this converter."""
        raise NotImplementedError
    
    @classmethod
    def get_format_extensions(cls, format_name: str) -> List[str]:
        """Get the list of file extensions for a specific format."""
        raise NotImplementedError
    
    def convert(
        self, 
        input_path: Any, 
        output_path: Any, 
        temp_dir: Any,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert a file from one format to another."""
        raise NotImplementedError
    
    def get_parameters(self) -> Dict[str, Dict[str, Any]]:
        """Get the parameters supported by this converter."""
        raise NotImplementedError


# Type alias for converter class
ConverterClass = Type[BaseConverter]


class ConverterRegistry:
    """Registry for file format converters."""

    def __init__(self) -> None:
        """Initialize the converter registry."""
        self._converters: Dict[str, Dict[str, ConverterClass]] = defaultdict(dict)
        self._format_info: Dict[str, Dict[str, Any]] = {}
        self._format_extensions: Dict[str, List[str]] = {}
        self._instances: Dict[Tuple[str, str], BaseConverter] = {}
        
        # Load all converters
        self._load_converters()
    
    def _load_converters(self) -> None:
        """Discover and register all available converters."""
        logger.debug("Loading converters...")
        
        # Import converter modules
        import fileconverter.converters
        
        # Get configuration to check which converters are enabled
        config = get_config()
        
        # Find all modules in the converters package
        for _, name, is_pkg in pkgutil.iter_modules(fileconverter.converters.__path__):
            # Check if this converter category is enabled
            category_enabled = config.get("converters", name, "enabled", default=True)
            if not category_enabled:
                logger.info(f"Converter category '{name}' is disabled")
                continue
            
            try:
                # Import the module
                module = importlib.import_module(f"fileconverter.converters.{name}")
                
                # Find all classes in the module that have the required methods
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    
                    # Skip if not a class or same as BaseConverter
                    if (not inspect.isclass(attr) or 
                        attr.__name__ == "BaseConverter" or 
                        not issubclass(attr, BaseConverter)):
                        continue
                    
                    # Skip abstract classes
                    if inspect.isabstract(attr):
                        continue
                    
                    # Register the converter
                    self._register_converter(cast(ConverterClass, attr))
            
            except Exception as e:
                logger.error(f"Error loading converter module '{name}': {str(e)}")
        
        logger.debug(f"Loaded {len(self._converters)} converter categories")
    
    def _register_converter(self, converter_class: ConverterClass) -> None:
        """Register a converter class.
        
        Args:
            converter_class: The converter class to register.
        """
        try:
            # Get supported formats
            input_formats = converter_class.get_input_formats()
            output_formats = converter_class.get_output_formats()
            
            converter_name = converter_class.__name__
            
            if not input_formats or not output_formats:
                logger.warning(f"Converter {converter_name} doesn't specify supported formats")
                return
            
            # Register format extensions
            for format_name in set(input_formats + output_formats):
                if format_name not in self._format_extensions:
                    extensions = converter_class.get_format_extensions(format_name)
                    if extensions:
                        self._format_extensions[format_name] = extensions
            
            # Register the converter for each input-output format pair
            for input_format in input_formats:
                for output_format in output_formats:
                    if input_format == output_format:
                        continue  # Skip self-conversion
                    
                    self._converters[input_format][output_format] = converter_class
                    logger.debug(
                        f"Registered converter {converter_name} for "
                        f"{input_format} -> {output_format}"
                    )
        
        except Exception as e:
            logger.error(
                f"Error registering converter {converter_class.__name__}: {str(e)}"
            )
    
    def get_converter(
        self, 
        input_format: str, 
        output_format: str
    ) -> Optional[BaseConverter]:
        """Get a converter instance for the specified formats.
        
        Args:
            input_format: Input file format.
            output_format: Output file format.
        
        Returns:
            A converter instance, or None if no suitable converter is found.
        """
        # Normalize format names
        input_format = input_format.lower()
        output_format = output_format.lower()
        
        # Check if converter is available
        if (
            input_format not in self._converters or
            output_format not in self._converters[input_format]
        ):
            logger.warning(
                f"No converter found for {input_format} -> {output_format}"
            )
            return None
        
        # Get or create converter instance
        converter_key = (input_format, output_format)
        if converter_key not in self._instances:
            converter_class = self._converters[input_format][output_format]
            self._instances[converter_key] = converter_class()
        
        return self._instances[converter_key]
    
    def get_conversion_map(self) -> Dict[str, List[str]]:
        """Get a mapping of all supported conversion combinations.
        
        Returns:
            Dictionary mapping input formats to lists of supported output formats.
        """
        result: Dict[str, List[str]] = {}
        
        for input_format, outputs in self._converters.items():
            result[input_format] = sorted(outputs.keys())
        
        return result
    
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
        # Collect all formats from registered converters
        formats_by_category: Dict[str, Set[str]] = defaultdict(set)
        
        # Import all converter modules to get format information
        import fileconverter.converters
        
        # Find all modules in the converters package
        for _, name, is_pkg in pkgutil.iter_modules(fileconverter.converters.__path__):
            if category and name != category:
                continue
                
            try:
                # Import the module
                module = importlib.import_module(f"fileconverter.converters.{name}")
                
                # Get format information
                if hasattr(module, "SUPPORTED_FORMATS"):
                    for format_name in module.SUPPORTED_FORMATS:
                        formats_by_category[name].add(format_name)
            
            except Exception as e:
                logger.error(f"Error loading format information from '{name}': {str(e)}")
        
        # Convert sets to sorted lists
        return {
            cat: sorted(formats)
            for cat, formats in formats_by_category.items()
        }
    
    def get_format_extensions(self, format_name: str) -> List[str]:
        """Get the file extensions for a specific format.
        
        Args:
            format_name: Name of the format.
        
        Returns:
            List of file extensions (without the dot).
        """
        return self._format_extensions.get(format_name.lower(), [])
