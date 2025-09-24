"""
Azure DevOps MCP Server Package

A modular Model Context Protocol (MCP) server for Azure DevOps integration.
"""

__version__ = "1.0.0"
__author__ = "ExecuteAutomation Ltd"

# Main components
from .main import main
from .client import AzureDevOpsClient
from .models import WorkItem, TestCase
from .parsers import parse_work_item, parse_test_case

__all__ = [
    "main",
    "AzureDevOpsClient", 
    "WorkItem",
    "TestCase",
    "parse_work_item",
    "parse_test_case"
]