"""Tool for getting incubator projects."""

from typing import Any

from crewai.tools import tool

from apps.ai.agents.project.tools.formatters import format_project_results
from apps.owasp.index.search.project import get_projects
from apps.owasp.models.enums.project import ProjectLevel


@tool("Get all OWASP incubator projects")
def get_incubator_projects(limit: int = 10) -> str:
    """Get all OWASP incubator projects.

    Incubator projects are early-stage projects that are
    being developed and refined.

    Use this tool when users ask about:
    - Incubator projects
    - New OWASP projects
    - Early-stage projects

    Args:
        limit: Maximum number of projects to return (default: 10)

    Returns:
        Formatted string with incubator projects information

    """
    results = get_projects("", limit=100)
    hits = results.get("hits", [])

    incubator = []
    for p in hits:
        level_value: Any = p.get("idx_level", "")
        if (
            isinstance(level_value, str) and level_value.lower() == ProjectLevel.INCUBATOR.lower()  # type: ignore[attr-defined]
        ):
            incubator.append(p)

    return format_project_results(incubator[:limit], "Incubator")
