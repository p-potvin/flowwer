#!/usr/bin/env python3
"""Test the workflow with an image model"""

import json
import sys
from pathlib import Path

# Add the scripts directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from ai_model_execution_workflow_simple import run_workflow

def main():
    # Test input for image model
    test_input = {
        "model_name": "image_processor.jpg",
        "input_data": {
            "image_path": "example.jpg",
            "processing_params": {
                "resize": [256, 256],
                "normalize": True
            }
        },
        "parameters": {
            "execution_timeout": 60
        },
        "framework": "pytorch"
    }
    
    print("Running AI Model Execution Workflow for image model...")
    print(f"Input: {json.dumps(test_input, indent=2)}")
    
    try:
        result = run_workflow(test_input)
        print("\nWorkflow completed!")
        print(f"Result: {json.dumps(result, indent=2)}")
        
        # Check if script was generated
        if 'script_path' in result and Path(result['script_path']).exists():
            print(f"\nGenerated script available at: {result['script_path']}")
            
            # Show the generated script content
            with open(result['script_path'], 'r') as f:
                script_content = f.read()
                print("\nGenerated script content:")
                print("=" * 50)
                print(script_content)
                print("=" * 50)
                
    except Exception as e:
        print(f"Workflow failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())