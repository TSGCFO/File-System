#!/usr/bin/env python3
"""
Universal File Format Converter

A comprehensive tool for converting files between various formats across multiple categories:
1. Document formats
2. Spreadsheet formats
3. Image formats
4. Archive formats
5. Database formats
6. Text and markup formats
7. Data exchange formats
8. Font formats
9. PDF, XPS, and similar formats

Usage:
    python format_converter.py input_file output_file [options]

Example:
    python format_converter.py document.docx document.pdf --verbose
"""

import argparse
import os
import sys
import logging
import importlib
import pkgutil
from typing import Dict, List, Tuple, Callable, Optional, Set, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global registry of converters
CONVERTERS: Dict[str, Dict[str, Callable]] = {}

# Global registry of format categories
FORMAT_CATEGORIES: Dict[str, List[str]] = {
    "document": ["doc", "docx", "odt", "rtf", "txt", "html", "md", "pdf"],
    "spreadsheet": ["xls", "xlsx", "ods", "csv", "tsv"],
    "image": ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "tif", "webp", "svg"],
    "archive": ["zip", "tar", "gz", "bz2", "7z", "rar"],
    "database": ["sql", "sqlite", "db", "json", "xml", "csv"],
    "text_markup": ["txt", "html", "xml", "json", "yaml", "yml", "md", "rst"],
    "data_exchange": ["json", "xml", "yaml", "yml", "csv", "toml", "pb"],
    "font": ["ttf", "otf", "woff", "woff2", "eot"],
    "pdf_xps": ["pdf", "xps", "djvu", "epub"]
}

def register_converter(source_format: str, target_format: str, converter_func: Callable) -> None:
    """
    Register a converter function for a specific source and target format.

    Args:
        source_format: The format to convert from (file extension without the dot)
        target_format: The format to convert to (file extension without the dot)
        converter_func: Function that performs the conversion, with signature:
                        func(input_path: str, output_path: str) -> None
    """
    global CONVERTERS
    if source_format not in CONVERTERS:
        CONVERTERS[source_format] = {}
    CONVERTERS[source_format][target_format] = converter_func
    logger.debug(f"Registered converter: {source_format} -> {target_format}")

def get_converter(source_format: str, target_format: str) -> Optional[Callable]:
    """
    Get a converter function for the given source and target formats.

    Args:
        source_format: The format to convert from (file extension without the dot)
        target_format: The format to convert to (file extension without the dot)

    Returns:
        The converter function or None if no converter is registered
    """
    global CONVERTERS
    if source_format in CONVERTERS and target_format in CONVERTERS[source_format]:
        return CONVERTERS[source_format][target_format]
    return None

def get_format_category(format_ext: str) -> Optional[str]:
    """
    Get the category of a file format.

    Args:
        format_ext: The file format extension without the dot

    Returns:
        The category name or None if not found
    """
    global FORMAT_CATEGORIES
    for category, formats in FORMAT_CATEGORIES.items():
        if format_ext in formats:
            return category
    return None

def list_supported_formats() -> Dict[str, Set[str]]:
    """
    List all supported formats and their possible conversions.

    Returns:
        A dictionary mapping source formats to sets of possible target formats
    """
    global CONVERTERS
    return {
        source: set(targets.keys())
        for source, targets in CONVERTERS.items()
    }

def list_supported_formats_by_category() -> Dict[str, Dict[str, Set[str]]]:
    """
    List all supported formats and their possible conversions, organized by category.

    Returns:
        A dictionary mapping categories to dictionaries of source formats and their target formats
    """
    global CONVERTERS, FORMAT_CATEGORIES
    result = {}
    
    for category, formats in FORMAT_CATEGORIES.items():
        category_converters = {}
        for source_format in formats:
            if source_format in CONVERTERS:
                # Find all target formats in this category
                category_targets = {
                    target for target in CONVERTERS[source_format]
                    if target in formats
                }
                if category_targets:
                    category_converters[source_format] = category_targets
        
        if category_converters:
            result[category] = category_converters
    
    return result

def convert_file(input_path: str, output_path: str, force: bool = False) -> bool:
    """
    Convert a file from one format to another based on file extensions.

    Args:
        input_path: Path to the input file
        output_path: Path to the output file
        force: Whether to overwrite existing output file

    Returns:
        True if conversion was successful, False otherwise
    """
    # Check if input file exists
    if not os.path.isfile(input_path):
        logger.error(f"Input file does not exist: {input_path}")
        return False

    # Check if output file already exists
    if os.path.exists(output_path) and not force:
        logger.error(f"Output file already exists: {output_path}. Use --force to overwrite.")
        return False

    # Determine source and target formats from file extensions
    source_ext = os.path.splitext(input_path)[1].lower().lstrip('.')
    target_ext = os.path.splitext(output_path)[1].lower().lstrip('.')

    if not source_ext or not target_ext:
        logger.error("Could not determine file formats from file extensions.")
        return False

    # Get converter function
    converter = get_converter(source_ext, target_ext)
    if not converter:
        # Check if there's a converter for alternative extensions (e.g., jpg/jpeg)
        if source_ext == 'jpg' and get_converter('jpeg', target_ext):
            converter = get_converter('jpeg', target_ext)
        elif source_ext == 'jpeg' and get_converter('jpg', target_ext):
            converter = get_converter('jpg', target_ext)
        elif target_ext == 'jpg' and get_converter(source_ext, 'jpeg'):
            converter = get_converter(source_ext, 'jpeg')
        elif target_ext == 'jpeg' and get_converter(source_ext, 'jpg'):
            converter = get_converter(source_ext, 'jpg')
        else:
            logger.error(f"No converter available for {source_ext} to {target_ext}")
            return False

    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Perform the conversion
        converter(input_path, output_path)
        logger.info(f"Successfully converted {input_path} to {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error during conversion: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        return False

def check_dependencies():
    """
    Check if required dependencies are installed.
    Print warnings for missing packages.
    """
    dependencies = {
        "PIL": "Pillow",  # For image conversions
        "docx": "python-docx",  # For Word document handling
        "openpyxl": "openpyxl",  # For Excel spreadsheet handling
        "PyPDF2": "PyPDF2",  # For PDF handling
        "yaml": "PyYAML",  # For YAML handling
        "lxml": "lxml",  # For XML handling
        "markdown": "Markdown",  # For Markdown conversions
        "chardet": "chardet",  # For character encoding detection
    }
    
    missing = []
    for module, package in dependencies.items():
        try:
            importlib.import_module(module)
        except ImportError:
            missing.append(package)
    
    if missing:
        logger.warning("The following packages are required but not installed:")
        for package in missing:
            logger.warning(f"  - {package}")
        logger.warning("Install them using: pip install " + " ".join(missing))

def discover_and_load_converters():
    """
    Discover and load all available converter modules.
    
    This function looks for Python modules in the 'converters' package
    and imports them, which triggers registration of converters.
    """
    try:
        # Import the converters package
        import converters
        
        # Find all modules in the converters package
        for _, name, is_pkg in pkgutil.iter_modules(converters.__path__, converters.__name__ + '.'):
            if not is_pkg:
                try:
                    importlib.import_module(name)
                    logger.debug(f"Loaded converter module: {name}")
                except ImportError as e:
                    logger.warning(f"Could not load converter module {name}: {str(e)}")
    except ImportError:
        logger.warning("Converters package not found. No converters will be loaded.")
        # Create a basic structure for converters
        os.makedirs('converters', exist_ok=True)
        with open(os.path.join('converters', '__init__.py'), 'w') as f:
            f.write('"""Converter modules package."""\n')
        logger.info("Created basic converters package structure.")

def main():
    """Main entry point for the script."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Convert files between different formats.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Format Categories:
  1. Document formats: doc, docx, odt, rtf, txt, html, md, pdf
  2. Spreadsheet formats: xls, xlsx, ods, csv, tsv
  3. Image formats: jpg, jpeg, png, gif, bmp, tiff, tif, webp, svg
  4. Archive formats: zip, tar, gz, bz2, 7z, rar
  5. Database formats: sql, sqlite, db, json, xml, csv
  6. Text and markup formats: txt, html, xml, json, yaml, yml, md, rst
  7. Data exchange formats: json, xml, yaml, yml, csv, toml, pb
  8. Font formats: ttf, otf, woff, woff2, eot
  9. PDF, XPS, and similar formats: pdf, xps, djvu, epub
"""
    )
    parser.add_argument("input", nargs="?", help="Input file path")
    parser.add_argument("output", nargs="?", help="Output file path")
    parser.add_argument("--force", "-f", action="store_true", help="Force overwrite of existing output file")
    parser.add_argument("--list-formats", "-l", action="store_true", help="List supported formats and exit")
    parser.add_argument("--list-categories", "-c", action="store_true", help="List format categories and exit")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--check-deps", "-d", action="store_true", help="Check dependencies and exit")
    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        # Also set root logger level
        logging.getLogger().setLevel(logging.DEBUG)

    # Check dependencies if requested
    if args.check_deps:
        check_dependencies()
        return 0

    # Discover and load converter modules
    discover_and_load_converters()

    # Load built-in converters
    try:
        from builtin_converters import register_builtin_converters
        register_builtin_converters()
    except ImportError:
        logger.debug("No built-in converters found.")

    # List format categories if requested
    if args.list_categories:
        print("Supported format categories:")
        for category, formats in FORMAT_CATEGORIES.items():
            print(f"  {category.replace('_', ' ').title()}: {', '.join(formats)}")
        return 0

    # List supported formats if requested
    if args.list_formats:
        formats_by_category = list_supported_formats_by_category()
        if not formats_by_category:
            print("No converters are currently registered.")
            return 0
            
        print("Supported conversions by category:")
        for category, formats in formats_by_category.items():
            print(f"\n{category.replace('_', ' ').title()}:")
            for source, targets in formats.items():
                print(f"  {source} -> {', '.join(sorted(targets))}")
        return 0

    # Check if input and output files were provided
    if not args.input or not args.output:
        parser.print_help()
        return 1

    # Perform conversion
    success = convert_file(args.input, args.output, args.force)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
