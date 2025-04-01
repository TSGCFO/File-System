"""
Converter registry for FileConverter.

This module provides a registry for file format converters,
allowing the system to discover and manage available converters.

The ConverterRegistry is a central component of the FileConverter system
that implements the Service Locator pattern. It automatically discovers
and registers converter implementations from the converters package,
provides a lookup mechanism to find appropriate converters for specific
format pairs, and maintains information about supported file formats.

Key components:
- BaseConverter: Abstract base class defining the interface for all converters
- ConverterRegistry: Registry that manages converter discovery and lookup
- ConverterClass: Type alias for converter class types

The registry provides methods to:
- Find converters capable of converting between specific format pairs
- Get information about supported formats and their file extensions
- Discover available conversion paths in the system

This module is used by the ConversionEngine to find appropriate converters
for requested conversions. It handles the dynamic discovery and registration
of converters, allowing for easy extension of the system with new format
support without modifying the core engine.
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
    """Base class for format converters.
    
    This abstract base class defines the interface that all converter
    implementations must adhere to. Converters are responsible for
    handling the actual conversion between specific file formats.
    
    Each converter:
    - Declares which input formats it can read
    - Declares which output formats it can write
    - Provides information about file extensions for each format
    - Implements the conversion logic
    - Defines the parameters it accepts
    
    Converters are automatically discovered and registered by the
    ConverterRegistry through introspection of modules in the
    converters package.
    
    When implementing a custom converter, you must override all the methods
    in this class with concrete implementations.
    """
    
    @classmethod
    def get_input_formats(cls) -> List[str]:
        """Get the list of input formats supported by this converter.
        
        This method should return a list of format names (lowercase) that
        this converter can accept as input. Format names should be
        standardized across the application (e.g., "docx", "pdf", "jpg").
        
        Returns:
            List[str]: A list of format names supported as input.
            
        Example implementation:
            @classmethod
            def get_input_formats(cls) -> List[str]:
                return ["docx", "rtf", "odt"]
        """
        raise NotImplementedError("Converter must implement get_input_formats")
    
    @classmethod
    def get_output_formats(cls) -> List[str]:
        """Get the list of output formats supported by this converter.
        
        This method should return a list of format names (lowercase) that
        this converter can produce as output. Format names should be
        standardized across the application.
        
        Returns:
            List[str]: A list of format names supported as output.
            
        Example implementation:
            @classmethod
            def get_output_formats(cls) -> List[str]:
                return ["pdf", "html", "txt"]
        """
        raise NotImplementedError("Converter must implement get_output_formats")
    
    @classmethod
    def get_format_extensions(cls, format_name: str) -> List[str]:
        """Get the list of file extensions for a specific format.
        
        This method should return a list of file extensions (without the dot)
        that correspond to the specified format name. This information is used
        by the system to determine the format of files based on their extension.
        
        Args:
            format_name (str): The name of the format to get extensions for.
                This name should match one of the formats returned by
                get_input_formats or get_output_formats.
                
        Returns:
            List[str]: A list of file extensions (without the dot) for the
                specified format. For example, for "docx" this might return
                ["docx"]. For "html" it might return ["html", "htm"].
                
        Example implementation:
            @classmethod
            def get_format_extensions(cls, format_name: str) -> List[str]:
                format_map = {
                    "docx": ["docx"],
                    "pdf": ["pdf"],
                    "html": ["html", "htm"],
                }
                return format_map.get(format_name.lower(), [])
        """
        raise NotImplementedError("Converter must implement get_format_extensions")
    
    def convert(
        self,
        input_path: Any,
        output_path: Any,
        temp_dir: Any,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert a file from one format to another.
        
        This is the core method that performs the actual conversion. It should
        read the input file, transform it to the desired output format, and
        write the result to the output file.
        
        Args:
            input_path: Path to the input file. This is typically a Path object
                but can be any type that the converter can handle.
            output_path: Path where the output file should be written. This is
                typically a Path object but can be any type that the converter
                can handle.
            temp_dir: Directory for temporary files. This is typically a Path
                object pointing to a directory that the converter can use for
                storing intermediate files during the conversion process.
            parameters: Dictionary of parameters that control the conversion.
                The specific parameters depend on the converter and the formats
                involved. The converter should document its supported parameters
                through the get_parameters method.
                
        Returns:
            Dict[str, Any]: A dictionary with information about the conversion.
                This should include at minimum:
                - input_format: The detected input format
                - output_format: The output format produced
                - input_path: The path to the input file
                - output_path: The path to the output file
                The converter may include additional information specific to the
                conversion, such as page count, dimensions, or processing time.
                
        Raises:
            ConversionError: If the conversion fails for any reason. The
                exception message should provide details about the failure.
                
        Example implementation:
            def convert(self, input_path, output_path, temp_dir, parameters):
                try:
                    # Read input file
                    with open(input_path, 'r') as f:
                        content = f.read()
                    
                    # Transform content
                    transformed = self._process_content(content, parameters)
                    
                    # Write output file
                    with open(output_path, 'w') as f:
                        f.write(transformed)
                    
                    return {
                        "input_format": "txt",
                        "output_format": "html",
                        "input_path": str(input_path),
                        "output_path": str(output_path),
                        "characters": len(content)
                    }
                except Exception as e:
                    raise ConversionError(f"Failed to convert: {str(e)}")
        """
        raise NotImplementedError("Converter must implement convert")
    
    def get_parameters(self) -> Dict[str, Dict[str, Any]]:
        """Get the parameters supported by this converter.
        
        This method should return a dictionary describing the parameters that
        this converter accepts. The dictionary is organized by output format,
        allowing different parameters for different output formats.
        
        Returns:
            Dict[str, Dict[str, Any]]: A dictionary with output formats as keys
                and parameter specifications as values. Each parameter specification
                is a dictionary with parameter names as keys and parameter details
                as values. Parameter details should include:
                - type: The parameter type (string, number, boolean, etc.)
                - description: A human-readable description of the parameter
                - default: The default value if not specified
                - Additional type-specific metadata (e.g., min/max for numbers,
                  options for string enums)
                  
        Example implementation:
            def get_parameters(self) -> Dict[str, Dict[str, Any]]:
                return {
                    "pdf": {
                        "margin": {
                            "type": "number",
                            "description": "Page margin in inches",
                            "default": 1.0,
                            "min": 0.0,
                            "max": 3.0,
                        },
                        "orientation": {
                            "type": "string",
                            "description": "Page orientation",
                            "default": "portrait",
                            "options": ["portrait", "landscape"],
                        },
                    },
                    "html": {
                        "css": {
                            "type": "string",
                            "description": "CSS file path or content",
                            "default": None,
                        },
                    },
                }
        """
        raise NotImplementedError("Converter must implement get_parameters")


# Type alias for converter class
ConverterClass = Type[BaseConverter]


class ConverterRegistry:
    """Registry for file format converters.
    
    The ConverterRegistry is responsible for discovering, registering, and
    providing access to converter implementations. It scans the converters
    package for classes that implement the BaseConverter interface and
    registers them for the format combinations they support.
    
    The registry enables the ConversionEngine to find appropriate converters
    for requested conversions without needing to know the specific converter
    implementations. This decoupling allows the system to be easily extended
    with new format support by simply adding new converter implementations.
    
    The registry implements the Service Locator design pattern, providing a
    central point for discovering and accessing services (converters) based
    on their capabilities rather than their concrete implementations.
    """

    def __init__(self) -> None:
        """Initialize the converter registry."""
        self._converters: Dict[str, Dict[str, ConverterClass]] = defaultdict(dict)
        self._format_info: Dict[str, Dict[str, Any]] = {}
        self._format_extensions: Dict[str, List[str]] = {}
        self._instances: Dict[Tuple[str, str], BaseConverter] = {}
        
        # Load all converters
        self._load_converters()
    
    def _load_converters(self) -> None:
        """Discover and register all available converters.
        
        This method scans the converters package for modules containing
        converter implementations, imports each module, and registers any
        classes that implement the BaseConverter interface. It uses Python's
        introspection capabilities to dynamically discover converters without
        requiring explicit registration.
        
        The method checks the configuration to determine if specific converter
        categories are enabled or disabled. If a category is disabled in the
        configuration, its converters will not be registered.
        
        This automatic discovery mechanism allows new converters to be added
        to the system simply by placing them in the converters package, without
        requiring changes to the registry or engine code.
        
        Note:
            This method is called automatically during registry initialization.
            It doesn't need to be called manually unless you want to refresh the
            list of converters (e.g., after adding new converters at runtime).
            
        TODO:
            - Add support for third-party converter plugins from external packages
            - Implement converter versioning and dependency management
            - Add converter priority/ranking for format pairs with multiple converters
        """
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
        
        This method registers a converter class for the format combinations
        it supports. It queries the converter for its supported input and
        output formats, and registers it for each valid input-output pair.
        It also collects information about file extensions for each format.
        
        Args:
            converter_class (ConverterClass): The converter class to register.
                This should be a class that implements the BaseConverter interface.
                
        Note:
            - The converter is not registered for self-conversion (same input
              and output format), as these are assumed to be trivial.
            - If a converter doesn't specify any supported formats, a warning
              is logged and the converter is not registered.
            - If an error occurs while registering a converter, it is logged
              but doesn't prevent other converters from being registered.
              
        TODO:
            - Add support for converter priority to handle multiple converters
              for the same format pair
            - Implement validation of converter implementations
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
        
        This method finds and returns a converter capable of converting from
        the specified input format to the specified output format. If multiple
        converters are available for the format pair, the first one registered
        is returned (in future versions, this might be based on priority).
        
        The method normalizes format names to lowercase to ensure case-insensitive
        matching. It also implements a caching mechanism to reuse converter
        instances for better performance and memory efficiency.
        
        Args:
            input_format (str): Input file format (e.g., "docx", "csv").
                Format names are case-insensitive.
            output_format (str): Output file format (e.g., "pdf", "xlsx").
                Format names are case-insensitive.
        
        Returns:
            Optional[BaseConverter]: A converter instance capable of performing
                the requested conversion, or None if no suitable converter is found.
                
        Example:
            # Get a converter for DOCX to PDF conversion
            converter = registry.get_converter("docx", "pdf")
            if converter:
                result = converter.convert("document.docx", "document.pdf", temp_dir, {})
            else:
                print("Conversion not supported")
                
        Note:
            Converters are instantiated on demand and cached for reuse. Each
            format pair gets its own converter instance, which allows converters
            to maintain state specific to the format pair if needed.
        """
        # Normalize format names
        input_format = input_format.lower()
        output_format = output_format.lower()
        
        # Same format means identity conversion (no conversion needed)
        if input_format == output_format:
            # For identity conversions, we can create a simple pass-through converter
            # This allows formats to be used in multi-step conversion chains
            return self._get_identity_converter(input_format)
        
        # Check if direct converter is available
        if (
            input_format in self._converters and
            output_format in self._converters[input_format]
        ):
            # Get or create converter instance
            converter_key = (input_format, output_format)
            if converter_key not in self._instances:
                converter_class = self._converters[input_format][output_format]
                self._instances[converter_key] = converter_class()
            
            return self._instances[converter_key]
        
        logger.warning(f"No direct converter found for {input_format} -> {output_format}")
        return None
        
    def _get_identity_converter(self, format_name: str) -> BaseConverter:
        """Get or create an identity converter for the specified format.
        
        An identity converter simply copies the input file to the output file
        without performing any actual conversion. This is useful for multi-step
        conversions where some steps might be identity conversions.
        
        Args:
            format_name (str): Format name for the identity converter.
            
        Returns:
            BaseConverter: An identity converter instance.
        """
        converter_key = (format_name, format_name)
        if converter_key not in self._instances:
            # Create a simple identity converter that just copies the file
            class IdentityConverter(BaseConverter):
                @classmethod
                def get_input_formats(cls) -> List[str]:
                    return [format_name]
                
                @classmethod
                def get_output_formats(cls) -> List[str]:
                    return [format_name]
                
                @classmethod
                def get_format_extensions(cls, fmt: str) -> List[str]:
                    return self.get_format_extensions(format_name)
                
                def convert(self, input_path, output_path, temp_dir, parameters):
                    import shutil
                    shutil.copy2(input_path, output_path)
                    return {
                        "input_format": format_name,
                        "output_format": format_name,
                        "input_path": str(input_path),
                        "output_path": str(output_path),
                    }
                
                def get_parameters(self) -> Dict[str, Dict[str, Any]]:
                    return {}
            
            self._instances[converter_key] = IdentityConverter()
        
        return self._instances[converter_key]
        return self._instances[converter_key]
    
    def find_conversion_path(
        self,
        input_format: str,
        output_format: str,
        max_steps: int = 3
    ) -> List[BaseConverter]:
        """Find a conversion path between two formats.
        
        This method uses a breadth-first search algorithm to find the shortest
        path between the input and output formats. It can discover multi-step
        conversion paths when direct conversion is not available.
        
        Args:
            input_format (str): Input file format (e.g., "docx", "csv").
                Format names are case-insensitive.
            output_format (str): Output file format (e.g., "pdf", "xlsx").
                Format names are case-insensitive.
            max_steps (int): Maximum number of conversion steps to consider.
                Default is 3, which means at most 3 converters will be used.
                
        Returns:
            List[BaseConverter]: A list of converter instances that form the
                conversion path, or an empty list if no path is found.
                
        Example:
            # Find a path from XLSX to XML
            path = registry.find_conversion_path("xlsx", "xml")
            if path:
                print(f"Found path with {len(path)} steps")
                for i, converter in enumerate(path):
                    print(f"Step {i+1}: {converter.__class__.__name__}")
            else:
                print("No conversion path found")
        """
        # Normalize format names
        input_format = input_format.lower()
        output_format = output_format.lower()
        
        # Direct conversion
        direct_converter = self.get_converter(input_format, output_format)
        if direct_converter:
            return [direct_converter]
            
        # If max_steps is 1, we only want direct conversions
        if max_steps <= 1:
            return []
            
        # Get all available formats
        all_formats = set()
        for from_fmt in self._converters:
            all_formats.add(from_fmt)
            for to_fmt in self._converters[from_fmt]:
                all_formats.add(to_fmt)
        
        # Breadth-first search to find shortest path
        visited = set([input_format])
        queue = [(input_format, [])]  # (format, path so far)
        
        while queue:
            current_format, path = queue.pop(0)
            
            # Try all possible next steps
            for next_format in all_formats:
                if next_format in visited:
                    continue
                    
                # Check if converter exists for this step
                converter = self.get_converter(current_format, next_format)
                if not converter:
                    continue
                    
                # Create new path with this converter
                new_path = path + [converter]
                
                # Check if we've reached the target
                if next_format == output_format:
                    return new_path
                    
                # Check if we've reached max steps
                if len(new_path) >= max_steps:
                    continue
                    
                # Add to queue for further exploration
                visited.add(next_format)
                queue.append((next_format, new_path))
        
        # No path found
        return []
        
    def get_conversion_map(self) -> Dict[str, List[str]]:
        """Get a mapping of all supported conversion combinations.
        
        This method provides a comprehensive view of all available conversion
        paths in the system. It returns a dictionary where each key is an input
        format and the corresponding value is a list of output formats that the
        input can be converted to.
        
        This information can be used to:
        - Display available conversion options to users
        - Determine if a requested conversion is possible
        - Find multi-step conversion paths when direct conversion isn't available
        
        Returns:
            Dict[str, List[str]]: Dictionary mapping input formats to lists of
                supported output formats. Format names are lowercase.
                
        Example:
            # Get all supported conversions
            conversion_map = registry.get_conversion_map()
            
            # Check if a conversion is supported
            if "docx" in conversion_map and "pdf" in conversion_map["docx"]:
                print("DOCX to PDF conversion is supported")
                
            # Display all supported conversions
            for input_format, output_formats in conversion_map.items():
                print(f"{input_format} -> {', '.join(output_formats)}")
        """
        result: Dict[str, List[str]] = {}
        
        for input_format, outputs in self._converters.items():
            result[input_format] = sorted(outputs.keys())
        
        return result
    
    def get_supported_formats(
        self,
        category: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """Get all supported file formats grouped by category.
        
        This method collects information about supported formats from all
        registered converters and organizes them by category. Each category
        corresponds to a module in the converters package (e.g., document,
        spreadsheet, image).
        
        The method uses the SUPPORTED_FORMATS constant defined in each
        converter module to determine which formats belong to which category.
        
        Args:
            category (Optional[str]): Optional category to filter formats.
                If provided, only formats in the specified category are
                returned. If None, formats from all categories are returned.
        
        Returns:
            Dict[str, List[str]]: Dictionary mapping format categories to lists
                of format names. Format names are sorted alphabetically within
                each category.
                
        Example:
            # Get all supported formats
            all_formats = registry.get_supported_formats()
            
            # Get only document formats
            document_formats = registry.get_supported_formats("document")
            
            # Display supported formats by category
            for category, formats in registry.get_supported_formats().items():
                print(f"{category}: {', '.join(formats)}")
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
        
        This method returns a list of file extensions that correspond to the
        specified format name. This information is used by the system to
        determine the format of files based on their extension, and to generate
        appropriate file filters for file dialogs.
        
        Args:
            format_name (str): Name of the format (e.g., "docx", "pdf").
                Format names are case-insensitive.
        
        Returns:
            List[str]: List of file extensions (without the dot) for the
                specified format. For example, for "html" this might return
                ["html", "htm"]. If the format is not recognized, an empty
                list is returned.
                
        Example:
            # Get extensions for the PDF format
            pdf_extensions = registry.get_format_extensions("pdf")  # ["pdf"]
            
            # Generate a file filter for a file dialog
            format_name = "html"
            extensions = registry.get_format_extensions(format_name)
            filter_text = f"{format_name.upper()} Files"
            filter_pattern = " ".join(f"*.{ext}" for ext in extensions)
            file_filter = f"{filter_text} ({filter_pattern})"
            
        TODO:
            - Add capability to get all extensions for all formats
            - Implement format detection based on file content signature
        """
        return self._format_extensions.get(format_name.lower(), [])
