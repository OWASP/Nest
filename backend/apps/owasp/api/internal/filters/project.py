"""Filters for OWASP Project."""

import strawberry_django
from django.db.models import Q

from apps.owasp.models.category import ProjectCategory
from apps.owasp.models.project import Project


@strawberry_django.filter_type(Project, lookups=True)
class ProjectFilter:
    """Filter for Project."""

    @strawberry_django.filter_field
    def categories(self, value: list[str], prefix: str):
        """Filter by project categories.

        When a category is specified, includes projects that have that category
        OR any of its nested subcategories.
        """
        if not value:
            return Q()

        category_q = Q()
        for category_slug in value:
            try:
                category = ProjectCategory.objects.get(slug=category_slug, is_active=True)
                category_ids = [category.id]
                category_ids.extend(
                    category.get_descendants().filter(is_active=True).values_list("id", flat=True)
                )
                category_q |= Q(categories__id__in=category_ids)
            except ProjectCategory.DoesNotExist:
                continue

        return category_q
