# Azure DevOps MCP Server

A modular Model Context Protocol (MCP) server for Azure DevOps integration, providing tools to manage user stories and test cases.

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

### 3. Configure MCP Server in Claude
Add the following configuration to your Claude MCP settings (`mcp.json`):

```json
{
  "AzureDevOps": {
    "command": "python3",
    "args": ["~/main.py"],
    "env": {
      "AZURE_DEVOPS_PAT": "your_personal_access_token_here",
      "AZURE_DEVOPS_ORG": "your_org_name",
      "AZURE_DEVOPS_PROJECT": "your_project_name",
      "AZURE_DEVOPS_DISABLE_SSL_VERIFY": "false"
    }
  }
}
```

**Note**: Replace the values with your actual Azure DevOps credentials and paths.

### 4. Run the Server (Optional - for testing)
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

**Note**: When using MCP configuration with Claude, you can set these environment variables directly in the `mcp.json` file instead of using a `.env` file.

## Available Tools

### User Story Tools
- `get_user_stories()` - List user stories
- `get_story_details()` - Get detailed story information
- `search_stories_by_title()` - Search stories by title
- `get_stories_by_state()` - Filter stories by state
- `update_story()` - Update story fields
- `create_user_story()` - Create new stories

### Test Case Tools
- `get_test_cases()` - List test cases
- `get_test_case_details()` - Get detailed test case information
- `search_test_cases_by_title()` - Search test cases by title
- `get_test_cases_by_state()` - Filter test cases by state
- `update_test_case()` - Update test case fields
- `create_test_case()` - Create new test cases

## Benefits of Modularization

1. **Separation of Concerns**: Each module has a specific responsibility
2. **Maintainability**: Easier to modify and debug individual components
3. **Reusability**: Client and parsers can be reused in other projects
4. **Testability**: Each module can be tested independently
5. **Readability**: Smaller, focused files are easier to understand
6. **Scalability**: Easy to add new work item types or tools