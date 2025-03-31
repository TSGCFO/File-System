"""
Document format converters for FileConverter.

This module provides converters for document formats, including:
- Microsoft Word (.doc, .docx)
- Rich Text Format (.rtf)
- OpenDocument Text (.odt)
- PDF (.pdf)
- Plain Text (.txt)
- HTML (.html, .htm)
- Markdown (.md)
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
SUPPORTED_FORMATS = ["doc", "docx", "rtf", "odt", "pdf", "txt", "html", "htm", "md"]


class DocumentConverter(BaseConverter):
    """Converter for document formats."""
    
    @classmethod
    def get_input_formats(cls) -> List[str]:
        """Get the list of input formats supported by this converter."""
        return ["doc", "docx", "rtf", "odt", "txt", "html", "htm", "md"]
    
    @classmethod
    def get_output_formats(cls) -> List[str]:
        """Get the list of output formats supported by this converter."""
        return ["docx", "pdf", "txt", "html", "md"]
    
    @classmethod
    def get_format_extensions(cls, format_name: str) -> List[str]:
        """Get the list of file extensions for a specific format."""
        format_map = {
            "doc": ["doc"],
            "docx": ["docx"],
            "rtf": ["rtf"],
            "odt": ["odt"],
            "pdf": ["pdf"],
            "txt": ["txt"],
            "html": ["html", "htm"],
            "md": ["md", "markdown"],
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
        else:
            raise ConversionError(
                f"Conversion from {input_format} to {output_format} is not supported"
            )
        
        return result
    
    def get_parameters(self) -> Dict[str, Dict[str, Any]]:
        """Get the parameters supported by this converter."""
        return {
            "pdf": {
                "page_size": {
                    "type": "string",
                    "description": "Page size (e.g., A4, Letter)",
                    "default": "A4",
                    "options": ["A4", "Letter", "Legal"],
                },
                "orientation": {
                    "type": "string",
                    "description": "Page orientation",
                    "default": "portrait",
                    "options": ["portrait", "landscape"],
                },
                "margin": {
                    "type": "number",
                    "description": "Page margin in inches",
                    "default": 1.0,
                    "min": 0.0,
                    "max": 3.0,
                },
            },
            "html": {
                "css": {
                    "type": "string",
                    "description": "CSS file path or CSS content",
                    "default": None,
                },
                "template": {
                    "type": "string",
                    "description": "HTML template file path",
                    "default": None,
                },
            },
            "docx": {
                "template": {
                    "type": "string",
                    "description": "Template file path",
                    "default": None,
                },
            },
        }
    
    def _get_format_from_extension(self, extension: str) -> Optional[str]:
        """Get the format name from a file extension.
        
        Args:
            extension: File extension (without the dot).
        
        Returns:
            Format name, or None if the extension is not supported.
        """
        ext_lower = extension.lower()
        
        if ext_lower in ["html", "htm"]:
            return "html"
        elif ext_lower in ["md", "markdown"]:
            return "md"
        elif ext_lower in SUPPORTED_FORMATS:
            return ext_lower
        
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
