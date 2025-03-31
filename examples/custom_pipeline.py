#!/usr/bin/env python3
"""
Custom conversion pipeline example for FileConverter.

This script demonstrates how to create a custom conversion pipeline
that processes files through multiple stages using the FileConverter API.
"""

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Union

from fileconverter import ConversionEngine, ConverterRegistry
from fileconverter.utils.error_handling import ConversionError


class ConversionPipeline:
    """A pipeline for multi-stage file conversions."""
    
    def __init__(self, config_file: Optional[str] = None) -> None:
        """Initialize the conversion pipeline.
        
        Args:
            config_file: Optional path to a configuration file.
        """
        self.engine = ConversionEngine(config_path=config_file)
        self.registry = ConverterRegistry()
        self.temp_dir = None
    
    def run_pipeline(
        self,
        input_file: Union[str, Path],
        output_file: Union[str, Path],
        stages: List[Dict],
        cleanup: bool = True
    ) -> Dict:
        """Run a multi-stage conversion pipeline.
        
        Args:
            input_file: Path to the input file.
            output_file: Path where the final output file will be saved.
            stages: List of conversion stages, each a dictionary with:
                   - format: Output format for this stage
                   - parameters: Optional parameters for this stage
            cleanup: Whether to clean up temporary files after conversion.
        
        Returns:
            Dictionary with information about the conversion.
        
        Raises:
            ConversionError: If the conversion fails.
        """
        input_path = Path(input_file)
        output_path = Path(output_file)
        
        # Create temporary directory for intermediate files
        self.temp_dir = tempfile.mkdtemp(prefix="fileconverter_pipeline_")
        
        try:
            current_file = input_path
            stage_results = []
            
            # Process each stage
            for i, stage in enumerate(stages):
                # Determine if this is the final stage
                is_final_stage = (i == len(stages) - 1)
                
                # Get output format for this stage
                output_format = stage.get("format")
                if not output_format:
                    raise ConversionError(f"Stage {i+1} missing 'format' attribute")
                
                # Set output path for this stage
                if is_final_stage:
                    # Final stage outputs to the specified output file
                    stage_output = output_path
                else:
                    # Intermediate stage outputs to a temporary file
                    stage_output = Path(self.temp_dir) / f"stage_{i+1}.{output_format}"
                
                # Get parameters for this stage
                parameters = stage.get("parameters", {})
                
                # Perform conversion for this stage
                print(f"Stage {i+1}: Converting to {output_format}...")
                
                result = self.engine.convert_file(
                    input_path=current_file,
                    output_path=stage_output,
                    parameters=parameters
                )
                
                stage_results.append({
                    "stage": i + 1,
                    "input_format": result["input_format"],
                    "output_format": result["output_format"],
                    "parameters": parameters
                })
                
                # Use the output of this stage as input for the next stage
                current_file = stage_output
            
            # Return information about the pipeline execution
            return {
                "input_file": str(input_path),
                "output_file": str(output_path),
                "stages": stage_results,
                "success": True
            }
        
        finally:
            # Clean up temporary files if requested
            if cleanup and self.temp_dir:
                import shutil
                try:
                    shutil.rmtree(self.temp_dir)
                except Exception as e:
                    print(f"Warning: Failed to clean up temporary files: {str(e)}")


def main():
    """Run the custom pipeline example."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Convert a file through a multi-stage pipeline."
    )
    
    parser.add_argument(
        "input_file", 
        help="Path to the input file"
    )
    
    parser.add_argument(
        "output_file", 
        help="Path where the output file will be saved"
    )
    
    parser.add_argument(
        "--pipeline", "-p",
        required=True,
        help="JSON file describing the conversion pipeline"
    )
    
    parser.add_argument(
        "--keep-temp", "-k",
        action="store_true",
        help="Keep temporary files after conversion"
    )
    
    args = parser.parse_args()
    
    # Load pipeline configuration
    try:
        with open(args.pipeline, "r") as f:
            pipeline_config = json.load(f)
        
        # Validate pipeline configuration
        if not isinstance(pipeline_config, dict) or "stages" not in pipeline_config:
            raise ValueError("Pipeline configuration must contain a 'stages' array")
        
        stages = pipeline_config["stages"]
        if not isinstance(stages, list) or not stages:
            raise ValueError("Pipeline 'stages' must be a non-empty array")
    
    except Exception as e:
        print(f"Error loading pipeline configuration: {str(e)}", file=sys.stderr)
        sys.exit(1)
    
    # Create and run the pipeline
    pipeline = ConversionPipeline()
    
    try:
        print(f"Converting {args.input_file} to {args.output_file}...")
        
        result = pipeline.run_pipeline(
            input_file=args.input_file,
            output_file=args.output_file,
            stages=stages,
            cleanup=not args.keep_temp
        )
        
        print("\nConversion pipeline completed successfully!")
        print(f"Input file: {result['input_file']}")
        print(f"Output file: {result['output_file']}")
        print(f"Stages: {len(result['stages'])}")
        
        for stage in result["stages"]:
            print(f"  Stage {stage['stage']}: "
                  f"{stage['input_format']} → {stage['output_format']}")
    
    except ConversionError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()