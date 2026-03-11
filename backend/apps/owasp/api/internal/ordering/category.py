"""OWASP Project Category Ordering."""

import strawberry
from strawberry_django import order_type

from apps.owasp.models.category import ProjectCategory


@order_type(ProjectCategory)
class ProjectCategoryOrder:
    """Ordering for Project Category."""

    nest_created_at: strawberry.auto
    name: strawberry.auto
    nest_updated_at: strawberry.auto
