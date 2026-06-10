# AI Model Execution Workflow

This workflow generates and executes Python scripts for running AI models using PyTorch, CUDA, and other frameworks.

## Overview

The AI Model Execution Workflow is designed to:

1. **Accept JSON input** with model specifications and input data
2. **Generate Python scripts** tailored to specific model types (image, text, generic)
3. **Execute the scripts** with proper error handling and timeout management
4. **Return structured results** with execution status and outputs

## Features

- **Multi-model support**: Handles image models, text models, and generic models
- **Framework flexibility**: Supports PyTorch, CUDA, xformers, sageattention, triton
- **Automatic script generation**: Creates appropriate Python code based on model type
- **Comprehensive error handling**: Validates inputs and handles execution failures
- **Logging and monitoring**: Detailed logging throughout the workflow execution
- **Timeout management**: Configurable execution timeouts

## Files

### Main Workflow Files

1. **`ai_model_execution_workflow.py`** - Full Mistral Workflows implementation (requires Mistral SDK)
2. **`ai_model_execution_workflow_simple.py`** - Simplified version for testing without SDK
3. **`test_workflow.py`** - Mistral's official workflow test runner
4. **`test_image_workflow.py`** - Test script for image model workflow

### Generated Outputs

- **`generated_scripts/`** - Directory containing automatically generated Python scripts
- Each script is timestamped and named according to the model used

## Usage

### Basic Usage (Simplified Version)

```bash
python ai_model_execution_workflow_simple.py
```

### Custom Input

```python
from ai_model_execution_workflow_simple import run_workflow

input_data = {
    "model_name": "your_model.pt",
    "input_data": {
        "text": "Sample input text",
        "additional_params": "values"
    },
    "parameters": {
        "execution_timeout": 120  # seconds
    },
    "framework": "pytorch"
}

result = run_workflow(input_data)
print(result)
```

### With Mistral Workflows SDK

```bash
python test_workflow.py ai_model_execution_workflow.py --input '{"model_name": "model.pt", "input_data": {"text": "hello"}, "framework": "pytorch"}' --timeout 60
```

## Input Format

The workflow accepts JSON input with the following structure:

```json
{
  "model_name": "string",          // Name of the AI model to use
  "input_data": {                   // Input data for the model
    "text": "string",              // For text models
    "image_path": "string",         // For image models
    "additional_params": {}         // Any additional parameters
  },
  "parameters": {                  // Optional execution parameters
    "execution_timeout": 300,        // Timeout in seconds (default: 300)
    "batch_size": 32,               // Batch size for processing
    "device": "cuda"               // Device to use
  },
  "framework": "pytorch",         // Framework to use (optional)
  "output_format": "json"          // Desired output format (optional)
}
```

## Output Format

The workflow returns a structured JSON result:

```json
{
  "script_path": "generated_scripts/20260609_171320_model.py",
  "execution_result": {
    "status": "success",
    "model": "model_name",
    "framework": "pytorch",
    "input_shape": [1, 3, 256, 256],
    "input_length": 128
  },
  "model_used": "model_name",
  "framework_used": "pytorch",
  "timestamp": "2026-06-09T17:13:42.764161",
  "status": "success",
  "error": null
}
```

## Supported Frameworks

- **PyTorch** (default)
- **CUDA** (automatic GPU acceleration)
- **xformers** (memory-efficient attention)
- **sageattention** (optimized attention mechanisms)
- **Triton** (GPU-accelerated operations)

## Model Types

The workflow automatically detects and handles different model types:

### Image Models
- Detected by: `.jpg`, `.png`, `.jpeg` extensions or "image" in model name
- Generates: Scripts with PIL, torchvision transforms, image processing
- Input: Expects `image_path` in input data

### Text Models  
- Detected by: "text", "language" in model name
- Generates: Scripts with transformers, tokenization
- Input: Expects `text` in input data

### Generic Models
- Default case for other model types
- Generates: Basic PyTorch model loading and execution

## Error Handling

The workflow includes comprehensive error handling:

- **Input validation**: Checks model existence and framework support
- **Execution timeouts**: Prevents hanging scripts
- **Subprocess errors**: Captures script execution failures
- **JSON parsing**: Handles malformed output
- **Workflow exceptions**: Custom exception types with error codes

## Logging

The workflow uses Python's logging module with INFO level by default:

- Logs all major workflow steps
- Records validation, script generation, execution
- Captures errors and exceptions
- Timestamps all log entries

## Example Workflow Execution

### Text Model Example

**Input:**
```json
{
  "model_name": "text_model.pt",
  "input_data": {"text": "Hello World"},
  "framework": "pytorch"
}
```

**Generated Script:**
```python
import torch
from transformers import AutoModel, AutoTokenizer
import json
import sys

# Load model from: D:/comfyui/resources/comfyui/models/text_model.pt
try:
    print("Loading model...")
    # tokenizer = AutoTokenizer.from_pretrained('model_path')
    # model = AutoModel.from_pretrained('model_path')
    
    input_data = {"text": "Hello World"}
    text_input = input_data.get('text', '')
    print(f"Processed text input (length: {len(text_input)})")
    
    print("Executing model...")
    result = {
        'status': 'success',
        'model': 'text_model.pt',
        'framework': 'pytorch',
        'input_length': len(text_input)
    }
    print(json.dumps(result))
    
except Exception as e:
    error_result = {
        'status': 'error',
        'model': 'text_model.pt',
        'error': str(e),
        'framework': 'pytorch'
    }
    print(json.dumps(error_result))
    sys.exit(1)
```

### Image Model Example

**Input:**
```json
{
  "model_name": "image_model.jpg",
  "input_data": {"image_path": "example.jpg"},
  "framework": "pytorch"
}
```

**Generated Script:**
```python
import torch
import torchvision.transforms as transforms
from PIL import Image
import json
import sys

# Load model from: D:/comfyui/resources/comfyui/models/image_model.jpg
try:
    print("Loading model...")
    
    input_data = {"image_path": "example.jpg"}
    if 'image_path' in input_data:
        image = Image.open(input_data['image_path'])
        transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
        ])
        image_tensor = transform(image).unsqueeze(0)
        print(f"Processed image: {image_tensor.shape}")
    
    print("Executing model...")
    result = {
        'status': 'success',
        'model': 'image_model.jpg',
        'framework': 'pytorch',
        'input_shape': list(image_tensor.shape)
    }
    print(json.dumps(result))
    
except Exception as e:
    error_result = {
        'status': 'error',
        'model': 'image_model.jpg',
        'error': str(e),
        'framework': 'pytorch'
    }
    print(json.dumps(error_result))
    sys.exit(1)
```

## Installation Requirements

For the full Mistral Workflows version:

```bash
pip install mistralai-workflows
```

For the simplified version (already included in standard Python):

```bash
pip install torch torchvision pillow
```

## Configuration

The workflow uses the following constants (configurable in the source):

- `MODELS_DIR`: Path to AI models (`D:/comfyui/resources/comfyui/models`)
- `DEFAULT_TIMEOUT`: Default execution timeout (300 seconds)
- `SUPPORTED_FRAMEWORKS`: List of supported frameworks

## Development Notes

### Adding New Model Types

To add support for new model types:

1. Add detection logic in `generate_python_script()`
2. Create appropriate script template with required imports
3. Update input validation if needed

### Extending Frameworks

To add new framework support:

1. Add framework name to `SUPPORTED_FRAMEWORKS`
2. Update framework detection logic
3. Add framework-specific imports and code generation

### Error Handling Enhancements

The workflow can be extended with:
- Retry logic for failed executions
- Fallback mechanisms for unavailable frameworks
- More detailed error classification

## Future Enhancements

- **Model registry**: Integration with model hubs and registries
- **Automatic dependency installation**: Check and install required packages
- **GPU/CPU auto-detection**: Automatic device selection
- **Batch processing**: Support for processing multiple inputs
- **API endpoint**: REST API for remote execution
- **Monitoring integration**: Prometheus, Grafana, or other monitoring

## License

This workflow is provided as part of the Mistral Workflows framework and follows its licensing terms.