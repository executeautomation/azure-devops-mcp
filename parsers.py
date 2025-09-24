"""
Azure DevOps MCP Server - Data Parsers
"""

from typing import Dict, Any
from models import WorkItem, TestCase


def parse_work_item(work_item_data: Dict[str, Any]) -> WorkItem:
    """Parse Azure DevOps work item data into WorkItem model"""
    fields = work_item_data.get("fields", {})
    
    # Extract assigned to (handle both display name and unique name)
    assigned_to = None
    if "System.AssignedTo" in fields:
        assigned_to_field = fields["System.AssignedTo"]
        if isinstance(assigned_to_field, dict):
            assigned_to = assigned_to_field.get("displayName")
        else:
            assigned_to = assigned_to_field
    
    return WorkItem(
        id=work_item_data["id"],
        title=fields.get("System.Title", ""),
        work_item_type=fields.get("System.WorkItemType", ""),
        state=fields.get("System.State", ""),
        assigned_to=assigned_to,
        area_path=fields.get("System.AreaPath", ""),
        iteration_path=fields.get("System.IterationPath", ""),
        description=fields.get("System.Description"),
        created_date=fields.get("System.CreatedDate", ""),
        changed_date=fields.get("System.ChangedDate", ""),
        tags=fields.get("System.Tags")
    )


def parse_test_case(work_item_data: Dict[str, Any]) -> TestCase:
    """Parse Azure DevOps test case data into TestCase model"""
    fields = work_item_data.get("fields", {})
    
    # Extract assigned to (handle both display name and unique name)
    assigned_to = None
    if "System.AssignedTo" in fields:
        assigned_to_field = fields["System.AssignedTo"]
        if isinstance(assigned_to_field, dict):
            assigned_to = assigned_to_field.get("displayName")
        else:
            assigned_to = assigned_to_field
    
    return TestCase(
        id=work_item_data["id"],
        title=fields.get("System.Title", ""),
        work_item_type=fields.get("System.WorkItemType", ""),
        state=fields.get("System.State", ""),
        assigned_to=assigned_to,
        area_path=fields.get("System.AreaPath", ""),
        iteration_path=fields.get("System.IterationPath", ""),
        description=fields.get("System.Description"),
        created_date=fields.get("System.CreatedDate", ""),
        changed_date=fields.get("System.ChangedDate", ""),
        tags=fields.get("System.Tags"),
        test_steps=fields.get("Microsoft.VSTS.TCM.Steps"),
        priority=fields.get("Microsoft.VSTS.Common.Priority"),
        automation_status=fields.get("Microsoft.VSTS.TCM.AutomationStatus")
    )