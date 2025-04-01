"""
Document format converters for FileConverter.

This module provides converters for document formats, enabling transformation
between various document types used in office and publishing environments.

Supported formats include:
- Microsoft Word (.doc, .docx) - proprietary document formats by Microsoft
- Rich Text Format (.rtf) - cross-platform document format
- OpenDocument Text (.odt) - open standard document format
- PDF (.pdf) - Portable Document Format for fixed-layout documents
- Plain Text (.txt) - unformatted text files
- HTML (.html, .htm) - HyperText Markup Language for web pages
- Markdown (.md) - lightweight markup language

The module implements the DocumentConverter class which handles conversions
between these formats. Different conversion paths use different approaches:
- Direct conversion using specialized libraries (e.g., python-docx for DOCX)
- Multi-step conversion through intermediate formats when direct conversion
  is not possible or optimal (e.g., Markdown → HTML → PDF)
- External tools when appropriate (e.g., LibreOffice for DOC → DOCX)

Conversion capabilities may depend on installed external dependencies. When
primary conversion methods are unavailable, the converter will attempt fallback
methods with appropriate warnings.

Examples:
    # Convert a Word document to PDF
    from fileconverter.core.engine import ConversionEngine
    
    engine = ConversionEngine()
    result = engine.convert_file("document.docx", "document.pdf")
    
    # Convert Markdown to HTML with custom CSS
    engine.convert_file(
        "document.md",
        "document.html",
        parameters={"css": "path/to/style.css"}
    )

Dependencies:
    - python-docx: For DOCX processing
    - docx2pdf: For DOCX to PDF conversion (optional)
    - markdown: For Markdown to HTML conversion
    - weasyprint or wkhtmltopdf: For HTML to PDF conversion
    - LibreOffice: For DOC to DOCX conversion (optional external dependency)
    
TODO:
    - Add support for DOCX to ODT conversion
    - Implement DOC to PDF direct conversion
    - Add batch processing optimization for multiple files
    - Improve CSS handling for HTML output
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from fileconverter.core.registry import BaseConverter
from fileconverter.utils.error_handling import ConversionError
from fileconverter.utils.file_utils import copy_file, get_file_extension, guess_encoding
from fileconverter.utils.logging_utils import get_logger
from fileconverter.utils.validation import validate_file_path

logger = get_logger(__name__)

# Define supported formats
SUPPORTED_FORMATS = ["doc", "docx", "rtf", "odt", "pdf", "txt", "html", "htm", "md", "xlsx", "csv", "tsv", "json", "xml", "yaml", "ini", "toml"]

class DocumentConverter(BaseConverter):
    """Converter for document formats.
    
    This class implements the BaseConverter interface to provide document format
    conversion capabilities. It supports various document formats such as DOCX,
    PDF, RTF, ODT, TXT, HTML, and Markdown.
    
    The converter uses different approaches for different conversion paths:
    - Native Python libraries for format-specific conversions
    - External tools (e.g., LibreOffice) for certain conversions
    - Multi-step conversions through intermediate formats
    
    Attributes:
        None
        
    Notes:
        - Format detection is based on file extensions
        - Temporary files are used for multi-step conversions
        - External dependencies may be required for some conversions
    
    TODO:
        - Add progress reporting for long-running conversions
        - Implement error recovery for failed conversions
        - Add support for password-protected documents
    """
    """Converter for document formats."""
    
    @classmethod
    def get_input_formats(cls) -> List[str]:
        """Get the list of input formats supported by this converter.
        
        This method returns a list of document format names that this converter
        can accept as input. These formats can be converted to one or more of the
        formats returned by get_output_formats().
        
        Returns:
            List[str]: A list of format names (lowercase) supported as input:
                - "doc": Microsoft Word Document (binary format)
                - "docx": Microsoft Word Document (Open XML format)
                - "rtf": Rich Text Format
                - "odt": OpenDocument Text
                - "txt": Plain Text
                - "html"/"htm": HTML Document
                - "md": Markdown
        """
        return ["doc", "docx", "rtf", "odt", "txt", "html", "htm", "md"]
    
    @classmethod
    def get_output_formats(cls) -> List[str]:
        """Get the list of output formats supported by this converter.
        
        This method returns a list of document format names that this converter
        can produce as output. Input formats (returned by get_input_formats())
        can be converted to these formats.
        
        Not all input formats can be converted to all output formats. The
        convert() method checks if a specific conversion path is supported.
        
        Returns:
            List[str]: A list of format names (lowercase) supported as output:
                - "docx": Microsoft Word Document (Open XML format)
                - "pdf": Portable Document Format
                - "txt": Plain Text
                - "html": HTML Document
                - "md": Markdown
                - "xlsx": Microsoft Excel Spreadsheet
                - "csv": Comma-Separated Values
                - "tsv": Tab-Separated Values
                - "json": JavaScript Object Notation
                - "xml": eXtensible Markup Language
                - "yaml": YAML Ain't Markup Language
                - "ini": Configuration File
                - "toml": Tom's Obvious, Minimal Language
                
        Note:
            Output format support may depend on the availability of required
            libraries and external tools.
        """
        return ["docx", "pdf", "txt", "html", "md", "xlsx", "csv", "tsv", "json", "xml", "yaml", "ini", "toml"]
    
    @classmethod
    def get_format_extensions(cls, format_name: str) -> List[str]:
        """Get the list of file extensions for a specific document format.
        
        This method returns a list of file extensions that correspond to the
        specified document format. These extensions are used by the system to
        determine the format of files based on their extension.
        
        Args:
            format_name (str): Name of the document format (e.g., "docx", "pdf").
                Format names are case-insensitive.
        
        Returns:
            List[str]: A list of file extensions (without the dot) for the
                specified format. For example, for "html" this returns
                ["html", "htm"]. If the format is not recognized, an empty
                list is returned.
                
        Example:
            extensions = DocumentConverter.get_format_extensions("html")
            # Returns ["html", "htm"]
        """
        format_map = {
            "doc": ["doc"],
            "docx": ["docx"],
            "rtf": ["rtf"],
            "odt": ["odt"],
            "pdf": ["pdf"],
            "txt": ["txt"],
            "html": ["html", "htm"],
            "md": ["md", "markdown"],
            "xlsx": ["xlsx"],
            "xls": ["xls"],
            "csv": ["csv"],
            "tsv": ["tsv"],
            "json": ["json"],
            "xml": ["xml"],
            "yaml": ["yaml", "yml"],
            "ini": ["ini", "conf", "cfg"],
            "toml": ["toml"],
        }
        return format_map.get(format_name.lower(), [])
    
    def convert(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        temp_dir: Union[str, Path],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert a document from one format to another.
        
        This method handles the conversion of a document file from one format
        to another. It determines the input and output formats based on file
        extensions, validates the input file, and selects an appropriate
        conversion method based on the format pair.
        
        The method supports various conversion paths, including direct conversions
        and multi-step conversions through intermediate formats when necessary.
        
        Args:
            input_path (Union[str, Path]): Path to the input document file.
                Must be a valid file that exists and is readable.
            
            output_path (Union[str, Path]): Path where the converted document
                will be saved. The directory must exist and be writable.
            
            temp_dir (Union[str, Path]): Directory for temporary files used
                during the conversion process. This directory must exist and
                be writable. It's used primarily for multi-step conversions.
            
            parameters (Dict[str, Any]): Conversion parameters that control
                the conversion behavior. Supported parameters depend on the
                output format and include:
                
                For PDF output:
                - page_size (str): Page size, e.g., "A4", "Letter" (default: "A4")
                - orientation (str): "portrait" or "landscape" (default: "portrait")
                - margin (float): Page margin in inches (default: 1.0)
                
                For HTML output:
                - css (str): CSS file path or CSS content (default: None)
                - template (str): HTML template file path (default: None)
                
                For DOCX output:
                - template (str): Template file path (default: None)
        
        Returns:
            Dict[str, Any]: Dictionary with information about the conversion:
            - input_format (str): The detected input format (e.g., "docx")
            - output_format (str): The output format (e.g., "pdf")
            - input_path (str): The absolute path to the input file
            - output_path (str): The absolute path to the output file
        
        Raises:
            ConversionError: If the conversion fails for any reason, such as:
                - Unsupported input or output format
                - Unsupported conversion path
                - Missing dependencies for a specific conversion
                - Error during the conversion process
                
        Example:
            converter = DocumentConverter()
            
            # Convert DOCX to PDF
            result = converter.convert(
                input_path="document.docx",
                output_path="document.pdf",
                temp_dir="/tmp",
                parameters={"orientation": "landscape", "margin": 0.5}
            )
            
            # Convert Markdown to HTML with custom CSS
            result = converter.convert(
                input_path="document.md",
                output_path="document.html",
                temp_dir="/tmp",
                parameters={"css": "style.css"}
            )
        """
        input_path = Path(input_path)
        output_path = Path(output_path)
        temp_dir = Path(temp_dir)
        
        # Validate paths
        validate_file_path(input_path, must_exist=True)
        
        # Get formats from file extensions
        input_ext = get_file_extension(input_path).lower()
        output_ext = get_file_extension(output_path).lower()
        
        # Map extensions to formats
        input_format = self._get_format_from_extension(input_ext)
        output_format = self._get_format_from_extension(output_ext)
        
        if not input_format:
            raise ConversionError(f"Unsupported input format: {input_ext}")
        
        if not output_format:
            raise ConversionError(f"Unsupported output format: {output_ext}")
        
        # Determine conversion method
        if input_format == "docx" and output_format == "pdf":
            result = self._convert_docx_to_pdf(input_path, output_path, parameters)
        elif input_format == "doc" and output_format == "docx":
            result = self._convert_doc_to_docx(input_path, output_path, parameters)
        elif input_format in ["html", "htm"] and output_format == "pdf":
            result = self._convert_html_to_pdf(input_path, output_path, parameters)
        elif input_format == "md" and output_format == "html":
            result = self._convert_markdown_to_html(input_path, output_path, parameters)
        elif input_format == "md" and output_format == "pdf":
            # Convert markdown to HTML first, then HTML to PDF
            html_path = temp_dir / "temp.html"
            self._convert_markdown_to_html(input_path, html_path, parameters)
            result = self._convert_html_to_pdf(html_path, output_path, parameters)
        elif input_format == "txt" and output_format == "html":
            result = self._convert_text_to_html(input_path, output_path, parameters)
        elif input_format == "txt" and output_format == "pdf":
            # Convert text to HTML first, then HTML to PDF
            html_path = temp_dir / "temp.html"
            self._convert_text_to_html(input_path, html_path, parameters)
            result = self._convert_html_to_pdf(html_path, output_path, parameters)
        # Handle conversions to spreadsheet and data exchange formats
        elif output_format in ["xlsx", "csv", "tsv", "json", "xml", "yaml", "ini", "toml"]:
            result = self._convert_to_data_format(input_path, output_path, input_format, output_format, temp_dir, parameters)
        else:
            raise ConversionError(
                f"Conversion from {input_format} to {output_format} is not supported"
            )
        
        return result
    def get_parameters(self) -> Dict[str, Dict[str, Any]]:
        """Get the parameters supported by this document converter.
        
        This method returns a dictionary describing the parameters that can be
        used to customize document conversions. The parameters are organized by
        output format, allowing different parameters for different output formats.
        
        The returned dictionary structure:
        - Top level keys are output format names (e.g., "pdf", "html")
        - For each format, the value is a dictionary of parameter definitions
        - Each parameter definition includes type, description, default value,
          and any additional format-specific metadata (like min/max values or options)
        
        Returns:
            Dict[str, Dict[str, Any]]: A dictionary mapping output formats to
                parameter definitions. Each parameter definition includes:
                - type: The parameter data type
                - description: User-friendly description of the parameter
                - default: Default value if not specified
                - Additional type-specific metadata
                
        Example:
            params = converter.get_parameters()
            pdf_params = params.get("pdf", {})
            
            # Check if a specific parameter is supported
            if "orientation" in pdf_params:
                print(f"Orientation options: {pdf_params['orientation']['options']}")
                print(f"Default orientation: {pdf_params['orientation']['default']}")
        """
        return {
            "pdf": {
                "page_size": {
                    "type": "string",
                    "description": "Page size (e.g., A4, Letter)",
                    "default": "A4",
                    "options": ["A4", "Letter", "Legal"],
                    "help": "Specifies the page size for the PDF document"
                },
                "orientation": {
                    "type": "string",
                    "description": "Page orientation",
                    "default": "portrait",
                    "options": ["portrait", "landscape"],
                    "help": "Sets the orientation of pages in the PDF document"
                },
                "margin": {
                    "type": "number",
                    "description": "Page margin in inches",
                    "default": 1.0,
                    "min": 0.0,
                    "max": 3.0,
                    "help": "Sets the margin size around all sides of the page"
                },
                "compression": {
                    "type": "string",
                    "description": "PDF compression level",
                    "default": "normal",
                    "options": ["none", "low", "normal", "high"],
                    "help": "Controls the compression level of the PDF file"
                },
            },
            "html": {
                "css": {
                    "type": "string",
                    "description": "CSS file path or CSS content",
                    "default": None,
                    "help": "Custom CSS to style the HTML output. Can be a file path or direct CSS content"
                },
                "template": {
                    "type": "string",
                    "description": "HTML template file path",
                    "default": None,
                    "help": "Path to an HTML template file. The template should include a {{content}} placeholder"
                },
                "title": {
                    "type": "string",
                    "description": "Document title",
                    "default": None,
                    "help": "Title to use in the HTML head section"
                },
            },
            "docx": {
                "template": {
                    "type": "string",
                    "description": "Template file path",
                    "default": None,
                    "help": "Path to a DOCX template file to use as the base for the output document"
                },
                "style": {
                    "type": "string",
                    "description": "Style to apply",
                    "default": "Normal",
                    "help": "Name of the style to apply to the document content"
                },
            },
            "txt": {
                "encoding": {
                    "type": "string",
                    "description": "Text encoding",
                    "default": "utf-8",
                    "options": ["utf-8", "ascii", "latin-1", "utf-16"],
                    "help": "Character encoding for the output text file"
                },
                "line_ending": {
                    "type": "string",
                    "description": "Line ending style",
                    "default": "auto",
                    "options": ["auto", "windows", "unix", "mac"],
                    "help": "Line ending style (auto selects based on the operating system)"
                }
            }
        }
    
    def _get_format_from_extension(self, extension: str) -> Optional[str]:
        """Get the format name from a file extension.
        
        This helper method determines the document format based on a file extension.
        It maps extensions to their corresponding format names, handling special
        cases where multiple extensions map to the same format (e.g., "html" and "htm").
        
        Args:
            extension (str): File extension (without the dot). For example, "docx",
                "html", or "md". Case is ignored.
        
        Returns:
            Optional[str]: The format name corresponding to the extension, or None
                if the extension is not recognized as a supported document format.
                
        Example:
            format_name = converter._get_format_from_extension("docx")  # Returns "docx"
            format_name = converter._get_format_from_extension("htm")   # Returns "html"
            format_name = converter._get_format_from_extension("xyz")   # Returns None
        
        Note:
            This is an internal helper method used by the convert() method to
            determine the input and output formats based on file extensions.
            
        TODO:
            - Consider implementing more sophisticated format detection based
              on file content analysis for ambiguous extensions
            - Add support for additional document format extensions
        """
        ext_lower = extension.lower()
        
        # Handle special cases with multiple extensions mapping to the same format
        if ext_lower in ["html", "htm"]:
            return "html"
        elif ext_lower in ["md", "markdown"]:
            return "md"
        # Check if it's a standard format with matching extension name
        elif ext_lower in SUPPORTED_FORMATS:
            return ext_lower
        
        # Extension not recognized as a supported document format
        return None
    
    def _convert_docx_to_pdf(
        self, 
        input_path: Path, 
        output_path: Path,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert a DOCX file to PDF.
        
        Args:
            input_path: Path to the input DOCX file.
            output_path: Path where the output PDF will be saved.
            parameters: Conversion parameters.
        
        Returns:
            Dictionary with information about the conversion.
        
        Raises:
            ConversionError: If the conversion fails.
        """
        try:
            # Try to use python-docx-pdf if available
            from docx2pdf import convert
            convert(str(input_path), str(output_path))
        except ImportError:
            # Fall back to using LibreOffice if available
            try:
                result = subprocess.run(
                    [
                        "libreoffice", "--headless", "--convert-to", "pdf",
                        "--outdir", str(output_path.parent),
                        str(input_path)
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                
                # LibreOffice outputs to a file with the same name but .pdf extension
                # If the output path has a different name, we need to rename the file
                libreoffice_output = input_path.with_suffix(".pdf")
                if libreoffice_output.name != output_path.name:
                    os.rename(libreoffice_output, output_path)
            
            except (subprocess.SubprocessError, FileNotFoundError) as e:
                raise ConversionError(
                    f"Failed to convert DOCX to PDF: {str(e)}. "
                    "Please install python-docx-pdf or LibreOffice."
                )
        
        return {
            "input_format": "docx",
            "output_format": "pdf",
            "input_path": str(input_path),
            "output_path": str(output_path),
        }
    
    def _convert_doc_to_docx(
        self, 
        input_path: Path, 
        output_path: Path,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert a DOC file to DOCX.
        
        Args:
            input_path: Path to the input DOC file.
            output_path: Path where the output DOCX will be saved.
            parameters: Conversion parameters.
        
        Returns:
            Dictionary with information about the conversion.
        
        Raises:
            ConversionError: If the conversion fails.
        """
        try:
            # Try to use LibreOffice if available
            result = subprocess.run(
                [
                    "libreoffice", "--headless", "--convert-to", "docx",
                    "--outdir", str(output_path.parent),
                    str(input_path)
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            
            # LibreOffice outputs to a file with the same name but .docx extension
            # If the output path has a different name, we need to rename the file
            libreoffice_output = input_path.parent / f"{input_path.stem}.docx"
            if libreoffice_output != output_path:
                os.rename(libreoffice_output, output_path)
        
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            raise ConversionError(
                f"Failed to convert DOC to DOCX: {str(e)}. "
                "Please install LibreOffice."
            )
        
        return {
            "input_format": "doc",
            "output_format": "docx",
            "input_path": str(input_path),
            "output_path": str(output_path),
        }
    
    def _convert_html_to_pdf(
        self, 
        input_path: Path, 
        output_path: Path,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert an HTML file to PDF.
        
        Args:
            input_path: Path to the input HTML file.
            output_path: Path where the output PDF will be saved.
            parameters: Conversion parameters.
        
        Returns:
            Dictionary with information about the conversion.
        
        Raises:
            ConversionError: If the conversion fails.
        """
        try:
            # Try to use weasyprint if available
            from weasyprint import HTML
            HTML(str(input_path)).write_pdf(str(output_path))
        
        except ImportError:
            # Try to use wkhtmltopdf if available
            try:
                page_size = parameters.get("page_size", "A4")
                orientation = parameters.get("orientation", "portrait")
                margin = parameters.get("margin", 1.0)
                
                result = subprocess.run(
                    [
                        "wkhtmltopdf",
                        f"--page-size={page_size}",
                        f"--orientation={orientation}",
                        f"--margin-top={margin}in",
                        f"--margin-right={margin}in",
                        f"--margin-bottom={margin}in",
                        f"--margin-left={margin}in",
                        str(input_path),
                        str(output_path)
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )
            
            except (subprocess.SubprocessError, FileNotFoundError) as e:
                raise ConversionError(
                    f"Failed to convert HTML to PDF: {str(e)}. "
                    "Please install weasyprint or wkhtmltopdf."
                )
        
        return {
            "input_format": "html",
            "output_format": "pdf",
            "input_path": str(input_path),
            "output_path": str(output_path),
        }
    
    def _convert_markdown_to_html(
        self, 
        input_path: Path, 
        output_path: Path,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert a Markdown file to HTML.
        
        Args:
            input_path: Path to the input Markdown file.
            output_path: Path where the output HTML will be saved.
            parameters: Conversion parameters.
        
        Returns:
            Dictionary with information about the conversion.
        
        Raises:
            ConversionError: If the conversion fails.
        """
        try:
            import markdown
            
            # Read the markdown file
            with open(input_path, "r", encoding="utf-8") as f:
                md_content = f.read()
            
            # Convert to HTML
            html_content = markdown.markdown(
                md_content,
                extensions=["tables", "fenced_code", "nl2br", "toc"]
            )
            
            # Apply template if provided
            template_path = parameters.get("template")
            if template_path:
                try:
                    with open(template_path, "r", encoding="utf-8") as f:
                        template = f.read()
                    html_content = template.replace("{{content}}", html_content)
                except Exception as e:
                    logger.warning(f"Failed to apply template: {str(e)}")
            else:
                # Use a simple default template
                css = parameters.get("css", "")
                if css and Path(css).exists():
                    with open(css, "r", encoding="utf-8") as f:
                        css_content = f.read()
                    css_tag = f"<style>{css_content}</style>"
                elif css:
                    css_tag = f"<style>{css}</style>"
                else:
                    css_tag = """
                    <style>
                        body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 1em; }
                        pre { background-color: #f8f8f8; padding: 1em; overflow: auto; }
                        code { background-color: #f8f8f8; padding: 0.2em 0.4em; }
                        table { border-collapse: collapse; width: 100%; }
                        th, td { border: 1px solid #ddd; padding: 8px; }
                        th { background-color: #f2f2f2; }
                        tr:nth-child(even) { background-color: #f9f9f9; }
                    </style>
                    """
                
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <title>{input_path.stem}</title>
                    {css_tag}
                </head>
                <body>
                    {html_content}
                </body>
                </html>
                """
            
            # Write the HTML file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)
        
        except ImportError:
            raise ConversionError(
                "Failed to convert Markdown to HTML: markdown package not available. "
                "Please install it with 'pip install markdown'."
            )
        except Exception as e:
            raise ConversionError(f"Failed to convert Markdown to HTML: {str(e)}")
        
        return {
            "input_format": "md",
            "output_format": "html",
            "input_path": str(input_path),
            "output_path": str(output_path),
        }
    
    def _convert_text_to_html(
        self, 
        input_path: Path, 
        output_path: Path,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert a plain text file to HTML.
        
        Args:
            input_path: Path to the input text file.
            output_path: Path where the output HTML will be saved.
            parameters: Conversion parameters.
        
        Returns:
            Dictionary with information about the conversion.
        
        Raises:
            ConversionError: If the conversion fails.
        """
        try:
            # Detect encoding
            encoding = guess_encoding(input_path)
            
            # Read the text file
            with open(input_path, "r", encoding=encoding) as f:
                text_content = f.read()
            
            # Escape HTML special characters
            import html
            html_escaped = html.escape(text_content)
            
            # Replace newlines with <br> tags
            html_content = html_escaped.replace("\n", "<br>\n")
            
            # Apply template if provided
            template_path = parameters.get("template")
            if template_path:
                try:
                    with open(template_path, "r", encoding="utf-8") as f:
                        template = f.read()
                    html_content = template.replace("{{content}}", html_content)
                except Exception as e:
                    logger.warning(f"Failed to apply template: {str(e)}")
            else:
                # Use a simple default template
                css = parameters.get("css", "")
                if css and Path(css).exists():
                    with open(css, "r", encoding="utf-8") as f:
                        css_content = f.read()
                    css_tag = f"<style>{css_content}</style>"
                elif css:
                    css_tag = f"<style>{css}</style>"
                else:
                    css_tag = """
                    <style>
                        body { font-family: monospace; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 1em; }
                        pre { white-space: pre-wrap; }
                    </style>
                    """
                
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="{encoding}">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <title>{input_path.stem}</title>
                    {css_tag}
                </head>
                <body>
                    <pre>{html_content}</pre>
                </body>
                </html>
                """
            
            # Write the HTML file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)
        
        except Exception as e:
            raise ConversionError(f"Failed to convert text to HTML: {str(e)}")
        
        return {
            "input_format": "txt",
            "output_format": "html",
            "input_path": str(input_path),
            "output_path": str(output_path),
        }
        
    def _convert_to_data_format(
        self,
        input_path: Path,
        output_path: Path,
        input_format: str,
        output_format: str,
        temp_dir: Path,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert a document to a data format (spreadsheet, CSV, JSON, etc.).
        
        This method handles conversions from document formats to data formats by:
        1. First converting the document to HTML (as an intermediary format)
        2. Parsing the HTML to extract structured data
        3. Outputting the data in the requested format
        
        Args:
            input_path: Path to the input document.
            output_path: Path where the output file will be saved.
            input_format: Format of the input file.
            output_format: Format of the output file.
            temp_dir: Directory for temporary files.
            parameters: Conversion parameters.
            
        Returns:
            Dictionary with information about the conversion.
            
        Raises:
            ConversionError: If the conversion fails.
        """
        try:
            # First convert to HTML as intermediate format
            html_path = temp_dir / "temp.html"
            
            if input_format == "docx":
                import docx
                from docx import Document
                
                # Extract text and structure from DOCX
                doc = Document(input_path)
                
                # Create simple HTML
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write("<html><body>\n")
                    
                    # Process paragraphs and tables
                    for item in doc.element.body:
                        if item.tag.endswith('p'):
                            # Process paragraph
                            p = docx.text.paragraph.Paragraph(item, doc)
                            f.write(f"<p>{p.text}</p>\n")
                        elif item.tag.endswith('tbl'):
                            # Process table
                            f.write("<table border='1'>\n")
                            
                            tbl = item
                            for row in tbl.findall('.//{*}tr'):
                                f.write("<tr>\n")
                                for cell in row.findall('.//{*}tc'):
                                    text = ''.join(cell.xpath('.//text()'))
                                    f.write(f"<td>{text}</td>\n")
                                f.write("</tr>\n")
                            
                            f.write("</table>\n")
                    
                    f.write("</body></html>")
            
            elif input_format == "pdf":
                # Extract text from PDF
                try:
                    import fitz  # PyMuPDF
                    
                    pdf = fitz.open(input_path)
                    with open(html_path, "w", encoding="utf-8") as f:
                        f.write("<html><body>\n")
                        
                        for page_num in range(len(pdf)):
                            page = pdf[page_num]
                            text = page.get_text()
                            
                            # Simple text-to-HTML conversion
                            paragraphs = text.split('\n\n')
                            for p in paragraphs:
                                if p.strip():
                                    f.write(f"<p>{p.replace('\n', ' ')}</p>\n")
                        
                        f.write("</body></html>")
                except ImportError:
                    # Fallback using pdfminer
                    try:
                        from pdfminer.high_level import extract_text
                        
                        text = extract_text(input_path)
                        with open(html_path, "w", encoding="utf-8") as f:
                            f.write("<html><body>\n")
                            
                            # Simple text-to-HTML conversion
                            paragraphs = text.split('\n\n')
                            for p in paragraphs:
                                if p.strip():
                                    f.write(f"<p>{p.replace('\n', ' ')}</p>\n")
                            
                            f.write("</body></html>")
                    except ImportError:
                        raise ConversionError(
                            "Either PyMuPDF or pdfminer.six is required for PDF conversion. "
                            "Install with 'pip install pymupdf' or 'pip install pdfminer.six'."
                        )
            
            elif input_format == "md":
                # Convert markdown to HTML
                self._convert_markdown_to_html(input_path, html_path, parameters)
            
            elif input_format == "txt":
                # Convert text to HTML
                self._convert_text_to_html(input_path, html_path, parameters)
            
            elif input_format in ["html", "htm"]:
                # Already HTML
                import shutil
                shutil.copy2(input_path, html_path)
                
            else:
                raise ConversionError(f"Unsupported input format for data conversion: {input_format}")
            
            # Now extract data from HTML and convert to target format
            from bs4 import BeautifulSoup
            import pandas as pd
            
            with open(html_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")
            
            # Extract tables
            tables = soup.find_all("table")
            
            if tables:
                # Use tables if available
                dfs = pd.read_html(html_path)
                df = dfs[0]  # Use the first table
            else:
                # No tables found, create structured data from paragraphs
                paragraphs = soup.find_all("p")
                data = {"content": [p.get_text() for p in paragraphs]}
                df = pd.DataFrame(data)
                
            # Output to target format
            if output_format == "xlsx":
                df.to_excel(output_path, index=False)
            elif output_format == "csv":
                df.to_csv(output_path, index=False)
            elif output_format == "tsv":
                df.to_csv(output_path, sep="\t", index=False)
            elif output_format == "json":
                df.to_json(output_path, orient="records", indent=2)
            elif output_format == "xml":
                # Convert to XML using dicttoxml
                try:
                    from dicttoxml import dicttoxml
                    
                    data = df.to_dict(orient="records")
                    xml = dicttoxml(
                        data,
                        custom_root="data",
                        item_func=lambda x: "row",
                        attr_type=False
                    )
                    
                    with open(output_path, "wb") as f:
                        f.write(xml)
                except ImportError:
                    # Simple XML creation
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                        f.write('<data>\n')
                        
                        for _, row in df.iterrows():
                            f.write('  <row>\n')
                            for col, value in row.items():
                                if pd.isna(value):
                                    f.write(f'    <{col}/>\n')
                                else:
                                    f.write(f'    <{col}>{value}</{col}>\n')
                            f.write('  </row>\n')
                        
                        f.write('</data>\n')
            elif output_format == "yaml":
                # Output to YAML
                try:
                    import yaml
                    
                    data = df.to_dict(orient="records")
                    with open(output_path, "w", encoding="utf-8") as f:
                        yaml.dump(data, f, allow_unicode=True)
                except ImportError:
                    raise ConversionError(
                        "PyYAML is required for YAML conversion. "
                        "Install it with 'pip install pyyaml'."
                    )
            elif output_format == "ini":
                # Output to INI
                import configparser
                
                config = configparser.ConfigParser()
                
                # Create sections for each row
                for idx, row in df.iterrows():
                    section_name = f"row{idx}"
                    config[section_name] = {}
                    
                    for col, value in row.items():
                        if not pd.isna(value):
                            config[section_name][str(col)] = str(value)
                
                with open(output_path, "w", encoding="utf-8") as f:
                    config.write(f)
            elif output_format == "toml":
                # Output to TOML
                try:
                    import tomli_w
                    has_tomli_w = True
                except ImportError:
                    try:
                        import toml
                        has_tomli_w = False
                    except ImportError:
                        raise ConversionError(
                            "toml or tomli_w is required for TOML conversion. "
                            "Install it with 'pip install toml' or 'pip install tomli_w'."
                        )
                
                data = {"items": df.to_dict(orient="records")}
                
                if has_tomli_w:
                    with open(output_path, "wb") as f:
                        tomli_w.dump(data, f)
                else:
                    with open(output_path, "w", encoding="utf-8") as f:
                        toml.dump(data, f)
            
            return {
                "input_format": input_format,
                "output_format": output_format,
                "input_path": str(input_path),
                "output_path": str(output_path),
            }
            
        except Exception as e:
            raise ConversionError(
                f"Failed to convert {input_format} to {output_format}: {str(e)}"
            )
