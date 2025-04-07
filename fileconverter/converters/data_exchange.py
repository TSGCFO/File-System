"""
Data exchange format converters for FileConverter.

This module provides converters for data exchange formats, including:
- JSON (.json)
- XML (.xml)
- YAML (.yaml, .yml)
- INI (.ini, .conf, .cfg)
- TOML (.toml)
- CSV (.csv)
- TSV (.tsv)
"""

import configparser
import csv
import json
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from fileconverter.core.registry import BaseConverter
from fileconverter.utils.error_handling import ConversionError
from fileconverter.utils.file_utils import get_file_extension, guess_encoding
from fileconverter.utils.logging_utils import get_logger
from fileconverter.utils.validation import validate_file_path

logger = get_logger(__name__)

# Define supported formats
SUPPORTED_FORMATS = ["json", "xml", "yaml", "yml", "ini", "toml", "csv", "tsv", 
                   "docx", "pdf", "txt", "html", "htm", "md", "xlsx", "xls"]


class DataExchangeConverter(BaseConverter):
    """Converter for data exchange formats."""
    
    @classmethod
    def get_input_formats(cls) -> List[str]:
        """Get the list of input formats supported by this converter."""
        return ["json", "xml", "yaml", "ini", "toml", "csv", "tsv", 
                "docx", "pdf", "txt", "html", "htm", "md", "xlsx"]
    
    @classmethod
    def get_output_formats(cls) -> List[str]:
        """Get the list of output formats supported by this converter."""
        return ["json", "xml", "yaml", "ini", "toml", "csv", "tsv", 
                "docx", "pdf", "txt", "html", "md", "xlsx"]
    
    @classmethod
    def get_format_extensions(cls, format_name: str) -> List[str]:
        """Get the list of file extensions for a specific format."""
        format_map = {
            "json": ["json"],
            "xml": ["xml"],
            "yaml": ["yaml", "yml"],
            "ini": ["ini", "conf", "cfg"],
            "toml": ["toml"],
            "csv": ["csv"],
            "tsv": ["tsv"],
            "docx": ["docx"],
            "pdf": ["pdf"],
            "txt": ["txt"],
            "html": ["html", "htm"],
            "md": ["md", "markdown"],
            "xlsx": ["xlsx"],
            "xls": ["xls"],
        }
        return format_map.get(format_name.lower(), [])
    
    def get_parameters(self) -> Dict[str, Dict[str, Any]]:
        """Get the parameters supported by this converter."""
        return {
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
                    "description": "Whether to write a header row",
                    "default": True,
                },
                "flatten": {
                    "type": "boolean",
                    "description": "Whether to flatten nested data",
                    "default": True,
                },
            },
        }
    
    def _normalize_format(self, extension: str) -> Optional[str]:
        """Normalize format name from file extension.
        
        Args:
            extension: File extension.
        
        Returns:
            Normalized format name or None if not supported.
        """
        if extension in ["yml", "yaml"]:
            return "yaml"
        elif extension in ["csv"]:
            return "csv"
        elif extension in ["tsv"]:
            return "tsv"
        elif extension in ["json", "xml", "ini", "toml"]:
            return extension
        elif extension in ["xlsx", "xls"]:
            return extension
        elif extension in ["docx", "pdf", "txt", "md"]:
            return extension
        
        return None
    
    def _load_data(
        self, 
        file_path: Path, 
        format_name: str,
        parameters: Dict[str, Any]
    ) -> Any:
        """Load data from a file.
        
        Args:
            file_path: Path to the file.
            format_name: Format of the file.
            parameters: Conversion parameters.
        
        Returns:
            Loaded data.
        
        Raises:
            ConversionError: If the data cannot be loaded.
        """
        if format_name == "json":
            return self._load_json(file_path, parameters)
        elif format_name == "xml":
            return self._load_xml(file_path, parameters)
        elif format_name == "yaml":
            return self._load_yaml(file_path, parameters)
        elif format_name == "ini":
            return self._load_ini(file_path, parameters)
        elif format_name == "toml":
            return self._load_toml(file_path, parameters)
        elif format_name == "csv":
            return self._load_csv(file_path, parameters)
        elif format_name == "tsv":
            return self._load_tsv(file_path, parameters)
        else:
            raise ConversionError(f"Unsupported format: {format_name}")
        
    def convert(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        temp_dir: Union[str, Path],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert a data file from one format to another.
        
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
        
        # Normalize formats
        input_format = self._normalize_format(input_ext)
        output_format = self._normalize_format(output_ext)
        
        if not input_format:
            raise ConversionError(f"Unsupported input format: {input_ext}")
        
        if not output_format:
            raise ConversionError(f"Unsupported output format: {output_ext}")
        
        # Load data from input file
        try:
            data = self._load_data(input_path, input_format, parameters)
        except Exception as e:
            raise ConversionError(f"Failed to load {input_format} data: {str(e)}")
        
        # Save data to output file
        try:
            self._save_data(data, output_path, output_format, parameters)
        except Exception as e:
            raise ConversionError(f"Failed to save {output_format} data: {str(e)}")
        
        # Handle conversions that require special processing
        if (input_format in ["json", "xml", "yaml", "ini", "toml", "csv", "tsv"] and 
            output_format in ["docx", "pdf", "html", "md"]):
            try:
                # Convert to document format
                self._convert_to_document_format(data, output_path, output_format, parameters)
            except Exception as e:
                raise ConversionError(f"Failed to convert to {output_format}: {str(e)}")
        
        return {
            "input_format": input_format,
            "output_format": output_format,
            "input_path": str(input_path),
            "output_path": str(output_path),
        }
    
    def _save_data(
        self, 
        data: Any, 
        file_path: Path, 
        format_name: str,
        parameters: Dict[str, Any]
    ) -> None:
        """Save data to a file.
        
        Args:
            data: Data to save.
            file_path: Path where to save the file.
            format_name: Format of the file.
            parameters: Conversion parameters.
        
        Raises:
            ConversionError: If the data cannot be saved.
        """
        if format_name == "json":
            self._save_json(data, file_path, parameters)
        elif format_name == "xml":
            self._save_xml(data, file_path, parameters)
        elif format_name == "yaml":
            self._save_yaml(data, file_path, parameters)
        elif format_name == "ini":
            self._save_ini(data, file_path, parameters)
        elif format_name == "toml":
            self._save_toml(data, file_path, parameters)
        elif format_name == "csv":
            self._save_csv(data, file_path, parameters)
        elif format_name == "tsv":
            self._save_tsv(data, file_path, parameters)
        elif format_name == "xlsx":
            self._save_xlsx(data, file_path, parameters)
        else:
            raise ConversionError(f"Unsupported format: {format_name}")
    
    def _load_json(
        self, 
        file_path: Path, 
        parameters: Dict[str, Any]
    ) -> Any:
        """Load data from a JSON file.
        
        Args:
            file_path: Path to the file.
            parameters: Conversion parameters.
        
        Returns:
            Loaded data.
        
        Raises:
            ConversionError: If the data cannot be loaded.
        """
        encoding = parameters.get("encoding")
        
        if not encoding:
            encoding = guess_encoding(file_path)
        
        try:
            with open(file_path, "r", encoding=encoding) as f:
                return json.load(f)
        except Exception as e:
            raise ConversionError(f"Failed to load JSON file: {str(e)}")
    
    def _load_xml(
        self, 
        file_path: Path, 
        parameters: Dict[str, Any]
    ) -> Any:
        """Load data from an XML file.
        
        Args:
            file_path: Path to the file.
            parameters: Conversion parameters.
        
        Returns:
            Loaded data.
        
        Raises:
            ConversionError: If the data cannot be loaded.
        """
        encoding = parameters.get("encoding")
        
        if not encoding:
            encoding = guess_encoding(file_path)
        
        try:
            # Use xmltodict if available (more powerful)
            try:
                import xmltodict
                
                with open(file_path, "r", encoding=encoding) as f:
                    return xmltodict.parse(f.read())
            except ImportError:
                # Fallback to built-in xml.etree
                import xml.etree.ElementTree as ET
                
                def element_to_dict(element):
                    """Convert an XML element to a dictionary."""
                    result = {}
                    
                    # Add attributes
                    for key, value in element.attrib.items():
                        result[f"@{key}"] = value
                    
                    # Add children
                    for child in element:
                        child_dict = element_to_dict(child)
                        
                        if child.tag in result:
                            if not isinstance(result[child.tag], list):
                                result[child.tag] = [result[child.tag]]
                            result[child.tag].append(child_dict)
                        else:
                            result[child.tag] = child_dict
                    
                    # Add text
                    if element.text and element.text.strip():
                        if not result:
                            return element.text.strip()
                        else:
                            result["#text"] = element.text.strip()
                    
                    return result
                
                tree = ET.parse(file_path)
                root = tree.getroot()
                
                return {root.tag: element_to_dict(root)}
        except Exception as e:
            raise ConversionError(f"Failed to load XML file: {str(e)}")
    
    def _load_yaml(
        self, 
        file_path: Path, 
        parameters: Dict[str, Any]
    ) -> Any:
        """Load data from a YAML file.
        
        Args:
            file_path: Path to the file.
            parameters: Conversion parameters.
        
        Returns:
            Loaded data.
        
        Raises:
            ConversionError: If the data cannot be loaded.
        """
        encoding = parameters.get("encoding")
        
        if not encoding:
            encoding = guess_encoding(file_path)
        
        try:
            import yaml
            
            with open(file_path, "r", encoding=encoding) as f:
                return yaml.safe_load(f)
        except ImportError:
            raise ConversionError(
                "PyYAML is required for YAML conversion. "
                "Install it with 'pip install pyyaml'."
            )
        except Exception as e:
            raise ConversionError(f"Failed to load YAML file: {str(e)}")
    
    def _load_ini(
        self, 
        file_path: Path, 
        parameters: Dict[str, Any]
    ) -> Any:
        """Load data from an INI file.
        
        Args:
            file_path: Path to the file.
            parameters: Conversion parameters.
        
        Returns:
            Loaded data.
        
        Raises:
            ConversionError: If the data cannot be loaded.
        """
        encoding = parameters.get("encoding")
        
        if not encoding:
            encoding = guess_encoding(file_path)
        
        try:
            config = configparser.ConfigParser()
            config.read(file_path, encoding=encoding)
            
            # Convert to dictionary
            result = {}
            
            for section in config.sections():
                result[section] = {}
                
                for key, value in config[section].items():
                    result[section][key] = value
            
            return result
        except Exception as e:
            raise ConversionError(f"Failed to load INI file: {str(e)}")
    
    def _load_toml(
        self, 
        file_path: Path, 
        parameters: Dict[str, Any]
    ) -> Any:
        """Load data from a TOML file.
        
        Args:
            file_path: Path to the file.
            parameters: Conversion parameters.
        
        Returns:
            Loaded data.
        
        Raises:
            ConversionError: If the data cannot be loaded.
        """
        encoding = parameters.get("encoding")
        
        if not encoding:
            encoding = guess_encoding(file_path)
        
        try:
            # Try different TOML libraries
            try:
                import tomli
                
                with open(file_path, "rb") as f:
                    return tomli.load(f)
            except ImportError:
                try:
                    import toml
                    
                    with open(file_path, "r", encoding=encoding) as f:
                        return toml.load(f)
                except ImportError:
                    raise ConversionError(
                        "toml or tomli is required for TOML conversion. "
                        "Install it with 'pip install toml' or 'pip install tomli'."
                    )
        except Exception as e:
            raise ConversionError(f"Failed to load TOML file: {str(e)}")
    
    def _load_csv(
        self, 
        file_path: Path, 
        parameters: Dict[str, Any]
    ) -> Any:
        """Load data from a CSV file.
        
        Args:
            file_path: Path to the file.
            parameters: Conversion parameters.
        
        Returns:
            Loaded data.
        
        Raises:
            ConversionError: If the data cannot be loaded.
        """
        delimiter = parameters.get("delimiter", ",")
        quotechar = parameters.get("quotechar", '"')
        encoding = parameters.get("encoding")
        header = parameters.get("header", True)
        
        if not encoding:
            encoding = guess_encoding(file_path)
        
        try:
            # Use pandas if available (more powerful)
            try:
                import pandas as pd
                
                df = pd.read_csv(
                    file_path,
                    delimiter=delimiter,
                    quotechar=quotechar,
                    encoding=encoding,
                    header=0 if header else None
                )
                
                # Convert to list of dictionaries
                return df.to_dict(orient="records")
            except ImportError:
                # Fallback to built-in csv
                with open(file_path, "r", encoding=encoding, newline="") as f:
                    reader = csv.reader(f, delimiter=delimiter, quotechar=quotechar)
                    
                    if header:
                        headers = next(reader)
                        return [dict(zip(headers, row)) for row in reader]
                    else:
                        return [row for row in reader]
        except Exception as e:
            raise ConversionError(f"Failed to load CSV file: {str(e)}")
    
    def _load_tsv(
        self, 
        file_path: Path, 
        parameters: Dict[str, Any]
    ) -> Any:
        """Load data from a TSV file.
        
        Args:
            file_path: Path to the file.
            parameters: Conversion parameters.
        
        Returns:
            Loaded data.
        
        Raises:
            ConversionError: If the data cannot be loaded.
        """
        # Use CSV loader with tab delimiter
        parameters["delimiter"] = "\t"
        return self._load_csv(file_path, parameters)
    
    def _save_json(
        self, 
        data: Any, 
        file_path: Path, 
        parameters: Dict[str, Any]
    ) -> None:
        """Save data to a JSON file.
        
        Args:
            data: Data to save.
            file_path: Path where to save the file.
            parameters: Conversion parameters.
        
        Raises:
            ConversionError: If the data cannot be saved.
        """
        indent = parameters.get("indent", 2)
        encoding = parameters.get("encoding", "utf-8")
        ensure_ascii = not parameters.get("unicode", True)
        
        try:
            with open(file_path, "w", encoding=encoding) as f:
                json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)
        except Exception as e:
            raise ConversionError(f"Failed to save JSON file: {str(e)}")
    
    def _save_xml(
        self, 
        data: Any, 
        file_path: Path, 
        parameters: Dict[str, Any]
    ) -> None:
        """Save data to an XML file.
        
        Args:
            data: Data to save.
            file_path: Path where to save the file.
            parameters: Conversion parameters.
        
        Raises:
            ConversionError: If the data cannot be saved.
        """
        encoding = parameters.get("encoding", "utf-8")
        
        try:
            # Use dicttoxml if available (more powerful)
            try:
                import dicttoxml
                
                xml = dicttoxml.dicttoxml(
                    data,
                    custom_root=parameters.get("root", "root"),
                    attr_type=False
                )
                
                with open(file_path, "wb") as f:
                    f.write(xml)
            except ImportError:
                # Fallback to built-in xml.etree
                import xml.etree.ElementTree as ET
                import xml.dom.minidom as minidom
                
                def dict_to_element(parent, data):
                    """Convert a dictionary to XML elements."""
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if key.startswith("@"):
                                # Attribute
                                parent.set(key[1:], str(value))
                            elif key == "#text":
                                # Text content
                                parent.text = str(value)
                            else:
                                # Child element
                                if isinstance(value, list):
                                    # List of elements
                                    for item in value:
                                        child = ET.SubElement(parent, key)
                                        dict_to_element(child, item)
                                else:
                                    # Single element
                                    child = ET.SubElement(parent, key)
                                    dict_to_element(child, value)
                    else:
                        # Simple value
                        parent.text = str(data)
                
                # Create root element
                root_tag = next(iter(data)) if isinstance(data, dict) else "root"
                root = ET.Element(root_tag)
                
                # Build the tree
                if isinstance(data, dict) and root_tag in data:
                    dict_to_element(root, data[root_tag])
                else:
                    dict_to_element(root, data)
                
                # Create the tree and write to file
                tree = ET.ElementTree(root)
                
                # Format with proper indentation
                xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
                
                with open(file_path, "w", encoding=encoding) as f:
                    f.write(xmlstr)
        except Exception as e:
            raise ConversionError(f"Failed to save XML file: {str(e)}")
    
    def _save_yaml(
        self, 
        data: Any, 
        file_path: Path, 
        parameters: Dict[str, Any]
    ) -> None:
        """Save data to a YAML file.
        
        Args:
            data: Data to save.
            file_path: Path where to save the file.
            parameters: Conversion parameters.
        
        Raises:
            ConversionError: If the data cannot be saved.
        """
        encoding = parameters.get("encoding", "utf-8")
        
        try:
            import yaml
            
            with open(file_path, "w", encoding=encoding) as f:
                yaml.dump(
                    data,
                    f,
                    default_flow_style=False,
                    sort_keys=parameters.get("sort_keys", False),
                    allow_unicode=True
                )
        except ImportError:
            raise ConversionError(
                "PyYAML is required for YAML conversion. "
                "Install it with 'pip install pyyaml'."
            )
        except Exception as e:
            raise ConversionError(f"Failed to save YAML file: {str(e)}")
    
    def _save_ini(
        self, 
        data: Any, 
        file_path: Path, 
        parameters: Dict[str, Any]
    ) -> None:
        """Save data to an INI file.
        
        Args:
            data: Data to save.
            file_path: Path where to save the file.
            parameters: Conversion parameters.
        
        Raises:
            ConversionError: If the data cannot be saved.
        """
        encoding = parameters.get("encoding", "utf-8")
        
        try:
            config = configparser.ConfigParser()
            
            if not isinstance(data, dict):
                raise ConversionError("Data must be a dictionary for INI files")
            
            for section, values in data.items():
                if not isinstance(values, dict):
                    continue
                
                config[section] = {}
                
                for key, value in values.items():
                    config[section][key] = str(value)
            
            with open(file_path, "w", encoding=encoding) as f:
                config.write(f)
        except Exception as e:
            raise ConversionError(f"Failed to save INI file: {str(e)}")
    
    def _save_toml(
        self, 
        data: Any, 
        file_path: Path, 
        parameters: Dict[str, Any]
    ) -> None:
        """Save data to a TOML file.
        
        Args:
            data: Data to save.
            file_path: Path where to save the file.
            parameters: Conversion parameters.
        
        Raises:
            ConversionError: If the data cannot be saved.
        """
        encoding = parameters.get("encoding", "utf-8")
        
        try:
            # Try different TOML libraries
            try:
                import tomli_w
                
                with open(file_path, "wb") as f:
                    tomli_w.dump(data, f)
            except ImportError:
                try:
                    import toml
                    
                    with open(file_path, "w", encoding=encoding) as f:
                        toml.dump(data, f)
                except ImportError:
                    raise ConversionError(
                        "toml or tomli_w is required for TOML conversion. "
                        "Install it with 'pip install toml' or 'pip install tomli_w'."
                    )
        except Exception as e:
            raise ConversionError(f"Failed to save TOML file: {str(e)}")
    
    def _save_csv(
        self, 
        data: Any, 
        file_path: Path, 
        parameters: Dict[str, Any]
    ) -> None:
        """Save data to a CSV file.
        
        Args:
            data: Data to save.
            file_path: Path where to save the file.
            parameters: Conversion parameters.
        
        Raises:
            ConversionError: If the data cannot be saved.
        """
        delimiter = parameters.get("delimiter", ",")
        quotechar = parameters.get("quotechar", '"')
        encoding = parameters.get("encoding", "utf-8")
        header = parameters.get("header", True)
        
        try:
            # Normalize data to a list of dictionaries or a list of lists
            rows = self._normalize_data_for_csv(data, header, parameters)
            
            # Use pandas if available (more powerful)
            try:
                import pandas as pd
                
                if header and rows and isinstance(rows[0], dict):
                    # Convert list of dictionaries to DataFrame
                    df = pd.DataFrame(rows)
                else:
                    # Convert list of lists to DataFrame
                    df = pd.DataFrame(rows)
                
                # Save to CSV
                df.to_csv(
                    file_path,
                    sep=delimiter,
                    index=False,
                    quotechar=quotechar,
                    encoding=encoding,
                    header=header
                )
            except ImportError:
                # Fallback to built-in csv
                with open(file_path, "w", encoding=encoding, newline="") as f:
                    writer = csv.writer(f, delimiter=delimiter, quotechar=quotechar)
                    
                    if header and rows and isinstance(rows[0], dict):
                        # Write header row
                        headers = list(rows[0].keys())
                        writer.writerow(headers)
                        
                        # Write data rows
                        for row in rows:
                            writer.writerow([row.get(h, "") for h in headers])
                    else:
                        # Write rows directly
                        writer.writerows(rows)
        except Exception as e:
            raise ConversionError(f"Failed to save CSV file: {str(e)}")
    
    def _save_tsv(
        self, 
        data: Any, 
        file_path: Path, 
        parameters: Dict[str, Any]
    ) -> None:
        """Save data to a TSV file.
        
        Args:
            data: Data to save.
            file_path: Path where to save the file.
            parameters: Conversion parameters.
        
        Raises:
            ConversionError: If the data cannot be saved.
        """
        # Use CSV saver with tab delimiter
        parameters["delimiter"] = "\t"
        self._save_csv(data, file_path, parameters)

    def _save_xlsx(
        self, 
        data: Any, 
        file_path: Path, 
        parameters: Dict[str, Any]
    ) -> None:
        """Save data to an Excel file.
        
        Args:
            data: Data to save.
            file_path: Path where to save the file.
            parameters: Conversion parameters.
        
        Raises:
            ConversionError: If the data cannot be saved.
        """
        try:
            import pandas as pd
            
            # Convert data to DataFrame
            if isinstance(data, dict):
                # Handle nested data structures
                if "data" in data and isinstance(data["data"], dict) and "row" in data["data"]:
                    # XML-like structure with rows
                    df = pd.DataFrame(data["data"]["row"])
                elif "items" in data:
                    # TOML/YAML-like structure with items list
                    df = pd.DataFrame(data["items"])
                else:
                    # Try to flatten the dictionary
                    flattened_data = self._flatten_dict(data)
                    df = pd.DataFrame([flattened_data])
            elif isinstance(data, list):
                # Simple list of dictionaries
                df = pd.DataFrame(data)
            else:
                raise ConversionError(f"Cannot convert data of type {type(data)} to Excel")
            
            # Save to Excel file
            sheet_name = parameters.get("sheet_name", "Sheet1")
            index = parameters.get("index", False)
            
            df.to_excel(
                file_path,
                sheet_name=sheet_name,
                index=index
            )
        except ImportError:
            raise ConversionError(
                "pandas and openpyxl are required for Excel conversion. "
                "Install with 'pip install pandas openpyxl'."
            )
        except Exception as e:
            raise ConversionError(f"Failed to save Excel file: {str(e)}")
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """Flatten a nested dictionary.
        
        Args:
            d: Dictionary to flatten.
            parent_key: Parent key for nested values.
            sep: Separator for nested keys.
            
        Returns:
            Flattened dictionary.
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    def _normalize_data_for_csv(
        self, 
        data: Any, 
        header: bool, 
        parameters: Dict[str, Any]
    ) -> List:
        """Normalize data for CSV output.
        
        Args:
            data: Data to normalize.
            header: Whether a header row is expected.
            parameters: Conversion parameters.
        
        Returns:
            Normalized data as a list of dictionaries or list of lists.
        
        Raises:
            ConversionError: If the data cannot be normalized.
        """
        flatten = parameters.get("flatten", True)
        
        if isinstance(data, list):
            if not data:
                return []
            
            if isinstance(data[0], dict):
                # Already a list of dictionaries
                if flatten:
                    # Flatten nested dictionaries
                    return [self._flatten_dict(item) for item in data]
                return data
            elif isinstance(data[0], list):
                # Already a list of lists
                return data
            else:
                # List of primitive values
                return [[item] for item in data]
        elif isinstance(data, dict):
            if "data" in data and isinstance(data["data"], dict) and "row" in data["data"]:
                # XML-like structure with rows
                rows = data["data"]["row"]
                if not isinstance(rows, list):
                    rows = [rows]
                
                if flatten:
                    # Flatten nested dictionaries
                    return [self._flatten_dict(item) for item in rows]
                return rows
            elif "items" in data and isinstance(data["items"], list):
                # TOML/YAML-like structure with items list
                if flatten:
                    # Flatten nested dictionaries
                    return [self._flatten_dict(item) for item in data["items"]]
                return data["items"]
            else:
                # Regular dictionary
                if flatten:
                    # Flatten nested dictionaries
                    return [self._flatten_dict(data)]
                return [data]
        else:
            # Primitive value
            if header:
                return [{"value": data}]
            else:
                return [[data]]
