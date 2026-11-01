"""Tool for getting lab projects."""

from typing import Any

from crewai.tools import tool

from apps.ai.agents.project.tools.formatters import format_project_results
from apps.owasp.index.search.project import get_projects
from apps.owasp.models.enums.project import ProjectLevel


@tool("Get all OWASP lab projects")
def get_lab_projects(limit: int = 10) -> str:
    """Get all OWASP lab projects.

    Lab projects are experimental projects that are being
    actively developed and tested.

    Use this tool when users ask about:
    - Lab projects
    - Experimental OWASP projects
    - Projects in development

    Args:
        limit: Maximum number of projects to return (default: 10)

    Returns:
        Formatted string with lab projects information

    """
    results = get_projects("", limit=100)
    hits = results.get("hits", [])

    lab = []
    for p in hits:
        level_value: Any = p.get("idx_level", "")
        if isinstance(level_value, str) and level_value.lower() == ProjectLevel.LAB.lower():  # type: ignore[attr-defined]
            lab.append(p)

    return format_project_results(lab[:limit], "Lab")
