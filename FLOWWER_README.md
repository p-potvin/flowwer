# Flowwer - Workflow Automation Platform

**The better version of workflow automation - superior, elegant, and powerful.**

## 🌸 About Flowwer

Flowwer is a workflow automation platform that transforms Gemini-generated workflow concepts into executable Python workflows with a RESTful API interface. Built for flexibility, scalability, and ease of use.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the API Server

```bash
python api.py
```

The API will be available at: `http://localhost:8004`

### 3. Test a Workflow

```bash
# Test the format workflow
python workflows/format.py

# Test the URL workflow
python workflows/url.py
```

## 📁 Project Structure

```
flowwer/
├── api.py                  # FastAPI server
├── requirements.txt        # Python dependencies
├── simple_convert.py       # Workflow conversion script
├── workflows/              # Generated workflows
│   ├── format.py           # Format workflow
│   ├── url.py              # URL workflow
│   ├── exportedat.py       # ExportedAt workflow
│   ├── count.py            # Count workflow
│   ├── title.py            # Title workflow
│   └── items.py            # Items workflow
└── README.md               # This file
```

## 🔧 API Endpoints

### GET `/`
Get API information and available workflows

**Response:**
```json
{
  "message": "Welcome to Flowwer API",
  "available_workflows": ["format", "url", "exportedat", "count", "title", "items"],
  "total_workflows": 6
}
```

### GET `/workflows`
List all available workflows with descriptions

**Response:**
```json
{
  "workflows": [
    {
      "name": "format",
      "description": "Execute the format workflow"
    },
    {
      "name": "url",
      "description": "Execute the url workflow"
    }
  ],
  "count": 6
}
```

### GET `/workflows/{workflow_name}`
Get detailed information about a specific workflow

**Response:**
```json
{
  "name": "format",
  "module_description": "format - Generated from Gemini workflow",
  "function_description": "Execute the format workflow",
  "source_code": "..."
}
```

### POST `/workflows/{workflow_name}/execute`
Execute a specific workflow

**Request Body:**
```json
{
  "input": "your data here",
  "parameters": {}
}
```

**Response:**
```json
{
  "status": "success",
  "workflow": "format",
  "result": {
    "workflow": "format",
    "input": "your data here",
    "message": "Workflow executed successfully",
    "status": "success"
  }
}
```

## 🎯 Available Workflows

### 1. Format Workflow
**File:** `workflows/format.py`
**Description:** Text formatting and transformation workflow
**Usage:**
```python
from workflows.format import run_format
result = run_format({"text": "sample text", "format_type": "uppercase"})
```

### 2. URL Workflow
**File:** `workflows/url.py`
**Description:** URL processing and analysis workflow
**Usage:**
```python
from workflows.url import run_url
result = run_url({"url": "https://example.com", "action": "validate"})
```

### 3. ExportedAt Workflow
**File:** `workflows/exportedat.py`
**Description:** Date/time export and formatting workflow
**Usage:**
```python
from workflows.exportedat import run_exportedat
result = run_exportedat({"timestamp": "2023-01-01", "format": "ISO"})
```

### 4. Count Workflow
**File:** `workflows/count.py`
**Description:** Counting and enumeration workflow
**Usage:**
```python
from workflows.count import run_count
result = run_count({"items": [1, 2, 3], "count_type": "total"})
```

### 5. Title Workflow
**File:** `workflows/title.py`
**Description:** Title generation and processing workflow
**Usage:**
```python
from workflows.title import run_title
result = run_title({"content": "article text", "style": "APA"})
```

### 6. Items Workflow
**File:** `workflows/items.py`
**Description:** Item processing and management workflow
**Usage:**
```python
from workflows.items import run_items
result = run_items({"items": ["item1", "item2"], "action": "sort"})
```

## 🛠️ Development

### Adding New Workflows

1. **Create a new workflow file** in the `workflows/` directory
2. **Follow the template:**
```python
#!/usr/bin/env python3
"""
WorkflowName - Description of the workflow
"""

def run_workflowname(input_data):
    """Execute the workflow"""
    # Your workflow logic here
    result = {
        'workflow': 'WorkflowName',
        'input': input_data,
        'message': 'Workflow executed successfully',
        'status': 'success'
    }
    return result

def test_workflow():
    """Test the workflow"""
    sample_input = {'test': 'data'}
    result = run_workflowname(sample_input)
    print(f"Result: {result}")
    return result

if __name__ == "__main__":
    test_workflow()
```

3. **The workflow will automatically be available** in the API

### Converting Gemini Workflows

Use the `simple_convert.py` script to convert Gemini-generated workflows:

```bash
python simple_convert.py
```

This will:
- Read workflows from `C:/Users/Administrator/Desktop/daily-workflow-gemini.json`
- Generate Python workflow files in the `workflows/` directory
- Automatically make them available through the API

## 🔄 Workflow Lifecycle

1. **Design**: Conceptualize workflow in Gemini
2. **Convert**: Use `simple_convert.py` to generate Python code
3. **Test**: Run workflow directly with `python workflows/workflow_name.py`
4. **Integrate**: Workflow automatically available in API
5. **Execute**: Call via API endpoint or direct Python import

## 📊 Technical Details

- **Framework**: FastAPI (high-performance, easy to use)
- **Language**: Python 3.10+
- **Architecture**: Modular, plugin-based workflow system
- **Performance**: Async-ready, scalable
- **Security**: CORS-enabled, input validation

## 🎯 Future Roadmap

- **Advanced Workflow Chaining**: Connect multiple workflows in sequences
- **Scheduling**: Cron-based workflow execution
- **Monitoring**: Execution logs and performance metrics
- **Authentication**: API key and JWT support
- **Web Interface**: Dashboard for workflow management
- **Workflow Marketplace**: Share and discover workflows

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a pull request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📧 Contact

For questions, suggestions, or support:
- **GitHub**: [p-potvin/flowwer](https://github.com/p-potvin/flowwer)
- **Issues**: Report bugs and request features
- **Discussions**: Join the community conversation

---

**Flowwer** - Where workflows bloom into automation 🌸