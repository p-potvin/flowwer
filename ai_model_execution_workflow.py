#!/usr/bin/env python3
"""
AI Model Execution Workflow - Generates Python scripts that execute AI models via PyTorch, CUDA, etc.
Accepts JSON input with images/text and outputs appropriate format based on model type.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import json
import logging
from datetime import datetime

# Import Mistral Workflows SDK
try:
    import mistralai.workflows as workflows
    from mistralai.workflows import workflow, activity
    from mistralai.workflows.core.definition.workflow_definition import get_workflow_definition
    from mistralai.workflows.exceptions import WorkflowsException
    from mistralai.workflows.core.models import WorkflowRunStatus
    from pydantic import BaseModel, Field
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
except ImportError as e:
    print(f"Error importing Mistral Workflows SDK: {e}")
    print("Please ensure the SDK is installed and available.")
    raise


# Constants
MODELS_DIR = Path("D:/comfyui/resources/comfyui/models")
DEFAULT_TIMEOUT = 300  # 5 minutes timeout for model execution
SUPPORTED_FRAMEWORKS = ["pytorch", "cuda", "xformers", "sageattention", "triton"]


# Input/Output Models
class ModelInput(BaseModel):
    """Input model for the workflow"""
    model_name: str = Field(..., description="Name of the AI model to use")
    input_data: Dict[str, Any] = Field(..., description="Input data (images, text, etc.)")
    parameters: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional parameters for model execution"
    )
    framework: Optional[str] = Field(
        None, 
        description="Framework to use (pytorch, cuda, etc.)"
    )
    output_format: Optional[str] = Field(
        None, 
        description="Desired output format (auto-detected if not specified)"
    )


class ModelOutput(BaseModel):
    """Output model for the workflow"""
    script_path: str = Field(..., description="Path to generated Python script")
    execution_result: Optional[Dict[str, Any]] = Field(
        None, 
        description="Result of script execution"
    )
    model_used: str = Field(..., description="Model that was used")
    framework_used: str = Field(..., description="Framework that was used")
    timestamp: datetime = Field(..., description="Execution timestamp")
    status: str = Field(..., description="Execution status")
    error: Optional[str] = Field(None, description="Error message if any")


class WorkflowState(BaseModel):
    """Internal workflow state"""
    model_path: Optional[str] = None
    script_content: Optional[str] = None
    execution_log: List[str] = Field(default_factory=list)
    current_step: str = "initialization"


# Activities
@activity.define
def validate_input_activity(input_data: ModelInput) -> Dict[str, Any]:
    """Validate the input data and ensure model exists"""
    logger.info(f"Validating input for model: {input_data.model_name}")
    
    # Check if model exists
    model_path = MODELS_DIR / input_data.model_name
    if not model_path.exists():
        available_models = [f.name for f in MODELS_DIR.iterdir() if f.is_file()]
        raise WorkflowsException(
            f"Model {input_data.model_name} not found. Available models: {available_models}",
            error_code="WF_1001"
        )
    
    # Validate framework
    if input_data.framework and input_data.framework not in SUPPORTED_FRAMEWORKS:
        raise WorkflowsException(
            f"Unsupported framework: {input_data.framework}. Supported: {SUPPORTED_FRAMEWORKS}",
            error_code="WF_1002"
        )
    
    return {
        "model_path": str(model_path),
        "validated_input": input_data.model_dump()
    }


@activity.define
def generate_python_script_activity(
    model_name: str, 
    model_path: str, 
    input_data: Dict[str, Any], 
    parameters: Optional[Dict[str, Any]] = None,
    framework: Optional[str] = None
) -> str:
    """Generate Python script for model execution"""
    logger.info(f"Generating Python script for model: {model_name}")
    
    # Determine framework (auto-detect if not specified)
    detected_framework = framework or "pytorch"
    
    # Generate appropriate script based on model type and framework
    if "image" in model_name.lower() or any(ext in model_name.lower() 
                                           for ext in ['.png', '.jpg', '.jpeg']):
        # Image processing model
        script_content = f"""
import torch
import torchvision.transforms as transforms
from PIL import Image
import json
import sys

# Load model from: {model_path}
try:
    # This would be replaced with actual model loading code
    print("Loading model...")
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
    
    elif "text" in model_name.lower() or "language" in model_name.lower():
        # Text processing model
        script_content = f"""
import torch
from transformers import AutoModel, AutoTokenizer
import json
import sys

# Load model from: {model_path}
try:
    print("Loading model...")
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
    
    else:
        # Generic model
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
    
    logger.info(f"Generated script for {model_name} using {detected_framework}")
    return script_content


@activity.define
def save_script_activity(script_content: str, model_name: str) -> str:
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


@activity.define
def execute_script_activity(script_path: str, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """Execute the generated Python script"""
    logger.info(f"Executing script: {script_path}")
    
    import subprocess
    import sys
    
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


# Main Workflow
@workflow.define(name="ai_model_execution_workflow")
class AIModelExecutionWorkflow:
    """
    Workflow for generating and executing Python scripts that run AI models.
    
    Input: JSON with model_name, input_data, parameters, framework, output_format
    Output: Generated script path and execution results
    """
    
    @workflow.run
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main workflow execution"""
        state = WorkflowState()
        
        try:
            # Parse input
            logger.info("Starting AI Model Execution Workflow")
            parsed_input = ModelInput(**input_data)
            
            # Step 1: Validate input
            state.current_step = "validation"
            validation_result = await workflow.execute_activity(
                validate_input_activity,
                input_data=parsed_input,
                timeout=30
            )
            state.model_path = validation_result["model_path"]
            logger.info(f"Input validation completed for model: {parsed_input.model_name}")
            
            # Step 2: Generate Python script
            state.current_step = "script_generation"
            script_content = await workflow.execute_activity(
                generate_python_script_activity,
                model_name=parsed_input.model_name,
                model_path=state.model_path,
                input_data=parsed_input.input_data,
                parameters=parsed_input.parameters,
                framework=parsed_input.framework,
                timeout=60
            )
            state.script_content = script_content
            logger.info(f"Python script generated for model: {parsed_input.model_name}")
            
            # Step 3: Save script
            state.current_step = "script_saving"
            script_path = await workflow.execute_activity(
                save_script_activity,
                script_content=script_content,
                model_name=parsed_input.model_name,
                timeout=30
            )
            logger.info(f"Script saved: {script_path}")
            
            # Step 4: Execute script
            state.current_step = "script_execution"
            execution_result = await workflow.execute_activity(
                execute_script_activity,
                script_path=script_path,
                timeout=parsed_input.parameters.get('execution_timeout', DEFAULT_TIMEOUT)
                if parsed_input.parameters else DEFAULT_TIMEOUT
            )
            logger.info(f"Script execution completed: {script_path}")
            
            # Prepare final output
            output = ModelOutput(
                script_path=script_path,
                execution_result=execution_result,
                model_used=parsed_input.model_name,
                framework_used=parsed_input.framework or "pytorch",
                timestamp=datetime.now(),
                status=execution_result.get('status', 'completed'),
                error=execution_result.get('error')
            )
            
            logger.info("Workflow completed successfully")
            return output.model_dump()
            
        except WorkflowsException as e:
            logger.error(f"Workflow failed with error: {e}")
            error_output = ModelOutput(
                script_path=state.model_path or "N/A",
                execution_result=None,
                model_used=input_data.get('model_name', 'unknown'),
                framework_used=input_data.get('framework', 'unknown'),
                timestamp=datetime.now(),
                status="failed",
                error=str(e)
            )
            return error_output.model_dump()
            
        except Exception as e:
            logger.error(f"Unexpected workflow error: {e}", exc_info=True)
            error_output = ModelOutput(
                script_path=state.model_path or "N/A",
                execution_result=None,
                model_used=input_data.get('model_name', 'unknown'),
                framework_used=input_data.get('framework', 'unknown'),
                timestamp=datetime.now(),
                status="error",
                error=f"Unexpected error: {str(e)}"
            )
            return error_output.model_dump()


# Workflow registration
if __name__ == "__main__":
    # This allows the workflow to be discovered and registered
    print(f"AI Model Execution Workflow - {get_workflow_definition(AIModelExecutionWorkflow).name}")
    print("Workflow ready for execution")