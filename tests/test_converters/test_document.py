"""
Tests for the document converter module.

This module contains unit tests for the document format converter.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# Add parent directory to path to ensure imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fileconverter.converters.document import DocumentConverter
from fileconverter.utils.error_handling import ConversionError


class DocumentConverterTests(unittest.TestCase):
    """Test cases for the DocumentConverter class."""
    
    def setUp(self):
        """Set up the test environment."""
        self.converter = DocumentConverter()
        
        # Create temporary directory for test files
        self.temp_dir = Path("tests/test_data/temp")
        self.temp_dir.mkdir(exist_ok=True, parents=True)
        
        # Define test file paths
        self.documents_dir = Path("tests/test_data/documents")
        self.documents_dir.mkdir(exist_ok=True, parents=True)
        
        # Create test files if they don't exist
        self.create_test_files()
    
    def tearDown(self):
        """Clean up after tests."""
        # Clean up temp files
        for file in self.temp_dir.glob("*"):
            try:
                file.unlink()
            except Exception:
                pass
    
    def create_test_files(self):
        """Create sample test files for the tests."""
        # Create a simple markdown file for testing
        md_file = self.documents_dir / "sample.md"
        if not md_file.exists():
            with open(md_file, "w") as f:
                f.write("# Sample Markdown\n\nThis is a sample markdown file for testing.\n\n* Item 1\n* Item 2\n")
        
        # Create a simple text file for testing
        txt_file = self.documents_dir / "sample.txt"
        if not txt_file.exists():
            with open(txt_file, "w") as f:
                f.write("Sample text file for testing.\n\nLine 1\nLine 2\n")
        
        # Create a simple HTML file for testing
        html_file = self.documents_dir / "sample.html"
        if not html_file.exists():
            with open(html_file, "w") as f:
                f.write("<!DOCTYPE html>\n<html><head><title>Sample</title></head><body><h1>Sample HTML</h1><p>This is sample content.</p></body></html>")
    
    def test_get_input_formats(self):
        """Test that the input formats list is correct."""
        formats = self.converter.get_input_formats()
        self.assertIsInstance(formats, list)
        self.assertTrue(len(formats) > 0)
        self.assertIn("md", formats)
        self.assertIn("txt", formats)
        self.assertIn("html", formats)
    
    def test_get_output_formats(self):
        """Test that the output formats list is correct."""
        formats = self.converter.get_output_formats()
        self.assertIsInstance(formats, list)
        self.assertTrue(len(formats) > 0)
        self.assertIn("html", formats)
        self.assertIn("pdf", formats)
    
    def test_get_format_extensions(self):
        """Test that format extensions are correctly returned."""
        html_exts = self.converter.get_format_extensions("html")
        self.assertIn("html", html_exts)
        self.assertIn("htm", html_exts)
        
        md_exts = self.converter.get_format_extensions("md")
        self.assertIn("md", md_exts)
        self.assertIn("markdown", md_exts)
    
    def test_get_format_from_extension(self):
        """Test getting format from extension."""
        self.assertEqual("html", self.converter._get_format_from_extension("html"))
        self.assertEqual("html", self.converter._get_format_from_extension("htm"))
        self.assertEqual("md", self.converter._get_format_from_extension("md"))
        self.assertEqual("md", self.converter._get_format_from_extension("markdown"))
    
    def test_convert_markdown_to_html(self):
        """Test converting Markdown to HTML."""
        input_path = self.documents_dir / "sample.md"
        output_path = self.temp_dir / "output.html"
        
        if not input_path.exists():
            self.skipTest("Test Markdown file does not exist")
        
        # Mock the markdown module to avoid dependency issues
        with patch("markdown.markdown", return_value="<h1>Sample Markdown</h1>"):
            result = self.converter._convert_markdown_to_html(input_path, output_path, {})
            
            self.assertEqual("md", result["input_format"])
            self.assertEqual("html", result["output_format"])
            self.assertTrue(output_path.exists())
    
    def test_convert_text_to_html(self):
        """Test converting plain text to HTML."""
        input_path = self.documents_dir / "sample.txt"
        output_path = self.temp_dir / "output.html"
        
        if not input_path.exists():
            self.skipTest("Test text file does not exist")
        
        result = self.converter._convert_text_to_html(input_path, output_path, {})
        
        self.assertEqual("txt", result["input_format"])
        self.assertEqual("html", result["output_format"])
        self.assertTrue(output_path.exists())
    
    @patch("subprocess.run")
    def test_convert_docx_to_pdf_with_libreoffice(self, mock_run):
        """Test converting DOCX to PDF using LibreOffice."""
        # Mock subprocess.run to avoid dependency on LibreOffice
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        # Create a temp file that exists
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_input:
            temp_input_path = temp_input.name
            
        try:
            input_path = Path(temp_input_path)
            output_path = Path(temp_input_path).with_suffix('.pdf')
            
            # Mock the file operations and imports
            with patch("builtins.open", mock_open()), \
                 patch("os.path.exists", return_value=True), \
                 patch("os.rename"), \
                 patch("importlib.import_module", side_effect=lambda x:
                       ImportError(f"No module named '{x}'") if x in ["weasyprint", "pdfkit"]
                       else unittest.mock.DEFAULT):
                
                # Test LibreOffice fallback
                result = self.converter._convert_docx_to_pdf(input_path, output_path, {})
                
                self.assertEqual("docx", result["input_format"])
                self.assertEqual("pdf", result["output_format"])
                
                # Check LibreOffice was called with correct arguments
                mock_run.assert_called_once()
                args = mock_run.call_args[0][0]
                self.assertIn("libreoffice", args)
                self.assertIn("--convert-to", args)
                self.assertIn("pdf", args)
        finally:
            # Clean up
            if os.path.exists(temp_input_path):
                os.unlink(temp_input_path)
    
    def test_convert_unsupported_format(self):
        """Test that conversion between unsupported formats raises an error."""
        # Create a temporary file with unsupported extension
        with tempfile.NamedTemporaryFile(suffix='.abc') as temp_input:
            input_path = Path(temp_input.name)
            output_path = Path(temp_input.name).with_suffix('.xyz')
            
            with self.assertRaises(ConversionError):
                self.converter.convert(input_path, output_path, Path(tempfile.gettempdir()), {})
    
    def test_get_parameters(self):
        """Test that parameters are correctly returned."""
        params = self.converter.get_parameters()
        
        self.assertIn("pdf", params)
        self.assertIn("html", params)
        self.assertIn("docx", params)
        
        # Check PDF parameters
        pdf_params = params["pdf"]
        self.assertIn("page_size", pdf_params)
        self.assertIn("orientation", pdf_params)
        
        # Check HTML parameters
        html_params = params["html"]
        self.assertIn("css", html_params)
        self.assertIn("template", html_params)


if __name__ == "__main__":
    unittest.main()