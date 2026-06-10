#!/usr/bin/env python3
"""
Flowwer API - Simple FastAPI server for workflows
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import importlib
from pathlib import Path
from typing import Dict, Any
import json

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
    try:
        module = importlib.import_module(f"workflows.{workflow_name}")
        available_workflows.append(workflow_name)
        print(f"[INFO] Loaded workflow: {workflow_name}")
    except Exception as e:
        print(f"[WARNING] Failed to load {workflow_name}: {e}")

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Flowwer API",
        "available_workflows": available_workflows,
        "total_workflows": len(available_workflows)
    }

@app.post("/workflows/{workflow_name}/execute")
def execute_workflow(workflow_name: str, input_data: Dict[str, Any]):
    """Execute a specific workflow"""
    
    if workflow_name not in available_workflows:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_name}' not found")
    
    try:
        module = importlib.import_module(f"workflows.{workflow_name}")
        execute_func = getattr(module, f"run_{workflow_name}")
        
        result = execute_func(input_data)
        return {
            "status": "success",
            "workflow": workflow_name,
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Workflow execution failed: {str(e)}"
        )

@app.get("/workflows")
def list_workflows():
    """List all available workflows"""
    workflow_details = []
    
    for workflow_name in available_workflows:
        try:
            module = importlib.import_module(f"workflows.{workflow_name}")
            docstring = getattr(module, f"run_{workflow_name}").__doc__ or "No description"
            workflow_details.append({
                "name": workflow_name,
                "description": docstring
            })
        except:
            workflow_details.append({
                "name": workflow_name,
                "description": "No description available"
            })
    
    return {
        "workflows": workflow_details,
        "count": len(workflow_details)
    }

@app.get("/workflows/{workflow_name}")
def get_workflow_details(workflow_name: str):
    """Get details about a specific workflow"""
    
    if workflow_name not in available_workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    try:
        module = importlib.import_module(f"workflows.{workflow_name}")
        
        # Get module docstring
        module_doc = module.__doc__ or "No module description"
        
        # Get function docstring
        func = getattr(module, f"run_{workflow_name}")
        func_doc = func.__doc__ or "No function description"
        
        # Get source code
        source_file = workflows_dir / f"{workflow_name}.py"
        with open(source_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        return {
            "name": workflow_name,
            "module_description": module_doc,
            "function_description": func_doc,
            "source_code": source_code
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get workflow details: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    print("Starting Flowwer API...")
    print(f"Available workflows: {available_workflows}")
    print("API will be available at: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)