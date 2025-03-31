"""
Spreadsheet format converters for FileConverter.

This module provides converters for spreadsheet formats, including:
- Microsoft Excel (.xls, .xlsx)
- CSV (.csv)
- TSV (.tsv)
- JSON (.json)
- XML (.xml)
- HTML (.html)
"""

import csv
import json
import tempfile
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from fileconverter.core.registry import BaseConverter
from fileconverter.utils.error_handling import ConversionError
from fileconverter.utils.file_utils import get_file_extension, guess_encoding
from fileconverter.utils.logging_utils import get_logger
from fileconverter.utils.validation import validate_file_path

logger = get_logger(__name__)

# Define supported formats
SUPPORTED_FORMATS = ["xlsx", "xls", "csv", "tsv", "json", "xml", "html"]


class SpreadsheetConverter(BaseConverter):
    """Converter for spreadsheet formats."""
    
    @classmethod
    def get_input_formats(cls) -> List[str]:
        """Get the list of input formats supported by this converter."""
        return ["xlsx", "xls", "csv", "tsv", "json"]
    
    @classmethod
    def get_output_formats(cls) -> List[str]:
        """Get the list of output formats supported by this converter."""
        return ["xlsx", "csv", "tsv", "json", "html", "xml"]
    
    @classmethod
    def get_format_extensions(cls, format_name: str) -> List[str]:
        """Get the list of file extensions for a specific format."""
        format_map = {
            "xlsx": ["xlsx"],
            "xls": ["xls"],
            "csv": ["csv"],
            "tsv": ["tsv"],
            "json": ["json"],
            "xml": ["xml"],
            "html": ["html", "htm"],
        }
        return format_map.get(format_name.lower(), [])
    
    def convert(
        self, 
        input_path: Union[str, Path], 
        output_path: Union[str, Path],
        temp_dir: Union[str, Path],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert a spreadsheet from one format to another.
        
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
        input_format = input_ext
        output_format = output_ext
        
        # Verify supported formats
        if input_format not in self.get_input_formats():
            raise ConversionError(f"Unsupported input format: {input_format}")
        
        if output_format not in self.get_output_formats():
            raise ConversionError(f"Unsupported output format: {output_format}")
        
        # Determine conversion method based on input and output formats
        try:
            # Most conversions will use pandas
            import pandas as pd
            
            # Load spreadsheet data based on input format
            if input_format in ["xlsx", "xls"]:
                df = self._load_excel(input_path, parameters)
            elif input_format == "csv":
                df = self._load_csv(input_path, parameters)
            elif input_format == "tsv":
                df = self._load_tsv(input_path, parameters)
            elif input_format == "json":
                df = self._load_json(input_path, parameters)
            else:
                raise ConversionError(f"Unsupported input format: {input_format}")
            
            # Save spreadsheet data based on output format
            if output_format in ["xlsx", "xls"]:
                self._save_excel(df, output_path, parameters)
            elif output_format == "csv":
                self._save_csv(df, output_path, parameters)
            elif output_format == "tsv":
                self._save_tsv(df, output_path, parameters)
            elif output_format == "json":
                self._save_json(df, output_path, parameters)
            elif output_format == "html":
                self._save_html(df, output_path, parameters)
            elif output_format == "xml":
                self._save_xml(df, output_path, parameters)
            else:
                raise ConversionError(f"Unsupported output format: {output_format}")
        
        except ImportError as e:
            raise ConversionError(
                f"Missing required dependency: {str(e)}. "
                "Please install pandas with 'pip install pandas'."
            )
        except Exception as e:
            raise ConversionError(
                f"Failed to convert {input_format} to {output_format}: {str(e)}"
            )
        
        return {
            "input_format": input_format,
            "output_format": output_format,
            "input_path": str(input_path),
            "output_path": str(output_path),
            "rows_processed": len(df) if 'df' in locals() else None,
        }
    
    def get_parameters(self) -> Dict[str, Dict[str, Any]]:
        """Get the parameters supported by this converter."""
        return {
            "excel": {
                "sheet_name": {
                    "type": "string",
                    "description": "Sheet name to read/write (excel only)",
                    "default": 0,  # 0 = first sheet
                },
                "header": {
                    "type": "boolean",
                    "description": "Whether the file has a header row",
                    "default": True,
                },
                "index": {
                    "type": "boolean",
                    "description": "Whether to include index in output",
                    "default": False,
                },
            },
            "csv": {
                "delimiter": {
                    "type": "string",
                    "description": "Delimiter character",
                    "default": ",",
                },
                "quotechar": {
                    "type": "string",
                    "description": "Quote character",
                    "default": '"',
                },
                "encoding": {
                    "type": "string",
                    "description": "File encoding",
                    "default": "utf-8",
                },
                "header": {
                    "type": "boolean",
                    "description": "Whether the file has a header row",
                    "default": True,
                },
            },
            "json": {
                "orient": {
                    "type": "string",
                    "description": "JSON orientation",
                    "default": "records",
                    "options": ["records", "columns", "index", "split", "table"],
                },
                "indent": {
                    "type": "integer",
                    "description": "Indentation level",
                    "default": 2,
                },
            },
            "html": {
                "table_id": {
                    "type": "string",
                    "description": "HTML table ID",
                    "default": "data",
                },
                "index": {
                    "type": "boolean",
                    "description": "Whether to include index in output",
                    "default": False,
                },
                "classes": {
                    "type": "string",
                    "description": "CSS classes for the table",
                    "default": "dataframe",
                },
                "escape": {
                    "type": "boolean",
                    "description": "Whether to escape HTML entities",
                    "default": True,
                },
            },
            "xml": {
                "root": {
                    "type": "string",
                    "description": "Root element name",
                    "default": "data",
                },
                "row": {
                    "type": "string",
                    "description": "Row element name",
                    "default": "row",
                },
            },
        }
    
    def _load_excel(self, file_path: Path, parameters: Dict[str, Any]) -> "pd.DataFrame":
        """Load data from an Excel file.
        
        Args:
            file_path: Path to the Excel file.
            parameters: Conversion parameters.
        
        Returns:
            Pandas DataFrame with the loaded data.
        
        Raises:
            ConversionError: If the file cannot be loaded.
        """
        import pandas as pd
        
        sheet_name = parameters.get("sheet_name", 0)
        header = 0 if parameters.get("header", True) else None
        
        try:
            return pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                header=header
            )
        except Exception as e:
            raise ConversionError(f"Failed to load Excel file: {str(e)}")
    
    def _load_csv(self, file_path: Path, parameters: Dict[str, Any]) -> "pd.DataFrame":
        """Load data from a CSV file.
        
        Args:
            file_path: Path to the CSV file.
            parameters: Conversion parameters.
        
        Returns:
            Pandas DataFrame with the loaded data.
        
        Raises:
            ConversionError: If the file cannot be loaded.
        """
        import pandas as pd
        
        delimiter = parameters.get("delimiter", ",")
        quotechar = parameters.get("quotechar", '"')
        encoding = parameters.get("encoding")
        header = 0 if parameters.get("header", True) else None
        
        if not encoding:
            encoding = guess_encoding(file_path)
        
        try:
            return pd.read_csv(
                file_path,
                delimiter=delimiter,
                quotechar=quotechar,
                encoding=encoding,
                header=header
            )
        except Exception as e:
            raise ConversionError(f"Failed to load CSV file: {str(e)}")
    
    def _load_tsv(self, file_path: Path, parameters: Dict[str, Any]) -> "pd.DataFrame":
        """Load data from a TSV file.
        
        Args:
            file_path: Path to the TSV file.
            parameters: Conversion parameters.
        
        Returns:
            Pandas DataFrame with the loaded data.
        
        Raises:
            ConversionError: If the file cannot be loaded.
        """
        # Use CSV loader with tab delimiter
        parameters["delimiter"] = "\t"
        return self._load_csv(file_path, parameters)
    
    def _load_json(self, file_path: Path, parameters: Dict[str, Any]) -> "pd.DataFrame":
        """Load data from a JSON file.
        
        Args:
            file_path: Path to the JSON file.
            parameters: Conversion parameters.
        
        Returns:
            Pandas DataFrame with the loaded data.
        
        Raises:
            ConversionError: If the file cannot be loaded.
        """
        import pandas as pd
        
        orient = parameters.get("orient", "records")
        encoding = parameters.get("encoding", "utf-8")
        
        try:
            return pd.read_json(
                file_path,
                orient=orient,
                encoding=encoding
            )
        except Exception as e:
            raise ConversionError(f"Failed to load JSON file: {str(e)}")
    
    def _save_excel(
        self, 
        df: "pd.DataFrame", 
        file_path: Path, 
        parameters: Dict[str, Any]
    ) -> None:
        """Save data to an Excel file.
        
        Args:
            df: Pandas DataFrame to save.
            file_path: Path where to save the file.
            parameters: Conversion parameters.
        
        Raises:
            ConversionError: If the file cannot be saved.
        """
        sheet_name = parameters.get("sheet_name", "Sheet1")
        index = parameters.get("index", False)
        
        try:
            df.to_excel(
                file_path,
                sheet_name=sheet_name,
                index=index
            )
        except Exception as e:
            raise ConversionError(f"Failed to save Excel file: {str(e)}")
    
    def _save_csv(
        self, 
        df: "pd.DataFrame", 
        file_path: Path, 
        parameters: Dict[str, Any]
    ) -> None:
        """Save data to a CSV file.
        
        Args:
            df: Pandas DataFrame to save.
            file_path: Path where to save the file.
            parameters: Conversion parameters.
        
        Raises:
            ConversionError: If the file cannot be saved.
        """
        delimiter = parameters.get("delimiter", ",")
        quotechar = parameters.get("quotechar", '"')
        encoding = parameters.get("encoding", "utf-8")
        index = parameters.get("index", False)
        header = parameters.get("header", True)
        
        try:
            df.to_csv(
                file_path,
                sep=delimiter,
                quotechar=quotechar,
                encoding=encoding,
                index=index,
                header=header
            )
        except Exception as e:
            raise ConversionError(f"Failed to save CSV file: {str(e)}")
    
    def _save_tsv(
        self, 
        df: "pd.DataFrame", 
        file_path: Path, 
        parameters: Dict[str, Any]
    ) -> None:
        """Save data to a TSV file.
        
        Args:
            df: Pandas DataFrame to save.
            file_path: Path where to save the file.
            parameters: Conversion parameters.
        
        Raises:
            ConversionError: If the file cannot be saved.
        """
        # Use CSV saver with tab delimiter
        parameters["delimiter"] = "\t"
        return self._save_csv(df, file_path, parameters)
    
    def _save_json(
        self, 
        df: "pd.DataFrame", 
        file_path: Path, 
        parameters: Dict[str, Any]
    ) -> None:
        """Save data to a JSON file.
        
        Args:
            df: Pandas DataFrame to save.
            file_path: Path where to save the file.
            parameters: Conversion parameters.
        
        Raises:
            ConversionError: If the file cannot be saved.
        """
        orient = parameters.get("orient", "records")
        indent = parameters.get("indent", 2)
        
        try:
            df.to_json(
                file_path,
                orient=orient,
                indent=indent
            )
        except Exception as e:
            raise ConversionError(f"Failed to save JSON file: {str(e)}")
    
    def _save_html(
        self, 
        df: "pd.DataFrame", 
        file_path: Path, 
        parameters: Dict[str, Any]
    ) -> None:
        """Save data to an HTML file.
        
        Args:
            df: Pandas DataFrame to save.
            file_path: Path where to save the file.
            parameters: Conversion parameters.
        
        Raises:
            ConversionError: If the file cannot be saved.
        """
        table_id = parameters.get("table_id", "data")
        index = parameters.get("index", False)
        classes = parameters.get("classes", "dataframe")
        escape = parameters.get("escape", True)
        
        try:
            # Generate HTML table
            html_table = df.to_html(
                index=index,
                table_id=table_id,
                classes=classes,
                escape=escape
            )
            
            # Create full HTML document
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <title>Data Table</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    tr:nth-child(even) {{ background-color: #f9f9f9; }}
                    .dataframe {{ width: 100%; }}
                </style>
            </head>
            <body>
                <h1>Data Table</h1>
                {html_table}
            </body>
            </html>
            """
            
            # Write to file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
        
        except Exception as e:
            raise ConversionError(f"Failed to save HTML file: {str(e)}")
    
    def _save_xml(
        self, 
        df: "pd.DataFrame", 
        file_path: Path, 
        parameters: Dict[str, Any]
    ) -> None:
        """Save data to an XML file.
        
        Args:
            df: Pandas DataFrame to save.
            file_path: Path where to save the file.
            parameters: Conversion parameters.
        
        Raises:
            ConversionError: If the file cannot be saved.
        """
        root_name = parameters.get("root", "data")
        row_name = parameters.get("row", "row")
        
        try:
            from dicttoxml import dicttoxml
            
            # Convert DataFrame to list of dictionaries
            data = df.to_dict(orient="records")
            
            # Convert to XML
            xml = dicttoxml(
                data,
                custom_root=root_name,
                item_func=lambda x: row_name,
                attr_type=False
            )
            
            # Write to file
            with open(file_path, "wb") as f:
                f.write(xml)
        
        except ImportError:
            # Fallback if dicttoxml is not available
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n')
                    f.write(f'<{root_name}>\n')
                    
                    for _, row in df.iterrows():
                        f.write(f'  <{row_name}>\n')
                        for col, value in row.items():
                            if pd.isna(value):
                                f.write(f'    <{col}/>\n')
                            else:
                                f.write(f'    <{col}>{value}</{col}>\n')
                        f.write(f'  </{row_name}>\n')
                    
                    f.write(f'</{root_name}>\n')
            
            except Exception as e:
                raise ConversionError(f"Failed to save XML file: {str(e)}")
        
        except Exception as e:
            raise ConversionError(f"Failed to save XML file: {str(e)}")
