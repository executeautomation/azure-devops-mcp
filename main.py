"""
Azure DevOps MCP Server - Main Entry Point

This is the main server file that initializes the FastMCP server and registers all tools.
"""

from fastmcp import FastMCP
from config import AZURE_DEVOPS_ORG, AZURE_DEVOPS_PROJECT, AZURE_DEVOPS_PAT
from client import AzureDevOpsClient
from user_story_tools import register_user_story_tools
from test_case_tools import register_test_case_tools


def main():
    """Initialize and run the Azure DevOps MCP server"""
    
    # Initialize the Azure DevOps client
    client = AzureDevOpsClient(AZURE_DEVOPS_ORG, AZURE_DEVOPS_PROJECT, AZURE_DEVOPS_PAT)
    
    # Initialize FastMCP server
    mcp = FastMCP("Azure DevOps MCP Server")
    
    # Register all tools
    register_user_story_tools(mcp, client)
    register_test_case_tools(mcp, client)
    
    # Run the server
    mcp.run()


if __name__ == "__main__":
    main()