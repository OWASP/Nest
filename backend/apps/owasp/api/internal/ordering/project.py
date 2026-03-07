"""OWASP Project Ordering."""

import strawberry
from strawberry_django import order_type

from apps.owasp.models.project import Project


@order_type(Project)
class ProjectOrder:
    """Ordering for Project."""

    contributors_count: strawberry.auto
    created_at: strawberry.auto
    forks_count: strawberry.auto
    level: strawberry.auto
    name: strawberry.auto
    stars_count: strawberry.auto
    updated_at: strawberry.auto
