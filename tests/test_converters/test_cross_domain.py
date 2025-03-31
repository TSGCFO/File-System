"""
Tests for cross-domain conversions between non-image formats.

These tests verify that conversions between different format domains
(spreadsheet, document, data exchange) work correctly.
"""

import os
import tempfile
from pathlib import Path

import pytest

from fileconverter.core.engine import ConversionEngine
from fileconverter.utils.error_handling import ConversionError

# Test data
SAMPLE_CSV_CONTENT = """id,name,value
1,Item 1,100
2,Item 2,200
3,Item 3,300
"""

SAMPLE_JSON_CONTENT = """[
  {"id": 1, "name": "Item 1", "value": 100},
  {"id": 2, "name": "Item 2", "value": 200},
  {"id": 3, "name": "Item 3", "value": 300}
]
"""

SAMPLE_XML_CONTENT = """<?xml version="1.0" encoding="UTF-8"?>
<data>
  <row>
    <id>1</id>
    <name>Item 1</name>
    <value>100</value>
  </row>
  <row>
    <id>2</id>
    <name>Item 2</name>
    <value>200</value>
  </row>
  <row>
    <id>3</id>
    <name>Item 3</name>
    <value>300</value>
  </row>
</data>
"""

@pytest.fixture
def engine():
    """Create a ConversionEngine instance for testing."""
    return ConversionEngine()

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

def create_test_file(path, content):
    """Create a test file with the given content."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path

def test_csv_to_docx_conversion(engine, temp_dir):
    """Test conversion from CSV to DOCX."""
    # Create test files
    input_path = create_test_file(temp_dir / "test.csv", SAMPLE_CSV_CONTENT)
    output_path = temp_dir / "test.docx"
    
    # Perform conversion
    result = engine.convert_file(input_path, output_path)
    
    # Check results
    assert result["input_format"] == "csv"
    assert result["output_format"] == "docx"
    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0

def test_json_to_pdf_conversion(engine, temp_dir):
    """Test conversion from JSON to PDF."""
    # Create test files
    input_path = create_test_file(temp_dir / "test.json", SAMPLE_JSON_CONTENT)
    output_path = temp_dir / "test.pdf"
    
    # Perform conversion
    result = engine.convert_file(input_path, output_path)
    
    # Check results
    assert result["input_format"] == "json"
    assert result["output_format"] == "pdf"
    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0

def test_xml_to_xlsx_conversion(engine, temp_dir):
    """Test conversion from XML to XLSX."""
    # Create test files
    input_path = create_test_file(temp_dir / "test.xml", SAMPLE_XML_CONTENT)
    output_path = temp_dir / "test.xlsx"
    
    # Perform conversion
    result = engine.convert_file(input_path, output_path)
    
    # Check results
    assert result["input_format"] == "xml"
    assert result["output_format"] == "xlsx"
    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0

def test_supported_conversions(engine):
    """Test that all supported conversion paths are available."""
    # Get all supported conversions
    conversion_map = engine.get_supported_conversions()
    
    # Check that specific format conversions are supported
    assert "xlsx" in conversion_map
    assert "docx" in conversion_map
    assert "json" in conversion_map
    
    # Check cross-domain conversions
    assert "pdf" in conversion_map["xlsx"]  # Spreadsheet to Document
    assert "json" in conversion_map["docx"]  # Document to Data Exchange
    assert "docx" in conversion_map["json"]  # Data Exchange to Document