"""Filters for OWASP Project Category."""

import strawberry_django
from django.db.models import Q

from apps.owasp.models.category import ProjectCategory


@strawberry_django.filter_type(ProjectCategory, lookups=True)
class ProjectCategoryFilter:
    """Filter for Project Category."""

    @strawberry_django.filter_field
    def is_active(self, value: bool, prefix: str):
        """Filter by active status."""
        return Q(is_active=value) if value is not None else Q()

    @strawberry_django.filter_field
    def level(self, value: int, prefix: str):
        """Filter by category level (1, 2, or 3)."""
        # This is a computed property, so we need to filter using parent relationships
        if value == 1:
            return Q(parent__isnull=True)
        elif value == 2:
            return Q(parent__isnull=False, parent__parent__isnull=True)
        elif value == 3:
            return Q(parent__parent__isnull=False)
        return Q()
