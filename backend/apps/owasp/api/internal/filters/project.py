"""Filters for OWASP Project."""

import strawberry
import strawberry_django
from django.db.models import Q

from apps.owasp.models.enums.project import ProjectType
from apps.owasp.models.project import Project


@strawberry_django.filter_type(Project, lookups=True)
class ProjectFilter:
    """Filter for Project."""

    @strawberry_django.filter_field
    def type(self, value: ProjectType, prefix: str):
        """Filter by project type (category)."""
        return Q(type=ProjectType(value)) if value else Q()
