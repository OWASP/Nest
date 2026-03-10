"""Project Category API."""

from django.http import HttpRequest
from ninja import Schema
from ninja.decorators import decorate_view
from ninja.pagination import RouterPaginated

from apps.api.decorators.cache import cache_response
from apps.owasp.models.category import ProjectCategory

router = RouterPaginated(tags=["Categories"])


class ProjectCategorySchema(Schema):
    """Schema for ProjectCategory."""

    id: str
    name: str
    slug: str
    description: str
    level: int
    full_path: str
    is_active: bool

    @staticmethod
    def resolve_id(obj: ProjectCategory) -> str:
        """Resolve id as string."""
        return str(obj.id)


@router.get(
    "/",
    description="Retrieve all active project categories with hierarchy.",
    operation_id="list_categories",
    response=list[ProjectCategorySchema],
    summary="List project categories",
)
@decorate_view(cache_response())
def list_categories(
    request: HttpRequest,
) -> list[ProjectCategorySchema]:
    """Get all active categories with hierarchy information."""
    return ProjectCategory.objects.filter(is_active=True).order_by("name")
