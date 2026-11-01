"""Tool for getting production projects."""

from typing import Any

from crewai.tools import tool

from apps.ai.agents.project.tools.formatters import format_project_results
from apps.owasp.index.search.project import get_projects
from apps.owasp.models.enums.project import ProjectLevel


@tool("Get all OWASP production projects")
def get_production_projects(limit: int = 10) -> str:
    """Get all OWASP production projects.

    Production projects are mature, stable projects that are
    ready for production use.

    Use this tool when users ask about:
    - Production projects
    - Production-ready OWASP projects
    - Stable OWASP projects

    Args:
        limit: Maximum number of projects to return (default: 10)

    Returns:
        Formatted string with production projects information

    """
    results = get_projects("", limit=100)
    hits = results.get("hits", [])

    production = []
    for p in hits:
        level_value: Any = p.get("idx_level", "")
        if (
            isinstance(level_value, str) and level_value.lower() == ProjectLevel.PRODUCTION.lower()  # type: ignore[attr-defined]
        ):
            production.append(p)

    return format_project_results(production[:limit], "Production")
