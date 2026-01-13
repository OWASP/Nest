"""Tool for querying project creation dates and age."""

from datetime import datetime

from crewai.tools import tool
from django.utils import timezone

from apps.owasp.index.search.project import get_projects


def format_project_age_results(hits: list, project_name: str | None = None) -> str:
    """Format project age results for display.

    Args:
        hits: List of project hits from Algolia search
        project_name: Optional project name for single project queries

    Returns:
        Formatted string with project creation dates

    """
    if not hits:
        if project_name:
            return f"No project found with name '{project_name}'."
        return "No projects found."

    if project_name and len(hits) == 1:
        # Single project result
        project = hits[0]
        name = project.get("idx_name", "Unknown")
        created_at_timestamp = project.get("idx_created_at")

        if not created_at_timestamp:
            return f"*{name}*\n\nCreation date is not available for this project."

        # Convert timestamp to datetime
        created_at = datetime.fromtimestamp(created_at_timestamp, tz=timezone.utc)

        # Format date
        date_str = created_at.strftime("%B %d, %Y")
        age_days = (timezone.now() - created_at).days
        age_years = age_days // 365
        age_months = (age_days % 365) // 30

        age_str = f"{age_years} year{'s' if age_years != 1 else ''}" if age_years > 0 else ""
        if age_months > 0:
            if age_str:
                age_str += ", "
            age_str += f"{age_months} month{'s' if age_months != 1 else ''}"
        if not age_str:
            age_str = f"{age_days} day{'s' if age_days != 1 else ''}"

        return f"📅 *{name}*\n\n• *Creation Date*: {date_str}\n• *Age*: {age_str} old"

    # Multiple projects
    header = "📅 *OWASP Projects with Creation Dates:*\n\n"
    formatted = header

    for project in hits:
        name = project.get("idx_name", "Unknown")
        created_at_timestamp = project.get("idx_created_at")

        formatted += f"• *{name}*"
        if created_at_timestamp:
            created_at = datetime.fromtimestamp(created_at_timestamp, tz=timezone.utc)
            date_str = created_at.strftime("%B %d, %Y")
            formatted += f"\n  Created: {date_str}"
        else:
            formatted += "\n  Creation date: Not available"
        formatted += "\n\n"

    return formatted


@tool("Get project creation date or list all projects with their creation dates")
def get_project_age(project_name: str | None = None, limit: int = 50) -> str:
    """Get project creation date(s).

    This tool returns the creation date for a specific project by name,
    or lists all projects with their creation dates if no name is provided.

    Use this tool when users ask about:
    - When was a project created?
    - How old is a project?
    - Project creation dates
    - List all projects with their ages
    - Project addition dates

    Args:
        project_name: Optional project name to search for. If not provided,
            returns all projects with their creation dates.
        limit: Maximum number of projects to return when listing all
            (default: 50, only used when project_name is not provided)

    Returns:
        Formatted string with project creation date(s)

    """
    if project_name:
        # Search for specific project by name
        results = get_projects(
            project_name.strip(), attributes=["idx_name", "idx_created_at", "idx_url"], limit=10
        )
        hits = results.get("hits", [])
    else:
        # Get all active projects ordered by creation date
        results = get_projects(
            "", attributes=["idx_name", "idx_created_at", "idx_url"], limit=limit
        )
        hits = results.get("hits", [])
        # Sort by creation date descending (newest first)
        hits.sort(key=lambda x: x.get("idx_created_at", 0), reverse=True)

    return format_project_age_results(hits, project_name)
