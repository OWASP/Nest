"""Repository API."""

from datetime import datetime

from django.http import HttpRequest
from ninja import FilterSchema, Query, Router, Schema
from ninja.errors import HttpError
from ninja.pagination import PageNumberPagination, paginate

from apps.common.constants import PAGE_SIZE
from apps.github.models.repository import Repository

router = Router()


class RepositoryFilterSchema(FilterSchema):
    """Filter schema for Repository."""

    name: str | None = None


class RepositorySchema(Schema):
    """Schema for Repository."""

    created_at: datetime
    description: str
    name: str
    updated_at: datetime


@router.get("/", response={200: list[RepositorySchema], 404: dict})
@paginate(PageNumberPagination, page_size=PAGE_SIZE)
def list_repository(
    request: HttpRequest, filters: RepositoryFilterSchema = Query(...)
) -> list[RepositorySchema] | dict:
    """Get all repositories."""
    repositories = filters.filter(Repository.objects.all())
    if not repositories.exists():
        raise HttpError(404, "Repositories not found")
    return repositories
