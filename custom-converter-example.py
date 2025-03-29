"""
Example Custom Converter Module

This module demonstrates how to create a custom converter for the Universal File Format Converter.
It implements converters for SQL dump files to JSON and back.
"""

import json
import logging
import re
from typing import Dict, List, Any

# Import the register_converter function from the main module
try:
    from format_converter import register_converter
except ImportError:
    # If running as standalone, define a dummy function
    def register_converter(source_format, target_format, converter_func):
        """Dummy register_converter function."""
        pass

logger = logging.getLogger(__name__)

def sql_dump_to_json(input_path: str, output_path: str) -> None:
    """
    Convert a SQL dump file to JSON format.
    
    Args:
        input_path: Path to the input SQL dump file
        output_path: Path to save the converted JSON file
    
    Raises:
        Exception: If conversion fails
    """
    try:
        # Read the SQL dump file
        with open(input_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Parse CREATE TABLE statements
        tables: Dict[str, Dict[str, Any]] = {}
        create_table_pattern = r'CREATE TABLE [`"]?(\w+)[`"]?\s*\((.*?)\);'
        create_table_matches = re.finditer(create_table_pattern, sql_content, re.DOTALL)
        
        for match in create_table_matches:
            table_name = match.group(1)
            table_def = match.group(2)
            
            # Extract column definitions
            columns = []
            for line in table_def.split('\n'):
                line = line.strip()
                if line and not line.startswith('PRIMARY KEY') and not line.startswith('KEY '):
                    # Basic column extraction - This is simplified
                    col_match = re.match(r'[`"]?(\w+)[`"]?\s+([A-Za-z0-9()]+)', line)
                    if col_match:
                        col_name = col_match.group(1)
                        col_type = col_match.group(2)
                        columns.append({
                            "name": col_name,
                            "type": col_type
                        })
            
            tables[table_name] = {
                "columns": columns,
                "data": []
            }
        
        # Parse INSERT statements
        insert_pattern = r'INSERT INTO [`"]?(\w+)[`"]?\s+VALUES\s+(.+?);'
        insert_matches = re.finditer(insert_pattern, sql_content, re.DOTALL)
        
        for match in insert_matches:
            table_name = match.group(1)
            values_str = match.group(2)
            
            # Skip if table not found in schema
            if table_name not in tables:
                continue
            
            # Parse values
            # This is a simplified parser - a real one would handle escaping, etc.
            values_pattern = r'\((.+?)\)'
            values_matches = re.finditer(values_pattern, values_str)
            
            for val_match in values_matches:
                val_str = val_match.group(1)
                
                # Split by comma but respect quoted strings
                # This is a simplified approach
                values = []
                current = ""
                in_quotes = False
                quote_char = None
                
                for char in val_str:
                    if char in ['"', "'"] and (not in_quotes or char == quote_char):
                        in_quotes = not in_quotes
                        if in_quotes:
                            quote_char = char
                        else:
                            quote_char = None
                        current += char
                    elif char == ',' and not in_quotes:
                        values.append(current.strip())
                        current = ""
                    else:
                        current += char
                
                if current:
                    values.append(current.strip())
                
                # Convert values to appropriate types
                processed_values = []
                for val in values:
                    if val.startswith(("'", '"')) and val.endswith(("'", '"')):
                        # String value
                        processed_values.append(val[1:-1])
                    elif val.lower() == 'null':
                        # NULL value
                        processed_values.append(None)
                    else:
                        # Numeric value
                        try:
                            if '.' in val:
                                processed_values.append(float(val))
                            else:
                                processed_values.append(int(val))
                        except ValueError:
                            # Fall back to string if not numeric
                            processed_values.append(val)
                
                # Create a row as a dictionary with column names
                if tables[table_name]["columns"]:
                    row = {}
                    for i, col in enumerate(tables[table_name]["columns"]):
                        if i < len(processed_values):
                            row[col["name"]] = processed_values[i]
                    tables[table_name]["data"].append(row)
                else:
                    # If no columns defined, just add the raw values
                    tables[table_name]["data"].append(processed_values)
        
        # Write to JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(tables, f, indent=2)
        
        logger.info(f"Successfully converted SQL dump to JSON: {input_path} -> {output_path}")
            
    except Exception as e:
        logger.error(f"Error converting SQL dump to JSON: {str(e)}")
        raise

def json_to_sql_dump(input_path: str, output_path: str) -> None:
    """
    Convert a JSON file to SQL dump format.
    
    Args:
        input_path: Path to the input JSON file
        output_path: Path to save the converted SQL dump file
    
    Raises:
        Exception: If conversion fails
    """
    try:
        # Read the JSON file
        with open(input_path, 'r', encoding='utf-8') as f:
            tables = json.load(f)
        
        # Generate SQL dump
        sql_content = []
        
        for table_name, table_info in tables.items():
            # Create table statement
            sql_content.append(f"-- Table structure for table `{table_name}`")
            sql_content.append("DROP TABLE IF EXISTS `" + table_name + "`;")
            
            create_table = f"CREATE TABLE `{table_name}` ("
            
            # Add columns
            columns = []
            for col in table_info.get("columns", []):
                col_name = col.get("name", "")
                col_type = col.get("type", "VARCHAR(255)")
                columns.append(f"`{col_name}` {col_type}")
            
            if columns:
                create_table += "\n  " + ",\n  ".join(columns)
                create_table += "\n);"
                sql_content.append(create_table)
            else:
                # Skip if no columns defined
                continue
            
            # Insert statements
            sql_content.append(f"\n-- Dumping data for table `{table_name}`")
            
            for row in table_info.get("data", []):
                if isinstance(row, dict):
                    # Convert row dictionary to values list
                    values = []
                    for col in table_info.get("columns", []):
                        col_name = col.get("name", "")
                        if col_name in row:
                            val = row[col_name]
                            if val is None:
                                values.append("NULL")
                            elif isinstance(val, (int, float)):
                                values.append(str(val))
                            else:
                                values.append(f"'{val}'")
                        else:
                            values.append("NULL")
                            
                    sql_content.append(f"INSERT INTO `{table_name}` VALUES ({', '.join(values)});")
                elif isinstance(row, list):
                    # Row is already a list of values
                    values = []
                    for val in row:
                        if val is None:
                            values.append("NULL")
                        elif isinstance(val, (int, float)):
                            values.append(str(val))
                        else:
                            values.append(f"'{val}'")
                    
                    sql_content.append(f"INSERT INTO `{table_name}` VALUES ({', '.join(values)});")
        
        # Write to SQL file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(sql_content))
        
        logger.info(f"Successfully converted JSON to SQL dump: {input_path} -> {output_path}")
            
    except Exception as e:
        logger.error(f"Error converting JSON to SQL dump: {str(e)}")
        raise

# Register the converters
register_converter('sql', 'json', sql_dump_to_json)
register_converter('json', 'sql', json_to_sql_dump)

# If running as standalone, log registration
if __name__ == "__main__":
    print("Registered custom converters: SQL <-> JSON")
