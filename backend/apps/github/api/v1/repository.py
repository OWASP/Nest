"""Repository API."""

from datetime import datetime

from django.http import HttpRequest
from ninja import Router, Schema

from apps.github.models.repository import Repository

router = Router()


class RepositorySchema(Schema):
    """Schema for Repository."""

    created_at: datetime
    description: str
    name: str
    updated_at: datetime


@router.get("/", response=list[RepositorySchema])
def list_repository(request: HttpRequest) -> list[RepositorySchema]:
    """Get all repositories."""
    return Repository.objects.all()
