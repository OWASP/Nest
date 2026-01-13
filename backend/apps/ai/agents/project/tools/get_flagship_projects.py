"""Tool for getting flagship projects."""

from typing import Any

from crewai.tools import tool

from apps.ai.agents.project.tools.formatters import format_project_results
from apps.owasp.index.search.project import get_projects
from apps.owasp.models.enums.project import ProjectLevel


@tool("Get all OWASP flagship projects")
def get_flagship_projects(limit: int = 10) -> str:
    """Get all OWASP flagship projects.

    Flagship projects are the highest maturity level in OWASP,
    representing production-ready, well-maintained projects.

    Use this tool when users ask about:
    - Flagship projects
    - Top OWASP projects
    - Main OWASP projects
    - Best OWASP projects

    Args:
        limit: Maximum number of projects to return (default: 10)

    Returns:
        Formatted string with flagship projects information

    """
    # Get all projects and filter by flagship level
    results = get_projects("", limit=100)  # Get more to filter
    hits = results.get("hits", [])

    flagship = []
    for p in hits:
        level_value: Any = p.get("idx_level", "")
        if (
            isinstance(level_value, str) and level_value.lower() == ProjectLevel.FLAGSHIP.lower()  # type: ignore[attr-defined]
        ):
            flagship.append(p)

    return format_project_results(flagship[:limit], "Flagship")
