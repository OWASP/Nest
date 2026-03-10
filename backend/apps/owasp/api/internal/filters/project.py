"""Strawberry Django filter definitions for the Project model."""

import strawberry_django
from django.db.models import Q

from apps.owasp.models.enums.project import ProjectType
from apps.owasp.models.project import Project


@strawberry_django.filter_type(Project, lookups=True)
class ProjectFilter:
    """Strawberry filter type enabling category-based project queries."""

    @strawberry_django.filter_field
    def type(self, value: ProjectType, prefix: str):
        """Narrow results to a specific project category (code, tool, etc.)."""
        if not value:
            return Q()
        lookup = f"{prefix}type" if prefix else "type"
        return Q(**{lookup: value})
