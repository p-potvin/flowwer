#!/usr/bin/env python3
"""
AI Model Execution Workflow - Simplified version for testing without Mistral SDK
Generates Python scripts that execute AI models via PyTorch, CUDA, etc.
"""

import json
import logging
import sys
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import subprocess

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Constants
MODELS_DIR = Path("D:/comfyui/resources/comfyui/models")
DEFAULT_TIMEOUT = 300  # 5 minutes timeout for model execution
SUPPORTED_FRAMEWORKS = ["pytorch", "cuda", "xformers", "sageattention", "triton"]
SUPPORTED_MODEL_FORMATS = [".safetensors", ".pt", ".pth", ".ckpt", ".gguf", ".bin", ".onnx"]

# Model type categories for better organization
MODEL_CATEGORIES = {
    "checkpoints": ["checkpoints"],
    "llm": ["LLM", "llm", "language_models"],
    "diffusion": ["diffusers", "diffusion_models"],
    "controlnet": ["controlnet"],
    "clip": ["clip", "clip_vision"],
    "vae": ["vae", "vae_approx"],
    "embeddings": ["embeddings"],
    "loras": ["loras"],
    "upscale": ["upscale_models", "latent_upscale_models"],
    "detection": ["detection", "face_parsing", "openpose", "mediapipe"],
    "segmentation": ["sams", "rembg", "background_removal"],
    "other": ["configs", "manifests", "tokenizers", "style_models", "unet"]
}


class WorkflowException(Exception):
    """Custom workflow exception"""
    def __init__(self, message: str, error_code: str = "WF_0000"):
        super().__init__(message)
        self.error_code = error_code


class ModelInput:
    """Input model for the workflow"""
    def __init__(self, model_name: str, input_data: Dict[str, Any], 
                 parameters: Optional[Dict[str, Any]] = None, 
                 framework: Optional[str] = None, 
                 output_format: Optional[str] = None):
        self.model_name = model_name
        self.input_data = input_data
        self.parameters = parameters or {}
        self.framework = framework
        self.output_format = output_format


class ModelOutput:
    """Output model for the workflow"""
    def __init__(self, script_path: str, execution_result: Optional[Dict[str, Any]], 
                 model_used: str, framework_used: str, status: str, 
                 error: Optional[str] = None):
        self.script_path = script_path
        self.execution_result = execution_result
        self.model_used = model_used
        self.framework_used = framework_used
        self.timestamp = datetime.now()
        self.status = status
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'script_path': self.script_path,
            'execution_result': self.execution_result,
            'model_used': self.model_used,
            'framework_used': self.framework_used,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status,
            'error': self.error
        }


class WorkflowState:
    """Internal workflow state"""
    def __init__(self):
        self.model_path: Optional[str] = None
        self.script_content: Optional[str] = None
        self.execution_log: List[str] = []
        self.current_step: str = "initialization"


def validate_input(input_data: ModelInput) -> Dict[str, Any]:
    """Validate the input data and ensure model exists"""
    logger.info(f"Validating input for model: {input_data.model_name}")
    
    # Check if model exists - search through subdirectories based on model type
    model_path = None
    model_category = None
    
    # First, check if it's a direct file path
    direct_path = MODELS_DIR / input_data.model_name
    if direct_path.exists():
        model_path = direct_path
        model_category = "direct"
    else:
        # Search through model categories
        for category, subdirs in MODEL_CATEGORIES.items():
            for subdir in subdirs:
                category_path = MODELS_DIR / subdir
                if category_path.exists():
                    # Look for the model in this category
                    for ext in SUPPORTED_MODEL_FORMATS:
                        model_file = category_path / f"{input_data.model_name}{ext}"
                        if model_file.exists():
                            model_path = model_file
                            model_category = category
                            break
                    if model_path:
                        break
            if model_path:
                break
    
    if not model_path:
        # Provide helpful error with available models
        available_models = []
        for category, subdirs in MODEL_CATEGORIES.items():
            for subdir in subdirs:
                category_path = MODELS_DIR / subdir
                if category_path.exists():
                    for ext in SUPPORTED_MODEL_FORMATS:
                        files = list(category_path.glob(f"*{ext}"))
                        available_models.extend([f.relative_to(MODELS_DIR) for f in files])
        
        raise WorkflowException(
            f"Model {input_data.model_name} not found. "
            f"Available models: {available_models[:10]}{'...' if len(available_models) > 10 else ''}",
            error_code="WF_1001"
        )
    
    # Validate framework
    if input_data.framework and input_data.framework not in SUPPORTED_FRAMEWORKS:
        raise WorkflowException(
            f"Unsupported framework: {input_data.framework}. Supported: {SUPPORTED_FRAMEWORKS}",
            error_code="WF_1002"
        )
    
    # Auto-detect framework based on model type if not specified
    detected_framework = input_data.framework
    if not detected_framework:
        if model_category in ["llm", "language_models"]:
            detected_framework = "pytorch"  # Most LLM models use PyTorch
        elif model_category in ["checkpoints", "diffusion", "controlnet"]:
            detected_framework = "cuda"  # Diffusion models typically use CUDA
        elif any(ext in [".gguf", ".bin"] for ext in SUPPORTED_MODEL_FORMATS if str(model_path).endswith(ext)):
            detected_framework = "triton"  # GGUF/BIN models often use Triton
        else:
            detected_framework = "pytorch"  # Default to PyTorch
    
    return {
        "model_path": str(model_path),
        "model_category": model_category,
        "detected_framework": detected_framework,
        "validated_input": {
            'model_name': input_data.model_name,
            'input_data': input_data.input_data,
            'parameters': input_data.parameters,
            'framework': detected_framework
        }
    }


def generate_python_script(
    model_name: str, 
    model_path: str, 
    input_data: Dict[str, Any], 
    parameters: Optional[Dict[str, Any]] = None,
    framework: Optional[str] = None,
    model_category: Optional[str] = None
) -> str:
    """Generate Python script for model execution"""
    logger.info(f"Generating Python script for model: {model_name}")
    
    # Determine framework (auto-detect if not specified)
    detected_framework = framework or "pytorch"
    
    # Determine model type based on file extension and category
    model_ext = Path(model_path).suffix.lower()
    
    # Generate appropriate script based on model type and framework
    if model_category in ["llm", "language_models"] or "text" in model_name.lower() or "language" in model_name.lower():
        # Text/LLM processing model
        if model_ext == ".gguf":
            # GGUF model (typically for llama.cpp or similar)
            script_content = f"""
import json
import sys

# Load GGUF model from: {model_path}
try:
    print("Loading GGUF model...")
    # from llama_cpp import Llama
    # model = Llama(model_path='{model_path}', n_gpu_layers=-1)
    
    # Process input data
    input_data = {json.dumps(input_data)}
    text_input = input_data.get('text', '')
    
    print(f"Processed text input (length: {{len(text_input)}})")
    
    # Execute model (placeholder)
    print("Executing GGUF model...")
    # output = model(text_input, max_tokens=512, temperature=0.7)
    
    # Return result
    result = {{
        'status': 'success',
        'model': '{model_name}',
        'framework': '{detected_framework}',
        'input_length': len(text_input),
        'model_type': 'GGUF'
    }}
    
    print("Execution completed successfully")
    print(json.dumps(result))
    
except Exception as e:
    error_result = {{
        'status': 'error',
        'model': '{model_name}',
        'error': str(e),
        'framework': '{detected_framework}'
    }}
    print("Execution failed:")
    print(json.dumps(error_result))
    sys.exit(1)
"""
        elif model_ext in [".safetensors", ".bin"]:
            # Safetensors or binary model (HuggingFace format)
            script_content = f"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import json
import sys

# Load model from: {model_path}
try:
    print("Loading HuggingFace model...")
    # tokenizer = AutoTokenizer.from_pretrained('{model_path}')
    # model = AutoModelForCausalLM.from_pretrained('{model_path}', torch_dtype=torch.float16, device_map='auto')
    
    # Process input data
    input_data = {json.dumps(input_data)}
    text_input = input_data.get('text', '')
    
    # Tokenize input
    # inputs = tokenizer(text_input, return_tensors='pt').to('cuda')
    print(f"Processed text input (length: {{len(text_input)}})")
    
    # Execute model (placeholder)
    print("Executing model...")
    # outputs = model.generate(**inputs, max_new_tokens=512)
    # result_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Return result
    result = {{
        'status': 'success',
        'model': '{model_name}',
        'framework': '{detected_framework}',
        'input_length': len(text_input),
        'model_type': 'HuggingFace'
    }}
    
    print("Execution completed successfully")
    print(json.dumps(result))
    
except Exception as e:
    error_result = {{
        'status': 'error',
        'model': '{model_name}',
        'error': str(e),
        'framework': '{detected_framework}'
    }}
    print("Execution failed:")
    print(json.dumps(error_result))
    sys.exit(1)
"""
        else:
            # Generic text model
            script_content = f"""
import torch
from transformers import AutoModel, AutoTokenizer
import json
import sys

# Load model from: {model_path}
try:
    print("Loading text model...")
    # tokenizer = AutoTokenizer.from_pretrained('{model_path}')
    # model = AutoModel.from_pretrained('{model_path}')
    
    # Process input data
    input_data = {json.dumps(input_data)}
    text_input = input_data.get('text', '')
    
    # Tokenize input
    # inputs = tokenizer(text_input, return_tensors='pt', padding=True, truncation=True)
    print(f"Processed text input (length: {{len(text_input)}})")
    
    # Execute model (placeholder)
    print("Executing model...")
    # outputs = model(**inputs)
    
    # Return result
    result = {{
        'status': 'success',
        'model': '{model_name}',
        'framework': '{detected_framework}',
        'input_length': len(text_input)
    }}
    
    print("Execution completed successfully")
    print(json.dumps(result))
    
except Exception as e:
    error_result = {{
        'status': 'error',
        'model': '{model_name}',
        'error': str(e),
        'framework': '{detected_framework}'
    }}
    print("Execution failed:")
    print(json.dumps(error_result))
    sys.exit(1)
"""
    
    elif model_category in ["checkpoints", "diffusion", "controlnet"] or any(ext in model_name.lower() 
                                                                           for ext in ['.png', '.jpg', '.jpeg']):
        # Image/diffusion processing model
        if model_ext == ".safetensors":
            # Stable Diffusion safetensors model
            script_content = f"""
import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import json
import sys

# Load Stable Diffusion model from: {model_path}
try:
    print("Loading Stable Diffusion model...")
    # pipe = StableDiffusionPipeline.from_single_file('{model_path}', torch_dtype=torch.float16)
    # pipe = pipe.to('cuda')
    
    # Process input data
    input_data = {json.dumps(input_data)}
    prompt = input_data.get('prompt', 'A beautiful landscape')
    
    print(f"Processing prompt: {{prompt}}")
    
    # Execute model (placeholder)
    print("Generating image...")
    # image = pipe(prompt).images[0]
    
    # Return result
    result = {{
        'status': 'success',
        'model': '{model_name}',
        'framework': '{detected_framework}',
        'prompt': prompt,
        'model_type': 'StableDiffusion'
    }}
    
    print("Execution completed successfully")
    print(json.dumps(result))
    
except Exception as e:
    error_result = {{
        'status': 'error',
        'model': '{model_name}',
        'error': str(e),
        'framework': '{detected_framework}'
    }}
    print("Execution failed:")
    print(json.dumps(error_result))
    sys.exit(1)
"""
        else:
            # Generic image processing model
            script_content = f"""
import torch
import torchvision.transforms as transforms
from PIL import Image
import json
import sys

# Load model from: {model_path}
try:
    # This would be replaced with actual model loading code
    print("Loading image model...")
    # model = torch.load('{model_path}', map_location='cuda' if torch.cuda.is_available() else 'cpu')
    
    # Process input data
    input_data = {json.dumps(input_data)}
    
    # For image models, we'd process the image
    if 'image_path' in input_data:
        image = Image.open(input_data['image_path'])
        transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
        ])
        image_tensor = transform(image).unsqueeze(0)
        print(f"Processed image: {{image_tensor.shape}}")
    
    # Execute model (placeholder)
    print("Executing model...")
    # output = model(image_tensor)
    
    # Return result
    result = {{
        'status': 'success',
        'model': '{model_name}',
        'framework': '{detected_framework}',
        'input_shape': list(image_tensor.shape) if 'image_tensor' in locals() else None
    }}
    
    print("Execution completed successfully")
    print(json.dumps(result))
    
except Exception as e:
    error_result = {{
        'status': 'error',
        'model': '{model_name}',
        'error': str(e),
        'framework': '{detected_framework}'
    }}
    print("Execution failed:")
    print(json.dumps(error_result))
    sys.exit(1)
"""
    
    elif model_category in ["vae", "embeddings", "upscale"]:
        # Specialized models (VAE, embeddings, upscale)
        script_content = f"""
import torch
import json
import sys

# Load {model_category.upper()} model from: {model_path}
try:
    print(f"Loading {model_category.upper()} model...")
    # model = torch.load('{model_path}', map_location='cuda' if torch.cuda.is_available() else 'cpu')
    
    # Process input data
    input_data = {json.dumps(input_data)}
    
    print("Executing model...")
    # output = model(input_data)
    
    # Return result
    result = {{
        'status': 'success',
        'model': '{model_name}',
        'framework': '{detected_framework}',
        'model_type': '{model_category.upper()}'
    }}
    
    print("Execution completed successfully")
    print(json.dumps(result))
    
except Exception as e:
    error_result = {{
        'status': 'error',
        'model': '{model_name}',
        'error': str(e),
        'framework': '{detected_framework}'
    }}
    print("Execution failed:")
    print(json.dumps(error_result))
    sys.exit(1)
"""
    
    else:
        # Generic model (fallback)
        script_content = f"""
import torch
import json
import sys

# Load model from: {model_path}
try:
    print("Loading model...")
    # model = torch.load('{model_path}', map_location='cuda' if torch.cuda.is_available() else 'cpu')
    
    # Process input data
    input_data = {json.dumps(input_data)}
    
    print("Executing model...")
    # output = model(input_data)
    
    # Return result
    result = {{
        'status': 'success',
        'model': '{model_name}',
        'framework': '{detected_framework}'
    }}
    
    print("Execution completed successfully")
    print(json.dumps(result))
    
except Exception as e:
    error_result = {{
        'status': 'error',
        'model': '{model_name}',
        'error': str(e),
        'framework': '{detected_framework}'
    }}
    print("Execution failed:")
    print(json.dumps(error_result))
    sys.exit(1)
"""
    
    logger.info(f"Generated script for {model_name} using {detected_framework} (category: {model_category})")
    return script_content


def save_script(script_content: str, model_name: str) -> str:
    """Save generated script to file"""
    logger.info(f"Saving script for model: {model_name}")
    
    # Create scripts directory if it doesn't exist
    scripts_dir = Path("generated_scripts")
    scripts_dir.mkdir(exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{model_name.replace('/', '_').replace('\\', '_')}.py"
    script_path = scripts_dir / filename
    
    # Write script content
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    logger.info(f"Script saved to: {script_path}")
    return str(script_path)


def execute_script(script_path: str, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """Execute the generated Python script"""
    logger.info(f"Executing script: {script_path}")
    
    try:
        # Execute the script using Python
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True
        )
        
        # Parse the output (assuming JSON format)
        try:
            output_data = json.loads(result.stdout.strip())
        except json.JSONDecodeError:
            output_data = {
                'status': 'success',
                'raw_output': result.stdout,
                'stderr': result.stderr
            }
        
        logger.info(f"Script executed successfully: {script_path}")
        return output_data
        
    except subprocess.TimeoutExpired:
        logger.error(f"Script execution timed out: {script_path}")
        return {
            'status': 'timeout',
            'error': f'Execution timed out after {timeout} seconds',
            'script_path': script_path
        }
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Script execution failed: {script_path}")
        return {
            'status': 'error',
            'error': e.stderr,
            'return_code': e.returncode,
            'script_path': script_path
        }
        
    except Exception as e:
        logger.error(f"Unexpected error executing script: {script_path}")
        return {
            'status': 'error',
            'error': str(e),
            'script_path': script_path
        }


def run_workflow(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Main workflow execution"""
    state = WorkflowState()
    
    try:
        # Parse input
        logger.info("Starting AI Model Execution Workflow")
        parsed_input = ModelInput(
            model_name=input_data['model_name'],
            input_data=input_data['input_data'],
            parameters=input_data.get('parameters'),
            framework=input_data.get('framework'),
            output_format=input_data.get('output_format')
        )
        
        # Step 1: Validate input
        state.current_step = "validation"
        validation_result = validate_input(parsed_input)
        state.model_path = validation_result["model_path"]
        logger.info(f"Input validation completed for model: {parsed_input.model_name}")
        
        # Step 2: Generate Python script
        state.current_step = "script_generation"
        script_content = generate_python_script(
            model_name=parsed_input.model_name,
            model_path=state.model_path,
            input_data=parsed_input.input_data,
            parameters=parsed_input.parameters,
            framework=validation_result.get("detected_framework"),
            model_category=validation_result.get("model_category")
        )
        state.script_content = script_content
        logger.info(f"Python script generated for model: {parsed_input.model_name}")
        
        # Step 3: Save script
        state.current_step = "script_saving"
        script_path = save_script(
            script_content=script_content,
            model_name=parsed_input.model_name
        )
        logger.info(f"Script saved: {script_path}")
        
        # Step 4: Execute script
        state.current_step = "script_execution"
        execution_result = execute_script(
            script_path=script_path,
            timeout=parsed_input.parameters.get('execution_timeout', DEFAULT_TIMEOUT)
        )
        logger.info(f"Script execution completed: {script_path}")
        
        # Prepare final output
        output = ModelOutput(
            script_path=script_path,
            execution_result=execution_result,
            model_used=parsed_input.model_name,
            framework_used=parsed_input.framework or "pytorch",
            status=execution_result.get('status', 'completed'),
            error=execution_result.get('error')
        )
        
        logger.info("Workflow completed successfully")
        return output.to_dict()
        
    except WorkflowException as e:
        logger.error(f"Workflow failed with error: {e}")
        error_output = ModelOutput(
            script_path=state.model_path or "N/A",
            execution_result=None,
            model_used=input_data.get('model_name', 'unknown'),
            framework_used=input_data.get('framework', 'unknown'),
            status="failed",
            error=str(e)
        )
        return error_output.to_dict()
        
    except Exception as e:
        logger.error(f"Unexpected workflow error: {e}", exc_info=True)
        error_output = ModelOutput(
            script_path=state.model_path or "N/A",
            execution_result=None,
            model_used=input_data.get('model_name', 'unknown'),
            framework_used=input_data.get('framework', 'unknown'),
            status="error",
            error=f"Unexpected error: {str(e)}"
        )
        return error_output.to_dict()


def main():
    """Test the workflow with sample input"""
    # Sample input
    test_input = {
        "model_name": "test_model.pt",
        "input_data": {
            "text": "Hello World",
            "additional_param": "value"
        },
        "parameters": {
            "execution_timeout": 60
        },
        "framework": "pytorch"
    }
    
    print("Running AI Model Execution Workflow...")
    print(f"Input: {json.dumps(test_input, indent=2)}")
    
    try:
        result = run_workflow(test_input)
        print("\nWorkflow completed!")
        print(f"Result: {json.dumps(result, indent=2)}")
        
        # Check if script was generated
        if 'script_path' in result and Path(result['script_path']).exists():
            print(f"\nGenerated script available at: {result['script_path']}")
            
    except Exception as e:
        print(f"Workflow failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())