"""Tool for searching OWASP projects."""

from crewai.tools import tool

from apps.ai.agents.project.tools.formatters import format_project_results
from apps.owasp.index.search.project import get_projects


@tool("Search for OWASP projects by name, topic, technology, or description")
def search_projects(query: str, limit: int = 5) -> str:
    """Search for OWASP projects.

    Use this tool when users ask about:
    - Finding specific projects
    - Projects related to a topic
    - Projects using certain technologies
    - Searching for projects by name

    Args:
        query: Search query (name, topic, technology, or description)
        limit: Maximum number of results to return (default: 5)

    Returns:
        Formatted string with search results

    """
    results = get_projects(query, limit=limit)
    hits = results.get("hits", [])

    return format_project_results(hits)
