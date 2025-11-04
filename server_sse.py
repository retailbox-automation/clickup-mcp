"""
ClickUp MCP Server with HTTP Stream Transport

A Model Context Protocol server with HTTP Stream transport for remote deployment.
Designed to work with Web Claude and can be deployed on platforms like Zeabur.

Endpoint: /mcp
"""

import os
from typing import Any, Optional
from urllib.parse import urljoin

import httpx
from fastmcp import FastMCP
from pydantic import BaseModel, Field, ConfigDict


# Constants
API_BASE_URL = "https://api.clickup.com/api/v2"
CHARACTER_LIMIT = 25000


# Initialize FastMCP server
mcp = FastMCP("clickup-mcp-server")


# API Client Helper Functions
def get_api_key() -> str:
    """Get ClickUp API key from environment variable."""
    api_key = os.getenv("CLICKUP_API_KEY")
    if not api_key:
        raise ValueError(
            "CLICKUP_API_KEY environment variable is not set. "
            "Please set your ClickUp Personal API Token: "
            "export CLICKUP_API_KEY='your_token_here'"
        )
    return api_key


async def make_api_request(
    endpoint: str,
    method: str = "GET",
    params: Optional[dict] = None,
    json_data: Optional[dict] = None
) -> dict[str, Any]:
    """
    Make an authenticated request to the ClickUp API.

    Args:
        endpoint: API endpoint (e.g., '/team')
        method: HTTP method (GET, POST, etc.)
        params: Query parameters
        json_data: JSON body for POST/PUT requests

    Returns:
        JSON response from the API

    Raises:
        ValueError: For authentication or validation errors
        httpx.HTTPStatusError: For other HTTP errors
    """
    api_key = get_api_key()
    url = urljoin(API_BASE_URL + "/", endpoint.lstrip("/"))

    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ValueError(
                    "Authentication failed. Please check your CLICKUP_API_KEY. "
                    "You can generate a new token at: "
                    "https://app.clickup.com/settings/apps"
                )
            elif e.response.status_code == 404:
                raise ValueError(
                    f"Resource not found: {endpoint}. "
                    "Please verify the ID is correct and you have access to this resource."
                )
            elif e.response.status_code == 403:
                raise ValueError(
                    f"Access denied to {endpoint}. "
                    "Please check your permissions for this resource."
                )
            elif e.response.status_code == 429:
                raise ValueError(
                    "Rate limit exceeded. Please wait a moment and try again. "
                    "ClickUp API has rate limits to protect service quality."
                )
            else:
                raise ValueError(
                    f"ClickUp API error ({e.response.status_code}): {e.response.text}"
                )


def truncate_if_needed(text: str, limit: int = CHARACTER_LIMIT) -> str:
    """Truncate text if it exceeds the character limit."""
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n\n... (truncated, {len(text) - limit} characters omitted)"


def format_spaces_response(spaces: list[dict]) -> str:
    """Format spaces data into a readable markdown response."""
    if not spaces:
        return "No spaces found in this workspace."

    output = f"# Spaces ({len(spaces)} total)\n\n"

    for space in spaces:
        output += f"## {space.get('name', 'Unnamed Space')}\n"
        output += f"- **ID**: `{space.get('id')}`\n"
        output += f"- **Private**: {space.get('private', False)}\n"
        output += f"- **Archived**: {space.get('archived', False)}\n"

        if 'statuses' in space:
            statuses = space['statuses']
            output += f"- **Statuses**: {len(statuses)} status(es)\n"

        if 'features' in space:
            features = space['features']
            due_dates = features.get('due_dates', {})
            output += f"- **Due Dates Enabled**: {due_dates.get('enabled', False)}\n"

        output += "\n"

    return truncate_if_needed(output)


def format_space_details(space: dict) -> str:
    """Format detailed space information into markdown."""
    output = f"# Space: {space.get('name', 'Unnamed')}\n\n"
    output += f"**ID**: `{space.get('id')}`\n"
    output += f"**Private**: {space.get('private', False)}\n"
    output += f"**Archived**: {space.get('archived', False)}\n\n"

    # Statuses
    if 'statuses' in space:
        output += "## Statuses\n\n"
        for status in space['statuses']:
            status_name = status.get('status', 'Unknown')
            status_type = status.get('type', '')
            color = status.get('color', '')
            output += f"- **{status_name}** (Type: {status_type}, Color: {color})\n"
        output += "\n"

    # Folders
    if 'folders' in space:
        folders = space['folders']
        output += f"## Folders ({len(folders)} total)\n\n"
        for folder in folders:
            output += f"### {folder.get('name', 'Unnamed Folder')}\n"
            output += f"- **ID**: `{folder.get('id')}`\n"
            output += f"- **Hidden**: {folder.get('hidden', False)}\n"

            if 'lists' in folder:
                lists = folder['lists']
                output += f"- **Lists**: {len(lists)}\n"
                for lst in lists:
                    output += f"  - {lst.get('name')} (ID: `{lst.get('id')}`)\n"
            output += "\n"

    # Lists (folderless)
    if 'lists' in space:
        lists = space['lists']
        output += f"## Lists ({len(lists)} folderless)\n\n"
        for lst in lists:
            output += f"- **{lst.get('name', 'Unnamed List')}** (ID: `{lst.get('id')}`)\n"

    return truncate_if_needed(output)


def format_custom_fields(fields: list[dict]) -> str:
    """Format custom fields into readable markdown."""
    if not fields:
        return "No custom fields found for this list."

    output = f"# Custom Fields ({len(fields)} total)\n\n"

    for field in fields:
        output += f"## {field.get('name', 'Unnamed Field')}\n"
        output += f"- **ID**: `{field.get('id')}`\n"
        output += f"- **Type**: {field.get('type', 'unknown')}\n"
        output += f"- **Required**: {field.get('required', False)}\n"
        output += f"- **Hidden from guests**: {field.get('hide_from_guests', False)}\n"

        # Type-specific configuration
        type_config = field.get('type_config', {})
        if type_config:
            output += "- **Configuration**:\n"
            for key, value in type_config.items():
                output += f"  - {key}: {value}\n"

        output += "\n"

    return truncate_if_needed(output)


# MCP Tools
@mcp.tool()
async def get_authorized_user() -> str:
    """
    Get information about the currently authenticated ClickUp user.

    This tool returns the user's profile information including name, email,
    workspace memberships, and account details.

    Use this tool to:
    - Verify authentication is working correctly
    - Get the user's team (workspace) IDs for other operations
    - Understand what workspaces the user has access to

    Returns:
        Markdown formatted user information including workspaces

    Example usage:
        - "Show me my ClickUp profile"
        - "What workspaces do I have access to?"
        - "Get my team IDs"
    """
    try:
        data = await make_api_request("/user")
        user = data.get("user", {})

        output = f"# ClickUp User Profile\n\n"
        output += f"**Name**: {user.get('username', 'N/A')}\n"
        output += f"**Email**: {user.get('email', 'N/A')}\n"
        output += f"**ID**: `{user.get('id')}`\n"
        output += f"**Color**: {user.get('color', 'N/A')}\n\n"

        # Workspaces (teams)
        teams = data.get("user", {}).get("teams", [])
        if teams:
            output += f"## Workspaces ({len(teams)} total)\n\n"
            for team in teams:
                output += f"### {team.get('name', 'Unnamed Workspace')}\n"
                output += f"- **ID**: `{team.get('id')}` (use this for get_spaces)\n"
                output += f"- **Color**: {team.get('color', 'N/A')}\n"
                output += f"- **Avatar**: {team.get('avatar', 'None')}\n\n"

        return truncate_if_needed(output)

    except Exception as e:
        return f"Error getting user information: {str(e)}"


@mcp.tool()
async def get_spaces(team_id: str, archived: bool = False) -> str:
    """
    Get all spaces in a ClickUp workspace (team).

    Spaces are the top-level organizational containers in ClickUp, containing
    folders, lists, and tasks. This tool returns an overview of all spaces
    with their basic information and status configuration.

    Args:
        team_id: The workspace (team) ID. Get this from get_authorized_user tool.
                 Example: "9012345678"
        archived: Include archived spaces in results. Default: false

    Returns:
        Markdown formatted list of spaces with their IDs and key properties

    Use this tool to:
    - Discover what spaces exist in a workspace
    - Get space IDs for further exploration
    - See space status configurations

    Example usage:
        - "List all spaces in workspace 9012345678"
        - "Show me the spaces including archived ones"
        - "What spaces are in my workspace?"
    """
    try:
        params = {"archived": str(archived).lower()}
        data = await make_api_request(f"/team/{team_id}/space", params=params)
        spaces = data.get("spaces", [])

        return format_spaces_response(spaces)

    except Exception as e:
        return f"Error getting spaces: {str(e)}"


@mcp.tool()
async def get_space_details(space_id: str) -> str:
    """
    Get detailed information about a specific ClickUp space.

    This tool returns comprehensive information about a space including:
    - Basic space properties (name, privacy, archived status)
    - All status configurations
    - Folder structure with nested lists
    - Folderless lists

    Args:
        space_id: The space ID. Get this from get_spaces tool.
                  Example: "90120012345"

    Returns:
        Markdown formatted detailed space information including folders and lists

    Use this tool to:
    - Explore the structure of a specific space
    - Find list IDs for getting custom fields
    - Understand the organizational hierarchy
    - See all available statuses in the space

    Example usage:
        - "Show me details for space 90120012345"
        - "What folders and lists are in this space?"
        - "Get the structure of space X"
    """
    try:
        data = await make_api_request(f"/space/{space_id}")

        return format_space_details(data)

    except Exception as e:
        return f"Error getting space details: {str(e)}"


@mcp.tool()
async def get_list_custom_fields(list_id: str) -> str:
    """
    Get all custom fields (columns) configured for a specific list.

    Custom fields are the columns you see in ClickUp lists. They can be various
    types like text, number, dropdown, date, etc. This tool shows all custom
    fields available on a list with their configuration.

    Args:
        list_id: The list ID. Get this from get_space_details tool.
                 Example: "901200567890"

    Returns:
        Markdown formatted list of custom fields with types and configuration

    Supported field types include:
    - text, short_text (text inputs)
    - number, currency (numeric values)
    - drop_down, labels (selection fields)
    - date (date picker)
    - checkbox (boolean)
    - email, phone, url (formatted text)
    - users, tasks (relationship fields)
    - And more...

    Use this tool to:
    - Discover what custom fields are available on a list
    - Understand field types and configurations
    - See field IDs for task operations
    - Check if fields are required or hidden from guests

    Example usage:
        - "What custom fields are on list 901200567890?"
        - "Show me the columns for this list"
        - "Get custom field configuration for list X"
    """
    try:
        data = await make_api_request(f"/list/{list_id}/field")
        fields = data.get("fields", [])

        return format_custom_fields(fields)

    except Exception as e:
        return f"Error getting custom fields: {str(e)}"


@mcp.tool()
async def get_folderless_lists(space_id: str, archived: bool = False) -> str:
    """
    Get all lists that are not inside folders in a space.

    In ClickUp, lists can exist directly in a space without being inside a folder.
    This tool returns those "folderless" lists with their basic information.

    Args:
        space_id: The space ID. Get this from get_spaces tool.
                  Example: "90120012345"
        archived: Include archived lists in results. Default: false

    Returns:
        Markdown formatted list of folderless lists with their IDs

    Use this tool to:
    - Find lists at the space level
    - Get list IDs for viewing custom fields
    - Discover lists not organized in folders

    Example usage:
        - "Show folderless lists in space 90120012345"
        - "What lists are directly in this space?"
        - "Get lists not in any folder"
    """
    try:
        params = {"archived": str(archived).lower()}
        data = await make_api_request(f"/space/{space_id}/list", params=params)
        lists = data.get("lists", [])

        if not lists:
            return "No folderless lists found in this space."

        output = f"# Folderless Lists ({len(lists)} total)\n\n"

        for lst in lists:
            output += f"## {lst.get('name', 'Unnamed List')}\n"
            output += f"- **ID**: `{lst.get('id')}` (use with get_list_custom_fields)\n"
            output += f"- **Archived**: {lst.get('archived', False)}\n"
            output += f"- **Task Count**: {lst.get('task_count', 0)}\n"

            if 'status' in lst:
                status = lst['status']
                output += f"- **Status**: {status.get('status', 'N/A')}\n"

            output += "\n"

        return truncate_if_needed(output)

    except Exception as e:
        return f"Error getting folderless lists: {str(e)}"


@mcp.tool()
async def get_folders(space_id: str, archived: bool = False) -> str:
    """
    Get all folders in a ClickUp space with their lists.

    This is the KEY tool for auditing workspace structure. Returns complete
    folder hierarchy with all lists, task counts, and IDs needed for deeper analysis.

    Args:
        space_id: The space ID. Get this from get_spaces tool.
                  Example: "90120012345"
        archived: Include archived folders. Default: false

    Returns:
        Markdown formatted folder structure with lists and task counts

    Use this tool to:
    - Audit complete workspace structure
    - Find all lists organized in folders
    - Get list IDs for custom field analysis
    - See task distribution across lists
    - Identify organizational patterns

    Example usage:
        - "Show me all folders in space X"
        - "Audit the structure of Austin's workspace"
        - "What lists exist in this space?"
    """
    try:
        params = {"archived": str(archived).lower()}
        data = await make_api_request(f"/space/{space_id}/folder", params=params)
        folders = data.get("folders", [])

        if not folders:
            return "No folders found in this space."

        output = f"# Folders ({len(folders)} total)\n\n"

        total_lists = 0
        total_tasks = 0

        for folder in folders:
            folder_name = folder.get('name', 'Unnamed Folder')
            folder_id = folder.get('id')
            hidden = folder.get('hidden', False)

            output += f"## 📁 {folder_name}\n"
            output += f"- **Folder ID**: `{folder_id}`\n"
            output += f"- **Hidden**: {hidden}\n"

            lists = folder.get('lists', [])
            if lists:
                output += f"- **Lists**: {len(lists)}\n\n"
                for lst in lists:
                    list_name = lst.get('name', 'Unnamed List')
                    list_id = lst.get('id')
                    task_count = lst.get('task_count', 0)

                    total_lists += 1
                    total_tasks += task_count

                    output += f"   📋 **{list_name}**\n"
                    output += f"      - List ID: `{list_id}`\n"
                    output += f"      - Tasks: {task_count}\n"
                    output += f"      - Archived: {lst.get('archived', False)}\n"

                    if 'folder' in lst:
                        output += f"      - Folder: {lst['folder'].get('name', 'N/A')}\n"
                    output += "\n"
            else:
                output += "- **Lists**: None\n\n"

        output += f"\n---\n**Summary**: {len(folders)} folders, {total_lists} lists, {total_tasks} total tasks\n"

        return truncate_if_needed(output)

    except Exception as e:
        return f"Error getting folders: {str(e)}"


@mcp.tool()
async def get_list_details(list_id: str) -> str:
    """
    Get detailed information about a specific list including all custom fields.

    This tool provides comprehensive list analysis including structure, fields,
    statuses, and configuration - essential for workflow audit.

    Args:
        list_id: The list ID. Get this from get_folders or get_space_details.
                 Example: "901200567890"

    Returns:
        Markdown formatted detailed list information with custom fields

    Use this tool to:
    - Audit list configuration and custom fields
    - Understand data structure for each list
    - See available statuses and priorities
    - Check assignees and permissions
    - Prepare for automation recommendations

    Example usage:
        - "Show me details for Lead Tracker list"
        - "What fields are in list 901111375515?"
        - "Audit the structure of this list"
    """
    try:
        data = await make_api_request(f"/list/{list_id}")

        output = f"# List: {data.get('name', 'Unnamed')}\n\n"
        output += f"**ID**: `{data.get('id')}`\n"
        output += f"**Archived**: {data.get('archived', False)}\n"
        output += f"**Task Count**: {data.get('task_count', 0)}\n"

        # Folder context
        if 'folder' in data:
            folder = data['folder']
            output += f"**Folder**: {folder.get('name')} (ID: `{folder.get('id')}`)\n"

        # Space context
        if 'space' in data:
            space = data['space']
            output += f"**Space**: {space.get('name')} (ID: `{space.get('id')}`)\n"

        output += "\n"

        # Statuses
        if 'statuses' in data:
            statuses = data['statuses']
            output += f"## Statuses ({len(statuses)} total)\n\n"
            for status in statuses:
                status_name = status.get('status', 'Unknown')
                status_type = status.get('type', 'N/A')
                color = status.get('color', 'N/A')
                output += f"- **{status_name}** (Type: {status_type}, Color: {color})\n"
            output += "\n"

        # Priority
        if 'priority' in data:
            priority = data['priority']
            if priority:
                output += f"## Priority\n\n"
                output += f"**Enabled**: {priority.get('enabled', False)}\n"
                if 'priorities' in priority:
                    for p in priority['priorities']:
                        output += f"- {p.get('priority')} (Color: {p.get('color')})\n"
                output += "\n"

        # Due dates
        if 'due_date_time' in data:
            output += f"**Due Dates**: {data.get('due_date_time', False)}\n"

        # Assignees
        if 'assignees' in data:
            assignees = data['assignees']
            if assignees:
                output += f"\n## Assignees ({len(assignees)} total)\n\n"
                for assignee in assignees:
                    output += f"- {assignee.get('username', 'N/A')} (ID: {assignee.get('id')})\n"
                output += "\n"

        # Get custom fields for this list
        try:
            fields_data = await make_api_request(f"/list/{list_id}/field")
            fields = fields_data.get("fields", [])

            if fields:
                output += f"## Custom Fields ({len(fields)} total)\n\n"
                for field in fields:
                    output += f"### {field.get('name', 'Unnamed')}\n"
                    output += f"- **ID**: `{field.get('id')}`\n"
                    output += f"- **Type**: {field.get('type', 'unknown')}\n"
                    output += f"- **Required**: {field.get('required', False)}\n"

                    # Type-specific config
                    type_config = field.get('type_config', {})
                    if type_config:
                        output += "- **Config**:\n"
                        for key, value in list(type_config.items())[:5]:  # Limit config details
                            output += f"  - {key}: {value}\n"
                    output += "\n"
        except Exception:
            output += "\n*Custom fields: Unable to retrieve*\n"

        return truncate_if_needed(output)

    except Exception as e:
        return f"Error getting list details: {str(e)}"


@mcp.tool()
async def get_tasks(list_id: str, page: int = 0, limit: int = 10) -> str:
    """
    Get sample tasks from a list to understand data structure and usage patterns.

    Use this to see real examples of how the list is being used, what data
    is being tracked, and how custom fields are filled out.

    Args:
        list_id: The list ID. Get from get_folders or get_list_details.
                 Example: "901200567890"
        page: Page number for pagination (0-indexed). Default: 0
        limit: Number of tasks to return (1-100). Default: 10

    Returns:
        Markdown formatted task information with custom field values

    Use this tool to:
    - See real data examples from lists
    - Understand how custom fields are used
    - Analyze data quality and completeness
    - Identify patterns for automation
    - Get insights for recommendations

    Example usage:
        - "Show me sample tasks from Lead Tracker"
        - "What data is in the first 5 tasks of this list?"
        - "Analyze task structure in list X"
    """
    try:
        params = {
            "page": page,
            "order_by": "created",
            "reverse": "true",
            "subtasks": "false",
            "include_closed": "true"
        }

        data = await make_api_request(f"/list/{list_id}/task", params=params)
        tasks = data.get("tasks", [])

        if not tasks:
            return f"No tasks found in list {list_id}"

        # Get list info for context
        list_data = await make_api_request(f"/list/{list_id}")
        list_name = list_data.get('name', 'Unknown List')

        output = f"# Tasks from: {list_name}\n\n"
        output += f"**Showing {min(limit, len(tasks))} of {len(tasks)} tasks**\n\n"

        for i, task in enumerate(tasks[:limit], 1):
            task_name = task.get('name', 'Unnamed Task')
            task_id = task.get('id')
            status = task.get('status', {}).get('status', 'No Status')

            output += f"## {i}. {task_name}\n"
            output += f"- **Task ID**: `{task_id}`\n"
            output += f"- **Status**: {status}\n"
            output += f"- **Created**: {task.get('date_created', 'N/A')}\n"

            # Priority
            if 'priority' in task and task['priority']:
                priority = task['priority']
                output += f"- **Priority**: {priority.get('priority', 'N/A')}\n"

            # Due date
            if 'due_date' in task and task['due_date']:
                output += f"- **Due Date**: {task['due_date']}\n"

            # Assignees
            assignees = task.get('assignees', [])
            if assignees:
                assignee_names = [a.get('username', 'N/A') for a in assignees[:3]]
                output += f"- **Assignees**: {', '.join(assignee_names)}\n"

            # Custom fields with values
            custom_fields = task.get('custom_fields', [])
            if custom_fields:
                output += "- **Custom Fields**:\n"
                for field in custom_fields[:5]:  # Limit to 5 fields per task
                    field_name = field.get('name', 'Unknown')
                    field_value = field.get('value', 'Empty')

                    # Format value based on type
                    if isinstance(field_value, dict):
                        field_value = str(field_value)[:50]
                    elif isinstance(field_value, list):
                        field_value = f"[{len(field_value)} items]"

                    output += f"  - {field_name}: {field_value}\n"

            # Description preview
            if 'description' in task and task['description']:
                desc = task['description'][:100].replace('\n', ' ')
                output += f"- **Description**: {desc}...\n"

            output += "\n"

        return truncate_if_needed(output)

    except Exception as e:
        return f"Error getting tasks: {str(e)}"


@mcp.tool()
async def get_views(space_id: str) -> str:
    """
    Get all views (including dashboards) in a space.

    Views include Board, List, Calendar, Gantt, and Dashboard views.
    This helps understand how the client visualizes and organizes their data.

    Args:
        space_id: The space ID. Get from get_spaces tool.
                  Example: "90120012345"

    Returns:
        Markdown formatted list of views with their types and configurations

    Use this tool to:
    - Discover existing dashboards and views
    - Understand data visualization preferences
    - Identify reporting patterns
    - Plan dashboard improvements

    Example usage:
        - "What views exist in this space?"
        - "Show me the dashboards"
        - "List all views in Austin's workspace"
    """
    try:
        data = await make_api_request(f"/space/{space_id}/view")
        views = data.get("views", [])

        if not views:
            return "No views found in this space."

        output = f"# Views ({len(views)} total)\n\n"

        # Group by type
        view_types = {}
        for view in views:
            view_type = view.get('type', 'unknown')
            if view_type not in view_types:
                view_types[view_type] = []
            view_types[view_type].append(view)

        for view_type, type_views in view_types.items():
            output += f"## {view_type.title()} Views ({len(type_views)})\n\n"

            for view in type_views:
                view_name = view.get('name', 'Unnamed View')
                view_id = view.get('id')

                output += f"### {view_name}\n"
                output += f"- **View ID**: `{view_id}`\n"
                output += f"- **Type**: {view_type}\n"

                # Protected/private
                if 'protected' in view:
                    output += f"- **Protected**: {view.get('protected', False)}\n"

                # Parent info
                if 'parent' in view:
                    parent = view['parent']
                    output += f"- **Parent**: {parent.get('name', 'N/A')} (ID: {parent.get('id')})\n"

                # Settings preview
                if 'settings' in view and view['settings']:
                    output += f"- **Configured**: Yes\n"

                output += "\n"

        return truncate_if_needed(output)

    except Exception as e:
        return f"Error getting views: {str(e)}"


# Run with HTTP Stream transport (SSE is deprecated since 2025-03-26)
if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))

    # FastMCP with streamable-http transport (recommended for 2025)
    # Endpoint will be available at: http://host:port/mcp
    mcp.run(transport="streamable-http", port=port, host="0.0.0.0")
