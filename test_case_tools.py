"""
Azure DevOps MCP Server - Test Case Tools
"""

from typing import Optional
from fastmcp import FastMCP
from client import AzureDevOpsClient
from parsers import parse_test_case, parse_work_item


def register_test_case_tools(mcp: FastMCP, client: AzureDevOpsClient):
    """Register all test case related tools with the MCP server"""
    
    @mcp.tool()
    def get_test_cases(limit: int = 50) -> str:
        """
        Retrieve test cases from Azure DevOps

        Args:
            limit: Maximum number of test cases to retrieve (default: 50, max: 200)

        Returns:
            JSON string containing the test cases
        """
        try:
            # Validate limit
            limit = min(max(1, limit), 200)
            
            # Fetch test cases
            work_items_data = client.get_work_items(work_item_type="Test Case", top=limit)
            
            # Parse test cases
            test_cases = []
            for item_data in work_items_data:
                try:
                    test_case = parse_test_case(item_data)
                    test_cases.append(test_case.dict())
                except Exception as e:
                    # Skip items that can't be parsed - don't print to stdout in MCP server
                    continue
            
            return f"Retrieved {len(test_cases)} test cases:\n" + str(test_cases)
            
        except Exception as e:
            return f"Error retrieving test cases: {str(e)}"

    @mcp.tool()
    def get_test_case_details(test_case_id: int) -> str:
        """
        Get detailed information for a specific test case

        Args:
            test_case_id: The ID of the test case to retrieve

        Returns:
            Detailed information about the test case including steps
        """
        try:
            # Fetch work item by ID
            work_item_data = client.get_work_item_by_id(test_case_id)
            
            if work_item_data is None:
                return f"Test case with ID {test_case_id} not found"
            
            # Check if it's actually a test case
            work_item_type = work_item_data.get("fields", {}).get("System.WorkItemType", "")
            if work_item_type != "Test Case":
                return f"Work item {test_case_id} is not a test case (it's a {work_item_type})"
            
            # Parse test case
            test_case = parse_test_case(work_item_data)
            
            return f"Test Case Details:\n{test_case.dict()}"
            
        except Exception as e:
            return f"Error retrieving test case details: {str(e)}"

    @mcp.tool()
    def search_test_cases_by_title(search_term: str, limit: int = 20) -> str:
        """
        Search for test cases by title

        Args:
            search_term: Term to search for in test case titles
            limit: Maximum number of results to return (default: 20)

        Returns:
            List of matching test cases
        """
        try:
            # Validate limit
            limit = min(max(1, limit), 100)
            
            # Search test cases
            work_items_data = client.search_work_items_by_title(
                search_term=search_term,
                work_item_type="Test Case",
                top=limit
            )
            
            # Parse test cases
            test_cases = []
            for item_data in work_items_data:
                try:
                    test_case = parse_test_case(item_data)
                    test_cases.append(test_case.dict())
                except Exception as e:
                    # Skip items that can't be parsed - don't print to stdout in MCP server
                    continue
            
            return f"Found {len(test_cases)} test cases matching '{search_term}':\n" + str(test_cases)
            
        except Exception as e:
            return f"Error searching test cases: {str(e)}"

    @mcp.tool()
    def get_test_cases_by_state(state: str, limit: int = 50) -> str:
        """
        Get test cases filtered by state

        Args:
            state: State to filter by (e.g., 'Design', 'Ready', 'Closed')
            limit: Maximum number of test cases to retrieve (default: 50)

        Returns:
            List of test cases in the specified state
        """
        try:
            # Validate limit
            limit = min(max(1, limit), 200)
            
            # Fetch test cases by state
            work_items_data = client.get_work_items_by_state(
                state=state,
                work_item_type="Test Case",
                top=limit
            )
            
            # Parse test cases
            test_cases = []
            for item_data in work_items_data:
                try:
                    test_case = parse_test_case(item_data)
                    test_cases.append(test_case.dict())
                except Exception as e:
                    # Skip items that can't be parsed - don't print to stdout in MCP server
                    continue
            
            return f"Found {len(test_cases)} test cases in state '{state}':\n" + str(test_cases)
            
        except Exception as e:
            return f"Error retrieving test cases by state: {str(e)}"

    @mcp.tool()
    def update_test_case(
        test_case_id: int,
        title: Optional[str] = None,
        state: Optional[str] = None,
        assigned_to: Optional[str] = None,
        description: Optional[str] = None,
        test_steps: Optional[str] = None,
        priority: Optional[int] = None,
        automation_status: Optional[str] = None,
        tags: Optional[str] = None,
        area_path: Optional[str] = None,
        iteration_path: Optional[str] = None
    ) -> str:
        """
        Update a test case with new field values

        Args:
            test_case_id: The ID of the test case to update
            title: Update the test case title
            state: Update the state (e.g., 'Design', 'Ready', 'Closed')
            assigned_to: Assign to a user (use display name or email)
            description: Update the test case description
            test_steps: Update the test steps
            priority: Update the priority (1-4, where 1 is highest)
            automation_status: Update automation status ('Automated', 'Not Automated', 'Planned')
            tags: Update tags (semicolon-separated string)
            area_path: Update the area path
            iteration_path: Update the iteration path

        Returns:
            Success message with updated test case information
        """
        try:
            # Verify the test case exists first
            existing_item = client.get_work_item_by_id(test_case_id)
            if existing_item is None:
                return f"Test case with ID {test_case_id} not found"
            
            # Check if it's actually a test case
            work_item_type = existing_item.get("fields", {}).get("System.WorkItemType", "")
            if work_item_type != "Test Case":
                return f"Work item {test_case_id} is not a test case (it's a {work_item_type})"
            
            # Map parameters to Azure DevOps field names and collect non-None values
            field_mapping = {
                'title': ('System.Title', title),
                'state': ('System.State', state),
                'assigned_to': ('System.AssignedTo', assigned_to),
                'description': ('System.Description', description),
                'test_steps': ('Microsoft.VSTS.TCM.Steps', test_steps),
                'priority': ('Microsoft.VSTS.Common.Priority', priority),
                'automation_status': ('Microsoft.VSTS.TCM.AutomationStatus', automation_status),
                'tags': ('System.Tags', tags),
                'area_path': ('System.AreaPath', area_path),
                'iteration_path': ('System.IterationPath', iteration_path)
            }
            
            # Prepare updates dictionary with proper field names
            updates = {}
            for param_name, (field_name, value) in field_mapping.items():
                if value is not None:
                    updates[field_name] = value
            
            if not updates:
                return f"No fields provided for update. Please specify at least one field to update."
            
            # Update the test case
            updated_item = client.update_work_item(test_case_id, updates)
            
            # Parse the updated test case
            updated_test_case = parse_test_case(updated_item)
            
            return f"Successfully updated test case {test_case_id}:\n{updated_test_case.dict()}"
            
        except Exception as e:
            return f"Error updating test case {test_case_id}: {str(e)}"

    @mcp.tool()
    def create_test_case(
        title: str,
        description: Optional[str] = None,
        test_steps: Optional[str] = None,
        priority: Optional[int] = None,
        assigned_to: Optional[str] = None,
        area_path: Optional[str] = None,
        iteration_path: Optional[str] = None,
        automation_status: Optional[str] = None,
        tags: Optional[str] = None
    ) -> str:
        """
        Create a new test case in Azure DevOps

        Args:
            title: The title of the test case (required)
            description: Description of the test case
            test_steps: Test steps in HTML or plain text format
            priority: Priority level (1-4, where 1 is highest)
            assigned_to: Assign to a user (use display name or email)
            area_path: Area path for the test case
            iteration_path: Iteration path for the test case
            automation_status: Automation status ('Automated', 'Not Automated', 'Planned')
            tags: Tags (semicolon-separated string)

        Returns:
            Success message with created test case information
        """
        try:
            # Prepare fields for the new test case
            fields = {}
            
            if description is not None:
                fields["System.Description"] = description
            if test_steps is not None:
                fields["Microsoft.VSTS.TCM.Steps"] = test_steps
            if priority is not None:
                fields["Microsoft.VSTS.Common.Priority"] = priority
            if assigned_to is not None:
                fields["System.AssignedTo"] = assigned_to
            if area_path is not None:
                fields["System.AreaPath"] = area_path
            if iteration_path is not None:
                fields["System.IterationPath"] = iteration_path
            if automation_status is not None:
                fields["Microsoft.VSTS.TCM.AutomationStatus"] = automation_status
            if tags is not None:
                fields["System.Tags"] = tags
            
            # Set default state for new test cases
            fields["System.State"] = "Design"
            
            # Create the test case
            created_item = client.create_work_item("Test Case", title, fields)
            
            # Parse the created test case
            created_test_case = parse_test_case(created_item)
            
            return f"Successfully created test case {created_test_case.id}:\n{created_test_case.dict()}"
            
        except Exception as e:
            return f"Error creating test case: {str(e)}"