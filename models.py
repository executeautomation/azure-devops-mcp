"""
Azure DevOps MCP Server - Data Models
"""

from typing import Optional
from pydantic import BaseModel


class WorkItem(BaseModel):
    """Work item model"""
    id: int
    title: str
    work_item_type: str
    state: str
    assigned_to: Optional[str] = None
    area_path: str
    iteration_path: str
    description: Optional[str] = None
    created_date: str
    changed_date: str
    tags: Optional[str] = None


class TestCase(BaseModel):
    """Test case model with additional test-specific fields"""
    id: int
    title: str
    work_item_type: str
    state: str
    assigned_to: Optional[str] = None
    area_path: str
    iteration_path: str
    description: Optional[str] = None
    created_date: str
    changed_date: str
    tags: Optional[str] = None
    # Test case specific fields
    test_steps: Optional[str] = None
    priority: Optional[int] = None
    automation_status: Optional[str] = None