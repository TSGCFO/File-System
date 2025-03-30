#!/usr/bin/env python3
"""
Basic conversion example for FileConverter.

This script demonstrates how to use the FileConverter API to convert files
between different formats.
"""

import argparse
import sys
from pathlib import Path

from fileconverter import ConversionEngine
from fileconverter.utils.error_handling import ConversionError


def main():
    """Run the basic conversion example."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Convert a file from one format to another.")
    
    parser.add_argument(
        "input_file", 
        help="Path to the input file"
    )
    
    parser.add_argument(
        "output_file", 
        help="Path where the output file will be saved"
    )
    
    parser.add_argument(
        "--param", "-p",
        action="append",
        dest="parameters",
        help="Conversion parameters in the format name=value",
        default=[]
    )
    
    args = parser.parse_args()
    
    # Parse parameters
    parameters = {}
    for param in args.parameters:
        try:
            name, value = param.split("=", 1)
            parameters[name.strip()] = value.strip()
        except ValueError:
            print(f"Error: Invalid parameter format: {param}")
            print("Parameters should be in the format: name=value")
            sys.exit(1)
    
    # Create conversion engine
    engine = ConversionEngine()
    
    try:
        # Convert the file
        print(f"Converting {args.input_file} to {args.output_file}...")
        
        result = engine.convert_file(
            input_path=args.input_file,
            output_path=args.output_file,
            parameters=parameters
        )
        
        print("Conversion successful!")
        print(f"Input format: {result['input_format']}")
        print(f"Output format: {result['output_format']}")
        
    except ConversionError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
