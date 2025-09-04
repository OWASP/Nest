"""Repository API."""

from datetime import datetime
from typing import Literal

from django.conf import settings
from django.http import HttpRequest
from django.views.decorators.cache import cache_page
from ninja import Query, Router, Schema
from ninja.decorators import decorate_view
from ninja.pagination import PageNumberPagination, paginate

from apps.github.models.repository import Repository

router = Router()


class RepositorySchema(Schema):
    """Schema for Repository."""

    created_at: datetime
    description: str
    name: str
    updated_at: datetime


@router.get(
    "/",
    description="Retrieve a paginated list of GitHub repositories.",
    operation_id="list_repositories",
    summary="List repositories",
    tags=["github"],
    response={200: list[RepositorySchema]},
)
@decorate_view(cache_page(settings.API_CACHE_TIME_SECONDS))
@paginate(PageNumberPagination, page_size=settings.API_PAGE_SIZE)
def list_repository(
    request: HttpRequest,
    ordering: Literal["created_at", "-created_at", "updated_at", "-updated_at"] | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[RepositorySchema]:
    """Get all repositories."""
    repositories = Repository.objects.all()

    if ordering:
        repositories = repositories.order_by(ordering)
    return repositories
