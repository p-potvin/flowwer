#!/usr/bin/env python3
"""List available models to help users understand what's available"""

import sys
from pathlib import Path

# Add the scripts directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from ai_model_execution_workflow_simple import MODELS_DIR, SUPPORTED_MODEL_FORMATS, MODEL_CATEGORIES

def list_available_models():
    """List available models by category"""
    print("Available AI Models by Category:")
    print("=" * 80)
    
    total_models = 0
    
    for category, subdirs in MODEL_CATEGORIES.items():
        models_found = []
        for subdir in subdirs:
            category_path = MODELS_DIR / subdir
            if category_path.exists():
                for ext in SUPPORTED_MODEL_FORMATS:
                    files = list(category_path.glob(f"*{ext}"))
                    models_found.extend([f.name for f in files])
        
        if models_found:
            print(f"\n{category.upper()} ({len(models_found)} models):")
            print("-" * 40)
            for i, model in enumerate(sorted(models_found)[:10], 1):  # Show first 10
                print(f"  {i:2d}. {model}")
            if len(models_found) > 10:
                print(f"     ... and {len(models_found) - 10} more")
            total_models += len(models_found)
    
    print(f"\n" + "=" * 80)
    print(f"TOTAL MODELS AVAILABLE: {total_models}")
    print(f"SUPPORTED FORMATS: {', '.join(SUPPORTED_MODEL_FORMATS)}")
    print(f"MODEL DIRECTORY: {MODELS_DIR}")
    print("=" * 80)
    
    # Show some example workflow inputs
    print("\nEXAMPLE WORKFLOW INPUTS:")
    print("-" * 40)
    
    # Example 1: Stable Diffusion model
    print("1. Stable Diffusion Checkpoint:")
    print("""
{
  "model_name": "babesIllustriousBy_v55DMD2",
  "input_data": {
    "prompt": "A beautiful landscape",
    "negative_prompt": "ugly, blurry",
    "steps": 20
  },
  "framework": "cuda"
}
""")
    
    # Example 2: Generic model
    print("2. Generic Model:")
    print("""
{
  "model_name": "your_model_name",
  "input_data": {
    "text": "Sample input text"
  },
  "parameters": {
    "execution_timeout": 120
  }
}
""")
    
    print("3. Image Processing:")
    print("""
{
  "model_name": "image_processor",
  "input_data": {
    "image_path": "input.jpg"
  },
  "framework": "pytorch"
}
""")

def main():
    try:
        list_available_models()
        return 0
    except Exception as e:
        print(f"Error listing models: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())