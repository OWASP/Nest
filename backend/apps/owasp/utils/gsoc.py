"""GSoC utility functions for OWASP projects."""

from functools import lru_cache


@lru_cache
def get_gsoc_projects(year: int) -> list[dict[str, str]]:
    """Get OWASP projects that participated in Google Summer of Code for a specific year.

    Args:
        year: The GSoC year (e.g., 2024, 2025)

    Returns:
        List of dictionaries with project information:
        - name: Project name
        - url: Project URL

    """
    from apps.owasp.models.project import Project

    projects = (
        Project.objects.filter(
            is_active=True,
            custom_tags__isnull=False,
            custom_tags__icontains=f"gsoc{year}",
        )
        .only("name", "key")
        .order_by("name")
    )

    return [
        {
            "name": project.name or project.key.replace("www-project-", ""),
            "url": project.owasp_url or "",
        }
        for project in projects
    ]
