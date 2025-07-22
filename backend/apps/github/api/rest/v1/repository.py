"""Repository API."""

from datetime import datetime

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


VALID_REPOSITORY_ORDERING_FIELDS = {"created_at", "updated_at"}


@router.get(
    "/",
    summary="Get all repositories",
    tags=["Repositories"],
    response={200: list[RepositorySchema]},
)
@decorate_view(cache_page(settings.API_CACHE_TIME_SECONDS))
@paginate(PageNumberPagination, page_size=settings.API_PAGE_SIZE)
def list_repository(
    request: HttpRequest,
    ordering: str | None = Query(None),
) -> list[RepositorySchema]:
    """
    Retrieves a paginated list of all repositories, optionally ordered by creation or update time.
    
    Parameters:
        ordering (str, optional): Field to order the repositories by. Must be either "created_at" or "updated_at" to take effect.
    
    Returns:
        list[RepositorySchema]: A paginated list of repositories serialized according to RepositorySchema.
    """
    repositories = Repository.objects.all()

    if ordering and ordering in VALID_REPOSITORY_ORDERING_FIELDS:
        repositories = repositories.order_by(ordering)
    return repositories
