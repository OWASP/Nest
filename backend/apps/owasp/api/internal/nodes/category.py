"""OWASP project category GraphQL node."""

import strawberry
import strawberry_django

from apps.owasp.models.category import ProjectCategory


@strawberry_django.type(
    ProjectCategory,
    fields=[
        "id",
        "name",
        "slug",
        "description",
        "is_active",
        "nest_created_at",
        "nest_updated_at",
    ],
)
class ProjectCategoryNode:
    """Project category node."""

    @strawberry_django.field
    def full_path(self, root: ProjectCategory) -> str:
        """Resolve full hierarchical path of the category."""
        return root.full_path

    @strawberry_django.field
    def level(self, root: ProjectCategory) -> int:
        """Resolve nesting level of the category."""
        return root.level

    @strawberry_django.field(
        prefetch_related=["parent"],
        description="Parent category if this is a subcategory",
    )
    def parent(self, root: ProjectCategory) -> "ProjectCategoryNode | None":
        """Resolve parent category if it exists."""
        return root.parent

    @strawberry_django.field(
        prefetch_related=["children"],
        description="Direct child categories",
    )
    def children(self, root: ProjectCategory) -> list["ProjectCategoryNode"]:
        """Resolve direct child categories."""
        return list(root.children.filter(is_active=True))
