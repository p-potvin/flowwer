#!/usr/bin/env python3
"""Test the workflow with an actual safetensors model"""

import json
import sys
from pathlib import Path

# Add the scripts directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from ai_model_execution_workflow_simple import run_workflow

def main():
    # Test input for safetensors model (using one of the actual models)
    test_input = {
        "model_name": "babesIllustriousBy_v55DMD2",  # This should match a .safetensors file in checkpoints
        "input_data": {
            "prompt": "A beautiful landscape with mountains and rivers",
            "negative_prompt": "ugly, deformed, blurry",
            "steps": 20,
            "cfg_scale": 7.5
        },
        "parameters": {
            "execution_timeout": 120,
            "batch_size": 1
        },
        "framework": "cuda"
    }
    
    print("Running AI Model Execution Workflow for safetensors model...")
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
                print("\nGenerated script content (first 50 lines):")
                print("=" * 60)
                lines = script_content.split('\n')[:50]
                print('\n'.join(lines))
                print("=" * 60)
                if len(lines) == 50:
                    print("... (script continues)")
                
    except Exception as e:
        print(f"Workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())