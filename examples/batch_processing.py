#!/usr/bin/env python3
"""
Batch processing example for FileConverter.

This script demonstrates how to convert multiple files using the FileConverter API.
"""

import argparse
import glob
import os
import sys
from pathlib import Path
from typing import List

from tqdm import tqdm

from fileconverter import ConversionEngine
from fileconverter.utils.error_handling import ConversionError
from fileconverter.utils.file_utils import get_file_extension


def main():
    """Run the batch processing example."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Convert multiple files in batch mode.")
    
    parser.add_argument(
        "input_pattern", 
        help="Input file pattern (e.g., '*.csv', 'data/*.json')"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        required=True,
        help="Directory where output files will be saved"
    )
    
    parser.add_argument(
        "--output-format", "-f",
        required=True,
        help="Output format extension (e.g., 'json', 'xlsx')"
    )
    
    parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        help="Process directories recursively"
    )
    
    parser.add_argument(
        "--param", "-p",
        action="append",
        dest="parameters",
        help="Conversion parameters in the format name=value",
        default=[]
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
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
    
    # Find input files
    try:
        if args.recursive:
            # For recursive search, we need to handle the pattern differently
            base_dir = os.path.dirname(args.input_pattern)
            if not base_dir:
                base_dir = "."
            
            file_pattern = os.path.basename(args.input_pattern)
            input_files = []
            
            for root, _, files in os.walk(base_dir):
                for file in files:
                    if glob.fnmatch.fnmatch(file, file_pattern):
                        input_files.append(os.path.join(root, file))
        else:
            input_files = glob.glob(args.input_pattern)
        
        if not input_files:
            print(f"No files found matching pattern: {args.input_pattern}")
            sys.exit(1)
        
        print(f"Found {len(input_files)} files to process")
    
    except Exception as e:
        print(f"Error finding input files: {str(e)}", file=sys.stderr)
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    output_dir = Path(args.output_dir)
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Error creating output directory: {str(e)}", file=sys.stderr)
        sys.exit(1)
    
    # Create conversion engine
    engine = ConversionEngine()
    
    # Process each file
    successful = 0
    failed = 0
    errors = []
    
    with tqdm(total=len(input_files), disable=not args.verbose) as progress_bar:
        for input_file in input_files:
            progress_bar.set_description(f"Processing {os.path.basename(input_file)}")
            
            try:
                # Determine output file path
                input_path = Path(input_file)
                output_file = output_dir / f"{input_path.stem}.{args.output_format}"
                
                # Convert the file
                engine.convert_file(
                    input_path=input_file,
                    output_path=output_file,
                    parameters=parameters
                )
                
                successful += 1
            
            except ConversionError as e:
                failed += 1
                errors.append((input_file, str(e)))
                if args.verbose:
                    print(f"\nError converting {input_file}: {str(e)}", file=sys.stderr)
            
            except Exception as e:
                failed += 1
                errors.append((input_file, str(e)))
                if args.verbose:
                    print(f"\nUnexpected error converting {input_file}: {str(e)}", file=sys.stderr)
            
            progress_bar.update(1)
    
    # Print summary
    print(f"\nBatch processing completed: {successful} successful, {failed} failed")
    
    if errors and args.verbose:
        print("\nErrors:")
        for file_path, error_msg in errors:
            print(f"  {file_path}: {error_msg}")
    
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
