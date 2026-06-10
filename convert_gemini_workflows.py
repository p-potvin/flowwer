#!/usr/bin/env python3
"""
Convert Gemini workflows to Flowwer format
"""

import json
import os
from pathlib import Path
from datetime import datetime

# Read Gemini workflows
gemini_file = r"C:\Users\Administrator\Desktop\daily-workflow-gemini.json"

with open(gemini_file, 'r', encoding='utf-8') as f:
    gemini_data = json.load(f)

print(f"Loaded {len(gemini_data)} workflows from Gemini")

# Create workflows directory
workflows_dir = Path("workflows")
workflows_dir.mkdir(exist_ok=True)

# Process each workflow
for workflow_name, workflow_data in gemini_data.items():
    print(f"\nProcessing workflow: {workflow_name}")
    
    # Create workflow file
    workflow_file = workflows_dir / f"{workflow_name.lower().replace(' ', '_')}.py"
    
    # Generate workflow code
    workflow_code = f'''#!/usr/bin/env python3
"""
{workflow_name} - Generated from Gemini workflow

Description: {workflow_data.get('description', 'No description provided')}
"""

from typing import Dict, Any, Optional
from pathlib import Path
import json
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class {workflow_name.replace(' ', '')}Input:
    """Input model for the {workflow_name} workflow"""
    def __init__(self, **kwargs):
        self.input_data = kwargs


class {workflow_name.replace(' ', '')}Output:
    """Output model for the {workflow_name} workflow"""
    def __init__(self, result: Dict[str, Any], status: str, error: Optional[str] = None):
        self.result = result
        self.status = status
        self.error = error
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {{
            'result': self.result,
            'status': self.status,
            'error': self.error,
            'timestamp': self.timestamp.isoformat()
        }}


def run_{workflow_name.lower().replace(' ', '_')}(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the {workflow_name} workflow"""
    logger.info(f"Starting {workflow_name} workflow")
    
    try:
        # Parse input
        parsed_input = {workflow_name.replace(' ', '')}Input(**input_data)
        
        # Workflow logic would go here
        # For now, we'll implement the basic structure based on Gemini's description
        
        workflow_logic = """
        # {workflow_data.get('description', 'No description')}
        # Steps: {workflow_data.get('steps', 'No steps defined')}
        """
        
        # Placeholder implementation
        result_data = {{
            'workflow': '{workflow_name}',
            'input': parsed_input.input_data,
            'message': 'Workflow executed successfully',
            'steps_completed': workflow_logic.count('Step')
        }}
        
        output = {workflow_name.replace(' ', '')}Output(
            result=result_data,
            status="success"
        )
        
        logger.info(f"{workflow_name} workflow completed successfully")
        return output.to_dict()
        
    except Exception as e:
        logger.error(f"{workflow_name} workflow failed: {e}")
        error_output = {workflow_name.replace(' ', '')}Output(
            result={{
                'workflow': '{workflow_name}',
                'error': str(e)
            }},
            status="failed",
            error=str(e)
        )
        return error_output.to_dict()


def test_workflow():
    """Test the workflow with sample input"""
    sample_input = {json.dumps(workflow_data.get('sample_input', {{'test': 'data'}}), indent=2)}
    
    print(f"Testing {workflow_name} workflow...")
    print(f"Sample input: {sample_input}")
    
    result = run_{workflow_name.lower().replace(' ', '_')}(sample_input)
    print(f"Result: {json.dumps(result, indent=2)}")
    
    return result


if __name__ == "__main__":
    test_workflow()
'''
    
    with open(workflow_file, 'w', encoding='utf-8') as f:
        f.write(workflow_code)
    
    print(f"✅ Created workflow file: {workflow_file}")

print(f"\n✅ All workflows converted successfully!")
print(f"📁 Workflows saved in: {workflows_dir}")

# Create a main API file
api_file = Path("main.py")
api_code = f"""#!/usr/bin/env python3
"""
Flowwer API - Main entry point for all workflows
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import importlib
import json
from pathlib import Path
from typing import Dict, Any

app = FastAPI(
    title="Flowwer API",
    description="API for executing various workflows",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load all workflows
workflows_dir = Path("workflows")
available_workflows = []

for workflow_file in workflows_dir.glob("*.py"):
    workflow_name = workflow_file.stem
    module_name = f"workflows.{workflow_name}"
    
    try:
        module = importlib.import_module(module_name)
        available_workflows.append(workflow_name)
        print(f"Loaded workflow: {workflow_name}")
    except Exception as e:
        print(f"Failed to load {workflow_name}: {e}")

@app.get("/")
def read_root():
    return {{
        "message": "Welcome to Flowwer API",
        "available_workflows": available_workflows,
        "total_workflows": len(available_workflows)
    }}

@app.post("/workflows/{workflow_name}/execute")
def execute_workflow(workflow_name: str, input_data: Dict[str, Any]):
    """Execute a specific workflow"""
    
    if workflow_name not in available_workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    try:
        module = importlib.import_module(f"workflows.{workflow_name}")
        execute_func = getattr(module, f"run_{workflow_name}")
        
        result = execute_func(input_data)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

@app.get("/workflows")
def list_workflows():
    """List all available workflows"""
    return {
        "workflows": available_workflows,
        "count": len(available_workflows)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""

with open(api_file, 'w', encoding='utf-8') as f:
    f.write(api_code)

print(f"✅ Created main API file: {api_file}")

# Create requirements file
requirements_file = Path("requirements.txt")
requirements = """fastapi>=0.95.0
uvicorn>=0.21.0
python-dotenv>=1.0.0
pydantic>=1.10.0
"""

with open(requirements_file, 'w') as f:
    f.write(requirements)

print(f"✅ Created requirements file: {requirements_file}")

print("\n🎉 Flowwer setup complete!")
print("\nTo run the API:")
print("  pip install -r requirements.txt")
print("  python main.py")
print("\nAPI will be available at: http://localhost:8000")