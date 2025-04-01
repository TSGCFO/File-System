# Adding New Converters to FileConverter

This guide explains how to extend FileConverter with support for new file formats by implementing custom converter plugins.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Step-by-Step Guide](#step-by-step-guide)
  - [1. Create a New Converter Module](#1-create-a-new-converter-module)
  - [2. Implement the BaseConverter Interface](#2-implement-the-baseconverter-interface)
  - [3. Define Supported Formats](#3-define-supported-formats)
  - [4. Implement the Conversion Logic](#4-implement-the-conversion-logic)
  - [5. Define Parameters](#5-define-parameters)
  - [6. Testing Your Converter](#6-testing-your-converter)
- [Example: PDF to Image Converter](#example-pdf-to-image-converter)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Advanced Topics](#advanced-topics)

## Overview

FileConverter's architecture is designed to be extensible through converter plugins. Each converter handles conversion between specific file formats. When you add a new converter, it is automatically discovered and registered by the system, making its functionality available through the command-line interface, GUI, and API.

The converter discovery process works as follows:

1. When FileConverter starts, the `ConverterRegistry` scans the `fileconverter.converters` package
2. It looks for classes that inherit from `BaseConverter`
3. These classes are registered for their supported input and output formats
4. When a conversion is requested, the appropriate converter is selected based on the input and output formats

## Prerequisites

Before adding a new converter, you should:

- Be familiar with the FileConverter architecture (see [Architecture Guide](./architecture.md))
- Understand the file formats you want to support
- Have the necessary libraries or tools for handling these formats
- Set up a development environment (see [Development Guide](./development.md))

## Step-by-Step Guide

### 1. Create a New Converter Module

Create a new Python module in the `fileconverter/converters` directory. You can either:

- Add your converter to an existing module if it's related to the same category (e.g., add a new document format to `document.py`)
- Create a new module for a new category of formats

For example, to create a new module for handling CAD file formats:

```python
# fileconverter/converters/cad.py

"""
CAD format converters for FileConverter.

This module provides converters for Computer-Aided Design (CAD) file formats,
including DWG, DXF, and STL formats.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from fileconverter.core.registry import BaseConverter
from fileconverter.utils.error_handling import ConversionError
from fileconverter.utils.logging_utils import get_logger

logger = get_logger(__name__)

# Define supported formats
SUPPORTED_FORMATS = ["dwg", "dxf", "stl"]
```

### 2. Implement the BaseConverter Interface

Create a converter class that inherits from `BaseConverter` and implements all required methods:

```python
class CADConverter(BaseConverter):
    """Converter for CAD file formats."""
    
    @classmethod
    def get_input_formats(cls) -> List[str]:
        """Get the list of input formats supported by this converter."""
        return ["dwg", "dxf", "stl"]
    
    @classmethod
    def get_output_formats(cls) -> List[str]:
        """Get the list of output formats supported by this converter."""
        return ["dxf", "stl", "obj"]
    
    @classmethod
    def get_format_extensions(cls, format_name: str) -> List[str]:
        """Get the list of file extensions for a specific format."""
        format_map = {
            "dwg": ["dwg"],
            "dxf": ["dxf"],
            "stl": ["stl"],
            "obj": ["obj"],
        }
        return format_map.get(format_name.lower(), [])
    
    def convert(
        self, 
        input_path: Union[str, Path], 
        output_path: Union[str, Path],
        temp_dir: Union[str, Path],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert a CAD file from one format to another."""
        # Implementation will be added in step 4
        pass
    
    def get_parameters(self) -> Dict[str, Dict[str, Any]]:
        """Get the parameters supported by this converter."""
        # Implementation will be added in step 5
        pass
```

### 3. Define Supported Formats

The first three methods define which formats your converter supports:

- `get_input_formats()`: Returns a list of format names that your converter can read
- `get_output_formats()`: Returns a list of format names that your converter can write
- `get_format_extensions()`: Maps format names to file extensions

Format names should be lowercase and consistent across the application. They typically match common file extensions (e.g., "docx", "pdf", "jpg").

When defining these methods, consider:

- Which formats can your converter handle as input?
- Which formats can it produce as output?
- Are there multiple extensions for the same format? (e.g., .html and .htm)

### 4. Implement the Conversion Logic

The `convert()` method is where the actual conversion happens. This method should:

1. Validate inputs
2. Perform the conversion
3. Return information about the conversion

Here's an example implementation:

```python
def convert(
    self, 
    input_path: Union[str, Path], 
    output_path: Union[str, Path],
    temp_dir: Union[str, Path],
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """Convert a CAD file from one format to another.
    
    Args:
        input_path: Path to the input file.
        output_path: Path where the output file will be saved.
        temp_dir: Directory for temporary files.
        parameters: Conversion parameters.
    
    Returns:
        Dictionary with information about the conversion.
    
    Raises:
        ConversionError: If the conversion fails.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    temp_dir = Path(temp_dir)
    
    # Get formats from file extensions
    input_ext = input_path.suffix.lstrip('.').lower()
    output_ext = output_path.suffix.lstrip('.').lower()
    
    # Validate formats
    if input_ext not in self.get_input_formats():
        raise ConversionError(f"Unsupported input format: {input_ext}")
    
    if output_ext not in self.get_output_formats():
        raise ConversionError(f"Unsupported output format: {output_ext}")
    
    try:
        # Example: Converting DXF to STL
        if input_ext == "dxf" and output_ext == "stl":
            result = self._convert_dxf_to_stl(input_path, output_path, parameters)
        # Example: Converting DWG to DXF
        elif input_ext == "dwg" and output_ext == "dxf":
            result = self._convert_dwg_to_dxf(input_path, output_path, parameters)
        # Example: Multi-step conversion (DWG → DXF → STL)
        elif input_ext == "dwg" and output_ext == "stl":
            # Use temp file for intermediate step
            dxf_path = temp_dir / (input_path.stem + ".dxf")
            self._convert_dwg_to_dxf(input_path, dxf_path, parameters)
            result = self._convert_dxf_to_stl(dxf_path, output_path, parameters)
        else:
            raise ConversionError(
                f"Conversion from {input_ext} to {output_ext} is not supported"
            )
        
        return {
            "input_format": input_ext,
            "output_format": output_ext,
            "input_path": str(input_path),
            "output_path": str(output_path),
        }
    
    except Exception as e:
        logger.exception(f"Error during conversion: {str(e)}")
        raise ConversionError(f"Failed to convert {input_ext} to {output_ext}: {str(e)}")
```

You'll typically implement private helper methods for specific conversion paths:

```python
def _convert_dxf_to_stl(
    self, 
    input_path: Path, 
    output_path: Path,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """Convert a DXF file to STL format."""
    try:
        # Import required libraries
        import ezdxf
        from stl import mesh
        import numpy as np
        
        # Read DXF file
        doc = ezdxf.readfile(str(input_path))
        
        # Extract 3D data
        # ... (implementation details)
        
        # Create STL mesh
        # ... (implementation details)
        
        # Write STL file
        mesh_data.save(str(output_path))
        
        return {
            "input_format": "dxf",
            "output_format": "stl",
            "input_path": str(input_path),
            "output_path": str(output_path),
            "vertices": len(vertices),
            "faces": len(faces),
        }
    
    except ImportError:
        raise ConversionError(
            "Failed to convert DXF to STL: required libraries not available. "
            "Please install ezdxf and numpy-stl."
        )
    except Exception as e:
        raise ConversionError(f"Failed to convert DXF to STL: {str(e)}")
```

### 5. Define Parameters

The `get_parameters()` method defines the parameters that your converter accepts. This information is used by the CLI and GUI to validate and display parameter options.

```python
def get_parameters(self) -> Dict[str, Dict[str, Any]]:
    """Get the parameters supported by this converter."""
    return {
        "stl": {
            "binary": {
                "type": "boolean",
                "description": "Whether to create a binary STL file",
                "default": True,
                "help": "Binary STL files are more compact but less compatible"
            },
            "precision": {
                "type": "number",
                "description": "Precision for vertex coordinates",
                "default": 0.001,
                "min": 0.0001,
                "max": 1.0,
                "help": "Higher precision results in larger files"
            },
        },
        "dxf": {
            "version": {
                "type": "string",
                "description": "DXF version",
                "default": "R2010",
                "options": ["R12", "R2000", "R2004", "R2007", "R2010", "R2013", "R2018"],
                "help": "Older versions may have better compatibility but fewer features"
            },
        },
        "obj": {
            "include_materials": {
                "type": "boolean",
                "description": "Include material definitions",
                "default": True,
                "help": "Creates an MTL file alongside the OBJ file"
            },
        },
    }
```

Parameter definitions should include:
- `type`: The parameter data type ("string", "number", "boolean", etc.)
- `description`: A brief description of the parameter
- `default`: The default value if not specified
- Additional type-specific metadata:
  - For numbers: `min` and `max` values
  - For strings with fixed options: `options` list
- `help`: A more detailed explanation of the parameter

### 6. Testing Your Converter

Before your converter can be used, it needs to be tested thoroughly:

1. Create unit tests in the `tests/test_converters` directory:

```python
# tests/test_converters/test_cad.py

import pytest
from pathlib import Path

from fileconverter.converters.cad import CADConverter
from fileconverter.core.engine import ConversionEngine

class TestCADConverter:
    def test_get_input_formats(self):
        converter = CADConverter()
        formats = converter.get_input_formats()
        assert "dxf" in formats
        assert "dwg" in formats
        assert "stl" in formats
    
    def test_get_output_formats(self):
        converter = CADConverter()
        formats = converter.get_output_formats()
        assert "dxf" in formats
        assert "stl" in formats
        assert "obj" in formats
    
    def test_convert_dxf_to_stl(self, tmp_path):
        # Skip if required libraries are not available
        pytest.importorskip("ezdxf")
        pytest.importorskip("stl")
        
        converter = CADConverter()
        input_path = Path("tests/fixtures/sample.dxf")
        output_path = tmp_path / "output.stl"
        temp_dir = tmp_path / "temp"
        temp_dir.mkdir()
        
        result = converter.convert(
            input_path=input_path,
            output_path=output_path,
            temp_dir=temp_dir,
            parameters={"binary": True}
        )
        
        assert output_path.exists()
        assert result["input_format"] == "dxf"
        assert result["output_format"] == "stl"
```

2. Test through the main API:

```python
engine = ConversionEngine()
result = engine.convert_file("sample.dxf", "output.stl")
```

3. Test through the command-line interface:

```bash
fileconverter convert sample.dxf output.stl
```

## Example: PDF to Image Converter

Here's a complete example of a converter that extracts images from PDF files:

```python
# fileconverter/converters/pdf_image.py

"""
PDF to image converter for FileConverter.

This module provides a converter for extracting images from PDF files
and converting PDFs to various image formats.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from fileconverter.core.registry import BaseConverter
from fileconverter.utils.error_handling import ConversionError
from fileconverter.utils.logging_utils import get_logger

logger = get_logger(__name__)

# Define supported formats
SUPPORTED_FORMATS = ["pdf", "png", "jpg", "tiff"]


class PDFImageConverter(BaseConverter):
    """Converter for extracting images from PDFs and converting PDFs to images."""
    
    @classmethod
    def get_input_formats(cls) -> List[str]:
        """Get the list of input formats supported by this converter."""
        return ["pdf"]
    
    @classmethod
    def get_output_formats(cls) -> List[str]:
        """Get the list of output formats supported by this converter."""
        return ["png", "jpg", "tiff"]
    
    @classmethod
    def get_format_extensions(cls, format_name: str) -> List[str]:
        """Get the list of file extensions for a specific format."""
        format_map = {
            "pdf": ["pdf"],
            "png": ["png"],
            "jpg": ["jpg", "jpeg"],
            "tiff": ["tiff", "tif"],
        }
        return format_map.get(format_name.lower(), [])
    
    def convert(
        self, 
        input_path: Union[str, Path], 
        output_path: Union[str, Path],
        temp_dir: Union[str, Path],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert a PDF to an image format or extract images from a PDF.
        
        Args:
            input_path: Path to the input PDF file.
            output_path: Path where the output image will be saved.
            temp_dir: Directory for temporary files.
            parameters: Conversion parameters:
                - dpi: Resolution in dots per inch (default: 300)
                - page: Page number to convert (default: 1)
                - quality: Image quality for lossy formats (default: 90)
        
        Returns:
            Dictionary with information about the conversion.
        
        Raises:
            ConversionError: If the conversion fails.
        """
        input_path = Path(input_path)
        output_path = Path(output_path)
        temp_dir = Path(temp_dir)
        
        # Get formats from file extensions
        input_ext = input_path.suffix.lstrip('.').lower()
        output_ext = output_path.suffix.lstrip('.').lower()
        
        # Normalize extensions
        if input_ext == "jpeg":
            input_ext = "jpg"
        if output_ext == "jpeg":
            output_ext = "jpg"
        if input_ext == "tif":
            input_ext = "tiff"
        if output_ext == "tif":
            output_ext = "tiff"
        
        # Validate formats
        if input_ext != "pdf":
            raise ConversionError(f"Unsupported input format: {input_ext}")
        
        if output_ext not in ["png", "jpg", "tiff"]:
            raise ConversionError(f"Unsupported output format: {output_ext}")
        
        # Get parameters
        dpi = parameters.get("dpi", 300)
        page = parameters.get("page", 1)
        quality = parameters.get("quality", 90)
        
        try:
            # Try to use PyMuPDF if available
            import fitz  # PyMuPDF
            
            doc = fitz.open(str(input_path))
            if page < 1 or page > len(doc):
                raise ConversionError(f"Invalid page number: {page}. PDF has {len(doc)} pages.")
            
            # Convert 1-based page number to 0-based index
            pix = doc[page - 1].get_pixmap(dpi=dpi)
            
            if output_ext == "png":
                pix.save(str(output_path))
            elif output_ext == "jpg":
                pix.save(str(output_path), quality=quality)
            elif output_ext == "tiff":
                pix.save(str(output_path))
            
            return {
                "input_format": "pdf",
                "output_format": output_ext,
                "input_path": str(input_path),
                "output_path": str(output_path),
                "page_count": len(doc),
                "converted_page": page,
                "width": pix.width,
                "height": pix.height,
            }
        
        except ImportError:
            # Fall back to using Wand (ImageMagick)
            try:
                from wand.image import Image
                
                with Image(filename=str(input_path), resolution=dpi) as pdf:
                    # Check page number
                    if page < 1 or page > len(pdf.sequence):
                        raise ConversionError(f"Invalid page number: {page}. PDF has {len(pdf.sequence)} pages.")
                    
                    # Extract the specified page
                    with Image(pdf.sequence[page - 1]) as img:
                        if output_ext == "jpg":
                            img.format = "JPEG"
                            img.compression_quality = quality
                        elif output_ext == "png":
                            img.format = "PNG"
                        elif output_ext == "tiff":
                            img.format = "TIFF"
                        
                        img.save(filename=str(output_path))
                
                return {
                    "input_format": "pdf",
                    "output_format": output_ext,
                    "input_path": str(input_path),
                    "output_path": str(output_path),
                    "page_count": len(pdf.sequence),
                    "converted_page": page,
                }
            
            except ImportError:
                raise ConversionError(
                    "Failed to convert PDF to image: required libraries not available. "
                    "Please install PyMuPDF or Wand: `pip install pymupdf` or `pip install wand`."
                )
            except Exception as e:
                raise ConversionError(f"Failed to convert PDF to image: {str(e)}")
    
    def get_parameters(self) -> Dict[str, Dict[str, Any]]:
        """Get the parameters supported by this converter."""
        return {
            "png": {
                "dpi": {
                    "type": "number",
                    "description": "Resolution in dots per inch",
                    "default": 300,
                    "min": 72,
                    "max": 1200,
                    "help": "Higher DPI results in larger images with more detail"
                },
                "page": {
                    "type": "number",
                    "description": "Page number to convert",
                    "default": 1,
                    "min": 1,
                    "help": "1-based page number (first page is 1)"
                },
            },
            "jpg": {
                "dpi": {
                    "type": "number",
                    "description": "Resolution in dots per inch",
                    "default": 300,
                    "min": 72,
                    "max": 1200,
                    "help": "Higher DPI results in larger images with more detail"
                },
                "page": {
                    "type": "number",
                    "description": "Page number to convert",
                    "default": 1,
                    "min": 1,
                    "help": "1-based page number (first page is 1)"
                },
                "quality": {
                    "type": "number",
                    "description": "JPEG quality",
                    "default": 90,
                    "min": 1,
                    "max": 100,
                    "help": "Higher quality results in larger files"
                },
            },
            "tiff": {
                "dpi": {
                    "type": "number",
                    "description": "Resolution in dots per inch",
                    "default": 300,
                    "min": 72,
                    "max": 1200,
                    "help": "Higher DPI results in larger images with more detail"
                },
                "page": {
                    "type": "number",
                    "description": "Page number to convert",
                    "default": 1,
                    "min": 1,
                    "help": "1-based page number (first page is 1)"
                },
            },
        }
```

## Best Practices

When implementing new converters, follow these best practices:

1. **Handle Dependencies Gracefully**:
   - Try to import optional dependencies inside methods rather than at the module level
   - Provide helpful error messages when dependencies are missing
   - Support alternative implementations when possible

2. **Error Handling**:
   - Use specific error messages that help users understand what went wrong
   - Catch and wrap exceptions from third-party libraries
   - Log detailed information for debugging

3. **Performance Considerations**:
   - For large files, process data in chunks when possible
   - Use temporary files for intermediate steps
   - Release resources (file handles, memory) promptly

4. **Documentation**:
   - Document each method thoroughly
   - Include examples in docstrings
   - Describe parameters in detail
   - Document any external dependencies

5. **Testing**:
   - Write unit tests for all conversion paths
   - Test with various inputs, including edge cases
   - Include tests that verify parameter behavior

## Troubleshooting

Common issues when developing new converters:

1. **Converter Not Found**:
   - Ensure your converter class inherits from `BaseConverter`
   - Make sure the module is in the `fileconverter/converters` directory
   - Check that your converter declares the formats correctly

2. **Import Errors**:
   - Handle optional dependencies properly
   - Use conditional imports inside methods
   - Provide clear error messages for missing dependencies

3. **Conversion Errors**:
   - Debug with preserved temporary files (`--preserve-temp`)
   - Enable debug logging (`-vv`)
   - Check file permissions and paths

## Advanced Topics

### Cross-Domain Conversions

FileConverter supports conversions not only within a single domain (like document-to-document or image-to-image) but also across different domains (like document-to-data or spreadsheet-to-document). Understanding how to implement these cross-domain conversions is important for creating powerful converters.

#### Implementing Cross-Domain Conversions

To implement a cross-domain converter:

1. **Declare supported cross-domain formats** in `get_input_formats()` and `get_output_formats()`:

```python
@classmethod
def get_input_formats(cls) -> List[str]:
    # Include formats from another domain
    return ["docx", "pdf", "txt", "html", "md"]

@classmethod
def get_output_formats(cls) -> List[str]:
    # Support conversion to data formats
    return ["json", "xml", "yaml", "csv", "xlsx"]
```

2. **Implement specific methods** for cross-domain conversions:

```python
def _convert_to_data_format(
    self,
    input_path: Path,
    output_path: Path,
    input_format: str,
    output_format: str,
    temp_dir: Path,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """Convert a document format to a data exchange format.
    
    This method handles the extraction and transformation of content
    from document formats to structured data formats.
    """
    # Implementation logic here
    # ...
```

3. **Include conditional checks** in your main `convert()` method:

```python
def convert(self, input_path, output_path, temp_dir, parameters):
    # ...
    
    # Handle cross-domain conversions
    if input_format in ["docx", "pdf", "html"] and output_format in ["json", "xml", "yaml"]:
        result = self._convert_to_data_format(
            input_path, output_path, input_format, output_format, temp_dir, parameters
        )
    # ...
```

#### Example: DocumentConverter to Data Exchange Formats

Here's a simplified example showing how document formats are converted to data exchange formats:

```python
def _convert_to_data_format(
    self,
    input_path: Path,
    output_path: Path,
    input_format: str,
    output_format: str,
    temp_dir: Path,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """Convert a document format to a data exchange format."""
    
    # Extract structured content from the document
    document_data = self._extract_document_structure(input_path, input_format)
    
    # Transform to the target data format
    if output_format == "json":
        self._save_as_json(document_data, output_path, parameters)
    elif output_format == "xml":
        self._save_as_xml(document_data, output_path, parameters)
    elif output_format == "yaml":
        self._save_as_yaml(document_data, output_path, parameters)
    # ... other format handlers
    
    return {
        "input_format": input_format,
        "output_format": output_format,
        "input_path": str(input_path),
        "output_path": str(output_path),
    }

def _extract_document_structure(self, input_path: Path, format: str) -> Dict[str, Any]:
    """Extract structured data from a document.
    
    This method analyzes a document and creates a structured representation
    that can be converted to various data formats.
    """
    structured_data = {
        "metadata": {},
        "content": [],
        "tables": []
    }
    
    # Logic to extract document structure varies by format
    if format == "docx":
        # Extract from DOCX using python-docx
        # ...
    elif format == "pdf":
        # Extract from PDF using PyPDF or related library
        # ...
    # ... other format handlers
    
    return structured_data
```

#### Coordinating Between Converter Classes

For more complex cross-domain conversions, you may need to coordinate between different converter classes:

1. **Import other converter classes** when needed:
```python
from fileconverter.converters.document import DocumentConverter
from fileconverter.converters.spreadsheet import SpreadsheetConverter
```

2. **Share common utility methods** in a separate module to avoid code duplication

3. **Use the registry to find other converters**:
```python
from fileconverter.core.registry import get_converter_registry

def convert(self, input_path, output_path, temp_dir, parameters):
    # ...
    
    # For complex conversions requiring another converter type
    if input_format == "pdf" and output_format == "xlsx":
        # First convert to an intermediate format both converters understand
        csv_path = temp_dir / f"{input_path.stem}.csv"
        
        # Use DocumentConverter to convert PDF to CSV
        registry = get_converter_registry()
        doc_converter = registry.get_converter("pdf", "csv")
        if doc_converter:
            doc_converter.convert(input_path, csv_path, temp_dir, parameters)
            
            # Then use SpreadsheetConverter to convert CSV to XLSX
            spreadsheet_converter = registry.get_converter("csv", "xlsx")
            if spreadsheet_converter:
                result = spreadsheet_converter.convert(
                    csv_path, output_path, temp_dir, parameters
                )
                return result
    # ...
```

#### Best Practices for Cross-Domain Conversions

1. **Structure Preservation**: Maintain as much structure and formatting as reasonably possible
2. **Semantic Mapping**: Map document elements to appropriate data structures (headings to keys, tables to arrays, etc.)
3. **Fallback Options**: Provide simpler conversions when complex structures can't be fully preserved
4. **Test Both Ways**: For bidirectional converters, ensure round-trip conversions produce reasonable results
5. **Document Limitations**: Clearly document what aspects of formatting or structure are preserved or lost

### Multi-Stage Conversions

For complex conversions requiring multiple steps:

```python
def convert(self, input_path, output_path, temp_dir, parameters):
    # Direct conversion not possible, use intermediate format
    intermediate_path = temp_dir / f"{input_path.stem}.intermediate"
    
    # Step 1: Convert to intermediate format
    step1_result = self._convert_to_intermediate(input_path, intermediate_path, parameters)
    
    # Step 2: Convert from intermediate to output format
    step2_result = self._convert_from_intermediate(intermediate_path, output_path, parameters)
    
    # Combine results
    return {
        "input_format": step1_result["input_format"],
        "output_format": step2_result["output_format"],
        "input_path": str(input_path),
        "output_path": str(output_path),
        "steps": [step1_result, step2_result],
    }
```

### Handling Large Files

For large file processing:

```python
def _convert_large_file(self, input_path, output_path, parameters):
    # Process in chunks to avoid memory issues
    chunk_size = parameters.get("chunk_size", 10000)
    
    with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
        # Process header
        header = self._process_header(infile, parameters)
        outfile.write(header)
        
        # Process data in chunks
        while True:
            chunk = infile.read(chunk_size)
            if not chunk:
                break
            
            processed_chunk = self._process_chunk(chunk, parameters)
            outfile.write(processed_chunk)
        
        # Process footer
        footer = self._process_footer(parameters)
        outfile.write(footer)
```

### Parameter Validation

Implement parameter validation in your conversion method:

```python
def convert(self, input_path, output_path, temp_dir, parameters):
    # Validate parameters
    quality = parameters.get("quality", 90)
    if not isinstance(quality, (int, float)) or quality < 1 or quality > 100:
        raise ConversionError(f"Invalid quality value: {quality}. Must be between 1 and 100.")
    
    # Continue with conversion
    # ...
```

### Progress Reporting

For long-running conversions, you can report progress:

```python
def _convert_with_progress(self, input_path, output_path, parameters):
    total_steps = 10
    
    for i in range(total_steps):
        # Do some work
        # ...
        
        # Report progress
        logger.info(f"Conversion progress: {(i+1)/total_steps:.0%}")
```

In the future, FileConverter may provide a more structured API for progress reporting.