"""Repository API."""

from datetime import datetime

from django.http import HttpRequest
from ninja import Schema
from ninja.errors import HttpError
from ninja.pagination import RouterPaginated

from apps.github.models.repository import Repository

router = RouterPaginated()


class RepositorySchema(Schema):
    """Schema for Repository."""

    created_at: datetime
    description: str
    name: str
    updated_at: datetime


@router.get("/", response=list[RepositorySchema])
def list_repository(request: HttpRequest) -> list[RepositorySchema]:
    """Get all repositories."""
    repositories = Repository.objects.all()
    if not repositories:
        raise HttpError(404, "Repositories not found")
    return repositories
