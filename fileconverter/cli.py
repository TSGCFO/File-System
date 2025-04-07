#!/usr/bin/env python3
"""
Command-line interface for FileConverter.

This module provides the command-line interface for the FileConverter application,
allowing users to convert files and manage dependencies from the command line.
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from fileconverter.core.engine import ConversionEngine
from fileconverter.version import __version__

logger = logging.getLogger(__name__)

def add_dependency_commands(subparsers):
    """Add dependency management commands to the CLI."""
    # Add dependency check command
    dep_parser = subparsers.add_parser(
        "dependencies",
        help="Manage dependencies"
    )
    dep_subparsers = dep_parser.add_subparsers(dest="dep_command")
    
    # Check subcommand
    check_parser = dep_subparsers.add_parser(
        "check",
        help="Check for missing dependencies"
    )
    check_parser.add_argument(
        "--format",
        action="append",
        dest="formats",
        help="Specific format categories to check"
    )
    
    # Install subcommand
    install_parser = dep_subparsers.add_parser(
        "install",
        help="Install missing dependencies"
    )
    install_parser.add_argument(
        "--offline",
        metavar="PATH",
        help="Use offline package repository"
    )
    install_parser.add_argument(
        "--format",
        action="append",
        dest="formats",
        help="Specific format categories to install"
    )
    install_parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Don't prompt for confirmation"
    )
    
    # Bundle subcommand
    bundle_parser = dep_subparsers.add_parser(
        "bundle",
        help="Create an offline dependency bundle"
    )
    bundle_parser.add_argument(
        "output_dir",
        help="Directory where the bundle will be created"
    )
    bundle_parser.add_argument(
        "--format",
        action="append",
        dest="formats",
        help="Specific format categories to bundle"
    )

def create_parser():
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(description="FileConverter - Convert files between various formats")
    
    # Add version argument
    parser.add_argument("--version", action="version", version=f"FileConverter {__version__}")
    
    # Add verbose argument
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    # Add dependency check argument
    parser.add_argument("--skip-dependency-check", action="store_true", 
                        help="Skip dependency checking (for advanced users)")
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Add convert command
    convert_parser = subparsers.add_parser("convert", help="Convert a file from one format to another")
    convert_parser.add_argument("input", help="Input file path")
    convert_parser.add_argument("output", help="Output file path")
    convert_parser.add_argument("--param", action="append", dest="params", metavar="KEY=VALUE", 
                               help="Conversion parameters (can be specified multiple times)")
    
    # Add list-formats command
    list_formats_parser = subparsers.add_parser("list-formats", help="List supported formats")
    list_formats_parser.add_argument("--input", action="store_true", help="Show only input formats")
    list_formats_parser.add_argument("--output", action="store_true", help="Show only output formats")
    list_formats_parser.add_argument("--verbose", action="store_true", help="Show detailed format information")
    
    # Add batch command
    batch_parser = subparsers.add_parser("batch", help="Convert multiple files in batch")
    batch_parser.add_argument("--input-dir", required=True, help="Input directory")
    batch_parser.add_argument("--output-dir", required=True, help="Output directory")
    batch_parser.add_argument("--pattern", default="*.*", help="File pattern to match (e.g., '*.docx')")
    batch_parser.add_argument("--output-format", required=True, help="Output format (e.g., 'pdf')")
    batch_parser.add_argument("--recursive", action="store_true", help="Recursively process subdirectories")
    batch_parser.add_argument("--param", action="append", dest="params", metavar="KEY=VALUE",
                             help="Conversion parameters (can be specified multiple times)")
    
    # Add dependency management commands
    add_dependency_commands(subparsers)
    
    return parser

def parse_params(param_strings: Optional[List[str]]) -> Dict[str, Any]:
    """Parse key=value parameter strings into a dictionary."""
    params = {}
    if param_strings:
        for param in param_strings:
            if "=" in param:
                key, value = param.split("=", 1)
                # Try to convert to appropriate types
                if value.lower() == "true":
                    value = True
                elif value.lower() == "false":
                    value = False
                elif value.isdigit():
                    value = int(value)
                elif value.replace(".", "", 1).isdigit() and value.count(".") == 1:
                    value = float(value)
                params[key] = value
            else:
                logger.warning(f"Invalid parameter format: {param} (should be KEY=VALUE)")
    return params

def handle_convert_command(args):
    """Handle the convert command."""
    engine = ConversionEngine()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        print(f"Error: Input file not found: {input_path}")
        return 1
    
    # Create output directory if it doesn't exist
    output_dir = output_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Parse parameters
    params = parse_params(args.params)
    
    try:
        print(f"Converting {input_path} to {output_path}...")
        result = engine.convert_file(input_path, output_path, params)
        print(f"Conversion complete. File saved to {output_path}")
        return 0
    except Exception as e:
        logger.error(f"Conversion failed: {e}", exc_info=True)
        print(f"Error: Conversion failed: {e}")
        return 1

def handle_list_formats_command(args):
    """Handle the list-formats command."""
    engine = ConversionEngine()
    
    if args.verbose:
        # Show detailed format information
        formats = engine.get_supported_formats(details=True)
        
        print("Supported Formats:")
        print("=================")
        
        for format_name, format_info in formats.items():
            print(f"\n{format_name.upper()}")
            print("-" * len(format_name))
            
            if "extensions" in format_info:
                ext_list = ", ".join(format_info["extensions"])
                print(f"Extensions: {ext_list}")
            
            if "input" in format_info and format_info["input"]:
                print("Can be used as input format: Yes")
            else:
                print("Can be used as input format: No")
                
            if "output" in format_info and format_info["output"]:
                print("Can be used as output format: Yes")
            else:
                print("Can be used as output format: No")
            
            if "description" in format_info:
                print(f"Description: {format_info['description']}")
            
            if "params" in format_info:
                print("\nSupported Parameters:")
                for param_name, param_info in format_info["params"].items():
                    param_type = param_info.get("type", "string")
                    param_desc = param_info.get("description", "")
                    param_default = param_info.get("default", "None")
                    print(f"  - {param_name} ({param_type}): {param_desc}")
                    print(f"    Default: {param_default}")
    else:
        # Show simple format list
        input_formats, output_formats = engine.get_supported_formats_simple()
        
        if not args.output:
            print("Supported Input Formats:")
            print("=======================")
            for fmt in sorted(input_formats):
                print(f"- {fmt}")
            print()
        
        if not args.input:
            print("Supported Output Formats:")
            print("========================")
            for fmt in sorted(output_formats):
                print(f"- {fmt}")
    
    return 0

def handle_batch_command(args):
    """Handle the batch command."""
    engine = ConversionEngine()
    
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    
    if not input_dir.exists() or not input_dir.is_dir():
        logger.error(f"Input directory not found: {input_dir}")
        print(f"Error: Input directory not found: {input_dir}")
        return 1
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Parse parameters
    params = parse_params(args.params)
    
    # Get files to convert
    pattern = args.pattern
    if args.recursive:
        files = list(input_dir.glob(f"**/{pattern}"))
    else:
        files = list(input_dir.glob(pattern))
    
    if not files:
        logger.warning(f"No files matching pattern '{pattern}' found in {input_dir}")
        print(f"Warning: No files matching pattern '{pattern}' found in {input_dir}")
        return 0
    
    print(f"Found {len(files)} files to convert")
    
    output_format = args.output_format
    if not output_format.startswith("."):
        output_format = f".{output_format}"
    
    success_count = 0
    error_count = 0
    
    for input_file in files:
        # Calculate relative path to preserve directory structure
        rel_path = input_file.relative_to(input_dir)
        output_file = output_dir / rel_path.with_suffix(output_format)
        
        # Create subdirectories if needed
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"Converting {input_file} to {output_file}...")
        try:
            engine.convert_file(input_file, output_file, params)
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to convert {input_file}: {e}")
            print(f"Error: Failed to convert {input_file}: {e}")
            error_count += 1
    
    print(f"\nBatch conversion complete. {success_count} files converted successfully, {error_count} errors.")
    return 0 if error_count == 0 else 1

def handle_dependency_commands(args):
    """Handle dependency management commands."""
    try:
        from fileconverter.dependency_manager import (
            detect_missing_dependencies, 
            auto_install_dependencies,
            create_dependency_bundle,
            generate_report
        )
        
        if args.dep_command == "check":
            missing_deps = detect_missing_dependencies(args.formats)
            if not missing_deps["python"] and not missing_deps["external"]:
                print("All dependencies are installed and ready to use.")
                return 0
            
            # Create empty results structure for report
            empty_results = {"success": [], "failure": [], "manual_action_required": []}
            report = generate_report(missing_deps, empty_results)
            print(report)
            
        elif args.dep_command == "install":
            missing_deps = detect_missing_dependencies(args.formats)
            if not missing_deps["python"] and not missing_deps["external"]:
                print("All dependencies are installed and ready to use.")
                return 0
                
            install_results = auto_install_dependencies(
                missing_deps,
                offline_path=args.offline,
                interactive=not getattr(args, 'non_interactive', False)
            )
            
            report = generate_report(missing_deps, install_results)
            print(report)
            
        elif args.dep_command == "bundle":
            bundle_path = create_dependency_bundle(args.output_dir, args.formats)
            if bundle_path:
                print(f"Dependency bundle created successfully at {bundle_path}")
                return 0
            else:
                print("Failed to create dependency bundle")
                return 1
                
        return 0
    except ImportError:
        logger.error("Dependency manager module not found")
        print("Error: Dependency manager module not found. Make sure FileConverter is properly installed.")
        return 1

def main():
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")
    
    # Check if a command was specified
    if not hasattr(args, 'command') or args.command is None:
        parser.print_help()
        return 0
    
    # Check dependencies unless skipped
    if not getattr(args, 'skip_dependency_check', False):
        try:
            from fileconverter.main import check_dependencies
            missing_critical = check_dependencies(silent=False)
            if missing_critical and args.command != "dependencies":
                return 1
        except ImportError:
            # If the dependency check function can't be imported,
            # we're probably running from source before installation
            logger.warning("Dependency check function not available")
    
    # Handle commands
    if args.command == "convert":
        return handle_convert_command(args)
    elif args.command == "list-formats":
        return handle_list_formats_command(args)
    elif args.command == "batch":
        return handle_batch_command(args)
    elif args.command == "dependencies" and hasattr(args, 'dep_command'):
        return handle_dependency_commands(args)
    else:
        parser.print_help()
        return 0

if __name__ == "__main__":
    sys.exit(main())
