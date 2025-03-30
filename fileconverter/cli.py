"""
Command Line Interface for FileConverter.

This module provides the CLI functionality for the FileConverter package.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple, Union, Dict, Any

import click
from tqdm import tqdm

from fileconverter.core.engine import ConversionEngine
from fileconverter.core.registry import ConverterRegistry
from fileconverter.utils.error_handling import ConversionError, handle_error
from fileconverter.utils.file_utils import get_file_format, list_files
from fileconverter.utils.logging_utils import get_logger

logger = get_logger(__name__)


@click.group()
@click.version_option()
@click.option(
    "--verbose", "-v", 
    count=True, 
    help="Increase verbosity (can be used multiple times)"
)
@click.option(
    "--config", "-c", 
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help="Path to configuration file"
)
@click.pass_context
def cli(ctx: click.Context, verbose: int, config: Optional[str]) -> None:
    """FileConverter - Convert files between different formats.
    
    This utility provides comprehensive file conversion capabilities with
    support for documents, spreadsheets, images, data exchange formats,
    and archives.
    """
    # Initialize context object
    ctx.ensure_object(dict)
    ctx.obj["VERBOSE"] = verbose
    ctx.obj["CONFIG"] = config
    
    # Configure logging based on verbosity
    if verbose >= 2:
        import logging
        logging.getLogger("fileconverter").setLevel(logging.DEBUG)
    elif verbose == 1:
        import logging
        logging.getLogger("fileconverter").setLevel(logging.INFO)


@cli.command("convert")
@click.argument(
    "input_file", 
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True)
)
@click.argument(
    "output_file", 
    type=click.Path(file_okay=True, dir_okay=False, writable=True)
)
@click.option(
    "--params", "-p", 
    multiple=True, 
    help="Conversion parameters in the format name=value"
)
@click.pass_context
def convert_file(
    ctx: click.Context, 
    input_file: str, 
    output_file: str, 
    params: List[str]
) -> None:
    """Convert a single file from one format to another.
    
    INPUT_FILE is the path to the file to convert.
    OUTPUT_FILE is the path where the converted file will be saved.
    """
    verbose = ctx.obj.get("VERBOSE", 0)
    config_path = ctx.obj.get("CONFIG")
    
    # Parse parameters
    conversion_params = {}
    for param in params:
        try:
            name, value = param.split("=", 1)
            conversion_params[name.strip()] = value.strip()
        except ValueError:
            click.echo(f"Error: Invalid parameter format: {param}", err=True)
            click.echo("Parameters should be in the format: name=value", err=True)
            sys.exit(1)
    
    # Create engine and perform conversion
    engine = ConversionEngine(config_path=config_path)
    
    try:
        if verbose:
            click.echo(f"Converting {input_file} to {output_file}...")
        
        result = engine.convert_file(
            input_path=input_file,
            output_path=output_file,
            parameters=conversion_params
        )
        
        if verbose:
            click.echo(f"Conversion successful: {result}")
        else:
            click.echo(f"Conversion successful")
    
    except ConversionError as e:
        handle_error(e, logger)
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error during conversion")
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command("batch")
@click.argument(
    "input_files", 
    nargs=-1, 
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True)
)
@click.option(
    "--output-dir", "-o", 
    required=True,
    type=click.Path(file_okay=False, dir_okay=True, writable=True),
    help="Directory to save converted files"
)
@click.option(
    "--output-format", "-f", 
    required=True,
    help="Target format for conversion (e.g., pdf, json, xlsx)"
)
@click.option(
    "--params", "-p", 
    multiple=True, 
    help="Conversion parameters in the format name=value"
)
@click.option(
    "--recursive/--no-recursive", 
    default=False, 
    help="Recursively process directories"
)
@click.pass_context
def batch_convert(
    ctx: click.Context, 
    input_files: List[str], 
    output_dir: str, 
    output_format: str,
    params: List[str],
    recursive: bool
) -> None:
    """Convert multiple files to the specified format.
    
    INPUT_FILES are paths to the files to convert.
    Multiple files can be specified using wildcards.
    """
    verbose = ctx.obj.get("VERBOSE", 0)
    config_path = ctx.obj.get("CONFIG")
    
    # Ensure output directory exists
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Parse parameters
    conversion_params = {}
    for param in params:
        try:
            name, value = param.split("=", 1)
            conversion_params[name.strip()] = value.strip()
        except ValueError:
            click.echo(f"Error: Invalid parameter format: {param}", err=True)
            click.echo("Parameters should be in the format: name=value", err=True)
            sys.exit(1)
    
    # Expand wildcards if necessary
    all_files = []
    for pattern in input_files:
        if "*" in pattern or "?" in pattern:
            matched_files = list_files(pattern, recursive=recursive)
            all_files.extend(matched_files)
        else:
            all_files.append(pattern)
    
    if not all_files:
        click.echo("No files found matching the specified patterns.", err=True)
        sys.exit(1)
    
    # Create engine
    engine = ConversionEngine(config_path=config_path)
    
    # Process each file
    successful = 0
    failed = 0
    
    with tqdm(total=len(all_files), disable=not verbose) as progress_bar:
        for input_file in all_files:
            input_path = Path(input_file)
            output_filename = f"{input_path.stem}.{output_format}"
            output_file = output_path / output_filename
            
            progress_bar.set_description(f"Converting {input_path.name}")
            
            try:
                engine.convert_file(
                    input_path=str(input_path),
                    output_path=str(output_file),
                    parameters=conversion_params
                )
                successful += 1
            except Exception as e:
                logger.error(f"Failed to convert {input_file}: {str(e)}")
                failed += 1
            
            progress_bar.update(1)
    
    # Report results
    click.echo(f"Batch conversion completed: {successful} successful, {failed} failed")
    if failed > 0:
        click.echo("Check the log file for details on failed conversions.")
        sys.exit(1)


@cli.command("list-formats")
@click.option(
    "--category", "-c", 
    help="Filter formats by category (document, spreadsheet, image, etc.)"
)
@click.pass_context
def list_formats(ctx: click.Context, category: Optional[str]) -> None:
    """List all supported file formats for conversion."""
    registry = ConverterRegistry()
    formats = registry.get_supported_formats(category)
    
    if not formats:
        if category:
            click.echo(f"No formats found for category: {category}")
        else:
            click.echo("No supported formats found.")
        return
    
    click.echo("Supported File Formats:")
    click.echo("=" * 50)
    
    for cat, format_list in formats.items():
        if category and cat.lower() != category.lower():
            continue
            
        click.echo(f"\n{cat}:")
        click.echo("-" * len(cat))
        
        for fmt in sorted(format_list):
            extensions = registry.get_format_extensions(fmt)
            ext_str = ", ".join(f".{ext}" for ext in extensions)
            click.echo(f"  {fmt:<15} [{ext_str}]")
    
    click.echo("\nUse 'fileconverter convert --help' for conversion options.")


def main() -> None:
    """Main entry point for the CLI."""
    try:
        cli(obj={})
    except Exception as e:
        logger.exception("Unexpected error in CLI")
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
