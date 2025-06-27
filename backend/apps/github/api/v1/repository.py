"""Repository API."""

from datetime import datetime

from django.http import HttpRequest
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.pagination import PageNumberPagination, paginate

from apps.github.models.repository import Repository

router = Router()


class RepositorySchema(Schema):
    """Schema for Repository."""

    created_at: datetime
    description: str
    name: str
    updated_at: datetime


@router.get("/", response={200: list[RepositorySchema], 404: dict})
@paginate(PageNumberPagination, page_size=100)
def list_repository(request: HttpRequest) -> list[RepositorySchema]:
    """Get all repositories."""
    repositories = Repository.objects.all()
    if not repositories.exists():
        raise HttpError(404, "Repositories not found")
    return repositories
