"""Project service for secure data access.

This module provides a security-first approach to exposing project data.
All public-facing data goes through ProjectPublicDTO which enforces
strict field allowlisting and XSS sanitization.
"""

from __future__ import annotations

import html
import logging

from pydantic import BaseModel, field_validator

logger = logging.getLogger(__name__)


class ProjectPublicDTO(BaseModel):
    """Public-safe representation of a project.

    Security: Only exposes name, url, description, and maintainers.
    All string fields are HTML-escaped to prevent XSS when rendered
    in LLM context or web responses.
    """

    name: str
    url: str | None
    description: str | None
    maintainers: list[str]

    @field_validator("name", "url", "description", mode="before")
    @classmethod
    def _escape_html(cls, val: str | None) -> str | None:
        # Security: Prevent XSS via HTML entity escaping (OWASP LLM01)
        return html.escape(str(val)) if val else val

    @field_validator("maintainers", mode="before")
    @classmethod
    def _escape_maintainer_list(cls, val: list | None) -> list[str]:
        if not val:
            return []
        return [html.escape(str(m)) for m in val if m]


class ProjectService:
    """Handles project lookups with security guarantees."""

    def get_project_details(self, project_key: str) -> ProjectPublicDTO | None:
        """Look up a project and return its public-safe representation.

        Args:
            project_key: The project's unique key (e.g., "www-project-zap").

        Returns:
            A sanitized DTO if the project exists and is active, else None.

        """
        # Defer import to avoid circular deps at module level
        from apps.owasp.models.project import Project

        try:
            return self._fetch_project(key=project_key)
        except Project.DoesNotExist:
            logger.debug("Project lookup miss by key: %s", project_key)

        # Fallback: Try fuzzy match on name
        try:
            return self._fetch_project(name__iexact=project_key)
        except Project.DoesNotExist:
            logger.debug("Project lookup miss by name: %s", project_key)
            return None

    def _fetch_project(self, **kwargs) -> ProjectPublicDTO:
        """Fetch and convert a project instance."""
        from apps.owasp.models.project import Project

        project = Project.objects.get(is_active=True, **kwargs)

        # Extract maintainer names
        maintainer_names = []
        for leader in project.entity_leaders:
            name = getattr(leader, "name", None) or getattr(leader, "login", None)
            if name:
                maintainer_names.append(name)

        return ProjectPublicDTO(
            name=project.name or "",
            url=project.url,
            description=project.description,
            maintainers=maintainer_names,
        )

    def search_projects(self, query: str, limit: int = 10) -> list[ProjectPublicDTO]:
        """Search for projects matching a query.

        Args:
            query: Search term to match against project names.
            limit: Maximum results to return.

        Returns:
            List of matching project DTOs.

        """
        from apps.owasp.models.project import Project

        projects = Project.objects.filter(name__icontains=query, is_active=True).order_by(
            "-stars_count"
        )[:limit]

        results = []
        for project in projects:
            maintainer_names = []
            for leader in project.entity_leaders:
                name = getattr(leader, "name", None) or getattr(leader, "login", None)
                if name:
                    maintainer_names.append(name)

            results.append(
                ProjectPublicDTO(
                    name=project.name or "",
                    url=project.url,
                    description=project.description,
                    maintainers=maintainer_names,
                )
            )
        return results
