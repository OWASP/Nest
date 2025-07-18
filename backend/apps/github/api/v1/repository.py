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


@router.get("/", response={200: list[RepositorySchema]})
@decorate_view(cache_page(settings.API_CACHE_TIME))
@paginate(PageNumberPagination, page_size=settings.API_PAGE_SIZE)
def list_repository(
    request: HttpRequest,
    ordering: str | None = Query(None),
) -> list[RepositorySchema]:
    """Get all repositories."""
    repositories = Repository.objects.all()

    if ordering and ordering in VALID_REPOSITORY_ORDERING_FIELDS:
        repositories = repositories.order_by(ordering)
    return repositories
