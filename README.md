# Azure DevOps MCP Server - Project Structure

This project has been modularized for better maintainability and organization.

## File Structure

```
azuredevopsmcp/
├── main.py              # Main entry point - initializes server and registers tools
├── config.py            # Configuration constants and settings
├── models.py            # Pydantic data models (WorkItem, TestCase)
├── client.py            # Azure DevOps API client class
├── parsers.py           # Functions to parse API responses into models
├── user_story_tools.py  # MCP tools for user story operations
├── test_case_tools.py   # MCP tools for test case operations
├── requirements.txt     # Python dependencies
├── __init__.py          # Package initialization
└── README.md            # This file
```

## Modules Overview

### `main.py`
- Entry point that initializes the FastMCP server
- Creates the AzureDevOpsClient instance
- Registers all tools from both tool modules
- Runs the MCP server

### `config.py`
- Contains all configuration constants
- Azure DevOps organization, project, and PAT settings
- API versions and timeout settings
- SSL and retry configurations

### `models.py`
- Pydantic models for data validation and serialization
- `WorkItem`: Base model for Azure DevOps work items
- `TestCase`: Extended model for test cases with additional fields

### `client.py`
- `AzureDevOpsClient`: Main API client class
- Handles authentication, SSL configuration, and retries
- Methods for all Azure DevOps API operations:
  - `get_work_items()`: Fetch work items by type
  - `get_work_item_by_id()`: Get specific work item
  - `search_work_items_by_title()`: Search by title
  - `get_work_items_by_state()`: Filter by state
  - `update_work_item()`: Update work item fields
  - `create_work_item()`: Create new work items

### `parsers.py`
- `parse_work_item()`: Converts API response to WorkItem model
- `parse_test_case()`: Converts API response to TestCase model
- Handles field extraction and data type conversion

### `user_story_tools.py`
- MCP tools specifically for user stories:
  - `get_user_stories()`: List user stories
  - `get_story_details()`: Get detailed story info
  - `search_stories_by_title()`: Search stories
  - `get_stories_by_state()`: Filter by state
  - `update_story()`: Update story fields
  - `create_user_story()`: Create new stories

### `test_case_tools.py`
- MCP tools specifically for test cases:
  - `get_test_cases()`: List test cases
  - `get_test_case_details()`: Get detailed test case info
  - `search_test_cases_by_title()`: Search test cases
  - `get_test_cases_by_state()`: Filter by state
  - `update_test_case()`: Update test case fields
  - `create_test_case()`: Create new test cases

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy the example environment file and fill in your values:
```bash
cp .env.example .env
```

Edit `.env` and set your Azure DevOps credentials:
```bash
# Required
AZURE_DEVOPS_PAT=your_personal_access_token_here

# Optional (with defaults)
AZURE_DEVOPS_ORG=your_org_name
AZURE_DEVOPS_PROJECT=your_project_name
```

### 3. Run the Server
```bash
python main.py
```

Or with python3:
```bash
python3 main.py
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AZURE_DEVOPS_PAT` | ✅ Yes | - | Personal Access Token for Azure DevOps |
| `AZURE_DEVOPS_ORG` | ❌ No | `executeauto` | Azure DevOps organization name |
| `AZURE_DEVOPS_PROJECT` | ❌ No | `Udemy` | Azure DevOps project name |
| `AZURE_DEVOPS_DISABLE_SSL_VERIFY` | ❌ No | `false` | Disable SSL verification (debugging only) |

## Benefits of Modularization

1. **Separation of Concerns**: Each module has a specific responsibility
2. **Maintainability**: Easier to modify and debug individual components
3. **Reusability**: Client and parsers can be reused in other projects
4. **Testability**: Each module can be tested independently
5. **Readability**: Smaller, focused files are easier to understand
6. **Scalability**: Easy to add new work item types or tools