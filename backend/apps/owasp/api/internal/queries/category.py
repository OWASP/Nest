"""OWASP project category GraphQL queries."""

import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginationInput

from apps.owasp.api.internal.nodes.category import ProjectCategoryNode
from apps.owasp.models.category import ProjectCategory

MAX_CATEGORIES_LIMIT = 1000
MAX_OFFSET = 10000


@strawberry.type
class CategoryQuery:
    """Project category queries."""

    @strawberry_django.field
    def project_categories(
        self,
        pagination: OffsetPaginationInput | None = None,
    ) -> list[ProjectCategoryNode]:
        """Resolve all active project categories with pagination.

        Args:
            pagination (OffsetPaginationInput, optional): Pagination parameters.

        Returns:
            list[ProjectCategoryNode]: List of active project categories.

        """
        queryset = ProjectCategory.objects.filter(is_active=True).order_by("name")

        if pagination:
            if pagination.offset < 0:
                return []
            pagination.offset = min(pagination.offset, MAX_OFFSET)

            if pagination.limit is not None and pagination.limit is not strawberry.UNSET:
                if pagination.limit <= 0:
                    return []
                pagination.limit = min(pagination.limit, MAX_CATEGORIES_LIMIT)

        return queryset
