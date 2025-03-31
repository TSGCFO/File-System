"""
Tests for the core functionality of FileConverter.

This module contains unit tests for the core components of the FileConverter package,
including the ConversionEngine and ConverterRegistry classes.
"""

import os
import sys
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock

# Add parent directory to path to ensure imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fileconverter.core.engine import ConversionEngine
from fileconverter.core.registry import ConverterRegistry, BaseConverter
from fileconverter.utils.error_handling import ConversionError, ConfigError


class MockConverter(BaseConverter):
    """Mock converter for testing."""
    
    @classmethod
    def get_input_formats(cls):
        return ["mock_in", "test_in"]
    
    @classmethod
    def get_output_formats(cls):
        return ["mock_out", "test_out"]
    
    @classmethod
    def get_format_extensions(cls, format_name):
        return ["mock", "test"]
    
    def convert(self, input_path, output_path, temp_dir, parameters):
        # Create an empty output file for testing
        with open(output_path, "w") as f:
            f.write("Mock converted content")
        
        return {
            "input_format": "mock_in",
            "output_format": "mock_out",
            "input_path": str(input_path),
            "output_path": str(output_path),
        }
    
    def get_parameters(self):
        return {
            "mock_param": {
                "type": "string",
                "description": "Mock parameter",
                "default": "mock_value",
            }
        }


class ConverterRegistryTests(unittest.TestCase):
    """Test cases for the ConverterRegistry class."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a registry with a mock converter
        self.registry = ConverterRegistry()
        
        # Register the mock converter manually
        self.registry._register_converter(MockConverter)
    
    def test_get_converter(self):
        """Test getting a converter for a specific format pair."""
        # Test getting a registered converter
        converter = self.registry.get_converter("mock_in", "mock_out")
        self.assertIsNotNone(converter)
        self.assertIsInstance(converter, MockConverter)
        
        # Test getting a non-existent converter
        converter = self.registry.get_converter("nonexistent", "format")
        self.assertIsNone(converter)
    
    def test_get_conversion_map(self):
        """Test getting the conversion map."""
        conversion_map = self.registry.get_conversion_map()
        
        self.assertIn("mock_in", conversion_map)
        self.assertIn("test_in", conversion_map)
        
        self.assertIn("mock_out", conversion_map["mock_in"])
        self.assertIn("test_out", conversion_map["mock_in"])
    
    def test_get_supported_formats(self):
        """Test getting supported formats."""
        # Since this depends on the actual modules, mock the imports
        with patch("importlib.import_module") as mock_import:
            mock_module = MagicMock()
            mock_module.SUPPORTED_FORMATS = ["mock_format", "test_format"]
            mock_import.return_value = mock_module
            
            with patch("pkgutil.iter_modules", return_value=[
                (None, "test_category", False)
            ]):
                formats = self.registry.get_supported_formats()
                
                self.assertIn("test_category", formats)
                self.assertIn("mock_format", formats["test_category"])
                self.assertIn("test_format", formats["test_category"])
    
    def test_get_format_extensions(self):
        """Test getting format extensions."""
        extensions = self.registry.get_format_extensions("mock_in")
        self.assertIn("mock", extensions)
        self.assertIn("test", extensions)


class ConversionEngineTests(unittest.TestCase):
    """Test cases for the ConversionEngine class."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        
        # Create sample input files
        self.input_file = Path(self.temp_dir) / "input.mock_in"
        with open(self.input_file, "w") as f:
            f.write("Test content")
        
        # Create an engine with a mocked registry
        self.engine = ConversionEngine()
        
        # Create and attach a registry with our mock converter
        self.registry = MagicMock(spec=ConverterRegistry)
        self.mock_converter = MockConverter()
        
        # Set up the registry mock to return our mock converter
        self.registry.get_converter.return_value = self.mock_converter
        
        # Patch the registry creation in the engine
        patch_registry = patch.object(
            self.engine, "registry", 
            new_callable=PropertyMock, 
            return_value=self.registry
        )
        patch_registry.start()
        self.addCleanup(patch_registry.stop)
    
    def tearDown(self):
        """Clean up after tests."""
        # Clean up temp directory
        for file in Path(self.temp_dir).glob("*"):
            try:
                file.unlink()
            except Exception:
                pass
        
        try:
            os.rmdir(self.temp_dir)
        except Exception:
            pass
    
    def test_convert_file(self):
        """Test converting a file."""
        output_file = Path(self.temp_dir) / "output.mock_out"
        
        # Mock the file format detection
        with patch("fileconverter.core.engine.get_file_format") as mock_get_format:
            mock_get_format.side_effect = ["mock_in", "mock_out"]
            
            # Mock the file size check
            with patch("fileconverter.core.engine.get_file_size_mb", return_value=1.0):
                # Perform the conversion
                result = self.engine.convert_file(
                    input_path=self.input_file,
                    output_path=output_file
                )
                
                # Verify the conversion was performed
                self.registry.get_converter.assert_called_with("mock_in", "mock_out")
                self.mock_converter.convert.assert_called_once()
                
                # Check the output file exists
                self.assertTrue(output_file.exists())
    
    def test_convert_file_no_converter(self):
        """Test converting a file with no available converter."""
        output_file = Path(self.temp_dir) / "output.mock_out"
        
        # Mock the file format detection
        with patch("fileconverter.core.engine.get_file_format") as mock_get_format:
            mock_get_format.side_effect = ["mock_in", "mock_out"]
            
            # Mock the file size check
            with patch("fileconverter.core.engine.get_file_size_mb", return_value=1.0):
                # Make the registry return None for the converter
                self.registry.get_converter.return_value = None
                
                # Attempt the conversion
                with self.assertRaises(ConversionError):
                    self.engine.convert_file(
                        input_path=self.input_file,
                        output_path=output_file
                    )
    
    def test_convert_file_too_large(self):
        """Test converting a file that exceeds the size limit."""
        output_file = Path(self.temp_dir) / "output.mock_out"
        
        # Mock the file size check to exceed the limit
        with patch("fileconverter.core.engine.get_file_size_mb", return_value=1000.0):
            # Attempt the conversion
            with self.assertRaises(ConversionError):
                self.engine.convert_file(
                    input_path=self.input_file,
                    output_path=output_file
                )
    
    def test_get_conversion_info(self):
        """Test getting information about a conversion."""
        # Mock the converter's get_parameters method
        mock_params = {"param1": {"type": "string", "default": "value"}}
        self.mock_converter.get_parameters.return_value = mock_params
        
        # Get conversion info
        info = self.engine.get_conversion_info("mock_in", "mock_out")
        
        # Verify the correct info is returned
        self.assertEqual("mock_in", info["input_format"])
        self.assertEqual("mock_out", info["output_format"])
        self.assertEqual(self.mock_converter.__class__.__name__, info["converter_name"])
        self.assertEqual(mock_params, info["parameters"])


if __name__ == "__main__":
    unittest.main()