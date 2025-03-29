"""
Converter modules package for the Universal File Format Converter.

This package contains modules for converting between different file formats.
Each module should register its converters with the main converter registry.

To create a new converter module:
1. Create a new Python file in the 'converters' directory
2. Import the register_converter function from format_converter
3. Implement converter functions
4. Register your converters using register_converter

Example:
    # converters/custom_converters.py
    from format_converter import register_converter
    
    def my_converter(input_path, output_path):
        # Conversion logic here
        pass
    
    register_converter('my_format', 'target_format', my_converter)
"""

# This package intentionally left empty - modules are discovered and loaded dynamically
