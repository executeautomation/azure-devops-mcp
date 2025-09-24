"""
Azure DevOps MCP Server - User Story Tools
"""

from typing import Optional
from fastmcp import FastMCP
from client import AzureDevOpsClient
from parsers import parse_work_item


def register_user_story_tools(mcp: FastMCP, client: AzureDevOpsClient):
    """Register all user story related tools with the MCP server"""
    
    @mcp.tool()
    def get_user_stories(limit: int = 50) -> str:
        """
        Retrieve user stories from Azure DevOps

        Args:
            limit: Maximum number of stories to retrieve (default: 50, max: 200)

        Returns:
            JSON string containing the user stories
        """
        try:
            # Validate limit
            limit = min(max(1, limit), 200)
            
            # Fetch work items
            work_items_data = client.get_work_items(work_item_type="User Story", top=limit)
            
            # Parse work items
            work_items = []
            for item_data in work_items_data:
                try:
                    work_item = parse_work_item(item_data)
                    work_items.append(work_item.dict())
                except Exception as e:
                    # Skip items that can't be parsed - don't print to stdout in MCP server
                    continue
            
            return f"Retrieved {len(work_items)} user stories:\n" + str(work_items)
            
        except Exception as e:
            return f"Error retrieving user stories: {str(e)}"

    @mcp.tool()
    def get_story_details(story_id: int) -> str:
        """
        Get detailed information for a specific user story

        Args:
            story_id: The ID of the user story to retrieve

        Returns:
            Detailed information about the story
        """
        try:
            # Fetch work item by ID
            work_item_data = client.get_work_item_by_id(story_id)
            
            if work_item_data is None:
                return f"Work item with ID {story_id} not found"
            
            # Parse work item
            work_item = parse_work_item(work_item_data)
            
            return f"Story Details:\n{work_item.dict()}"
            
        except Exception as e:
            return f"Error retrieving story details: {str(e)}"

    @mcp.tool()
    def search_stories_by_title(search_term: str, limit: int = 20) -> str:
        """
        Search for user stories by title

        Args:
            search_term: Term to search for in story titles
            limit: Maximum number of results to return (default: 20)

        Returns:
            List of matching stories
        """
        try:
            # Validate limit
            limit = min(max(1, limit), 100)
            
            # Search work items
            work_items_data = client.search_work_items_by_title(
                search_term=search_term,
                work_item_type="User Story",
                top=limit
            )
            
            # Parse work items
            work_items = []
            for item_data in work_items_data:
                try:
                    work_item = parse_work_item(item_data)
                    work_items.append(work_item.dict())
                except Exception as e:
                    # Skip items that can't be parsed - don't print to stdout in MCP server
                    continue
            
            return f"Found {len(work_items)} stories matching '{search_term}':\n" + str(work_items)
            
        except Exception as e:
            return f"Error searching stories: {str(e)}"

    @mcp.tool()
    def get_stories_by_state(state: str, limit: int = 50) -> str:
        """
        Get user stories filtered by state

        Args:
            state: State to filter by (e.g., 'New', 'Active', 'Resolved', 'Closed')
            limit: Maximum number of stories to retrieve (default: 50)

        Returns:
            List of stories in the specified state
        """
        try:
            # Validate limit
            limit = min(max(1, limit), 200)
            
            # Fetch work items by state
            work_items_data = client.get_work_items_by_state(
                state=state,
                work_item_type="User Story",
                top=limit
            )
            
            # Parse work items
            work_items = []
            for item_data in work_items_data:
                try:
                    work_item = parse_work_item(item_data)
                    work_items.append(work_item.dict())
                except Exception as e:
                    # Skip items that can't be parsed - don't print to stdout in MCP server
                    continue
            
            return f"Found {len(work_items)} stories in state '{state}':\n" + str(work_items)
            
        except Exception as e:
            return f"Error retrieving stories by state: {str(e)}"

    @mcp.tool()
    def update_story(
        story_id: int,
        title: Optional[str] = None,
        state: Optional[str] = None,
        assigned_to: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[int] = None,
        story_points: Optional[int] = None,
        tags: Optional[str] = None,
        area_path: Optional[str] = None,
        iteration_path: Optional[str] = None
    ) -> str:
        """
        Update a user story with new field values

        Args:
            story_id: The ID of the user story to update
            title: Update the story title
            state: Update the state (e.g., 'New', 'Active', 'Resolved', 'Closed')
            assigned_to: Assign to a user (use display name or email)
            description: Update the story description
            priority: Update the priority (1-4, where 1 is highest)
            story_points: Update story points
            tags: Update tags (semicolon-separated string)
            area_path: Update the area path
            iteration_path: Update the iteration path

        Returns:
            Success message with updated story information
        """
        try:
            # Verify the story exists first
            existing_item = client.get_work_item_by_id(story_id)
            if existing_item is None:
                return f"User story with ID {story_id} not found"
            
            # Check if it's actually a user story
            work_item_type = existing_item.get("fields", {}).get("System.WorkItemType", "")
            if work_item_type != "User Story":
                return f"Work item {story_id} is not a user story (it's a {work_item_type})"
            
            # Map parameters to Azure DevOps field names and collect non-None values
            field_mapping = {
                'title': ('System.Title', title),
                'state': ('System.State', state),
                'assigned_to': ('System.AssignedTo', assigned_to),
                'description': ('System.Description', description),
                'priority': ('Microsoft.VSTS.Common.Priority', priority),
                'story_points': ('Microsoft.VSTS.Scheduling.StoryPoints', story_points),
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
            
            # Update the user story
            updated_item = client.update_work_item(story_id, updates)
            
            # Parse the updated story
            updated_story = parse_work_item(updated_item)
            
            return f"Successfully updated user story {story_id}:\n{updated_story.dict()}"
            
        except Exception as e:
            return f"Error updating user story {story_id}: {str(e)}"

    @mcp.tool()
    def create_user_story(
        title: str,
        description: Optional[str] = None,
        priority: Optional[int] = None,
        story_points: Optional[int] = None,
        assigned_to: Optional[str] = None,
        area_path: Optional[str] = None,
        iteration_path: Optional[str] = None,
        tags: Optional[str] = None
    ) -> str:
        """
        Create a new user story in Azure DevOps

        Args:
            title: The title of the user story (required)
            description: Description of the user story
            priority: Priority level (1-4, where 1 is highest)
            story_points: Story points for estimation
            assigned_to: Assign to a user (use display name or email)
            area_path: Area path for the user story
            iteration_path: Iteration path for the user story
            tags: Tags (semicolon-separated string)

        Returns:
            Success message with created user story information
        """
        try:
            # Prepare fields for the new user story
            fields = {}
            
            if description is not None:
                fields["System.Description"] = description
            if priority is not None:
                fields["Microsoft.VSTS.Common.Priority"] = priority
            if story_points is not None:
                fields["Microsoft.VSTS.Scheduling.StoryPoints"] = story_points
            if assigned_to is not None:
                fields["System.AssignedTo"] = assigned_to
            if area_path is not None:
                fields["System.AreaPath"] = area_path
            if iteration_path is not None:
                fields["System.IterationPath"] = iteration_path
            if tags is not None:
                fields["System.Tags"] = tags
            
            # Set default state for new user stories
            fields["System.State"] = "New"
            
            # Create the user story
            created_item = client.create_work_item("User Story", title, fields)
            
            # Parse the created user story
            created_story = parse_work_item(created_item)
            
            return f"Successfully created user story {created_story.id}:\n{created_story.dict()}"
            
        except Exception as e:
            return f"Error creating user story: {str(e)}"