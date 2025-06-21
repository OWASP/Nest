"""Repository API."""

from datetime import datetime

from django.http import HttpRequest
from ninja import Router
from pydantic import BaseModel

from apps.github.models.repository import Repository

router = Router()


class RepositorySchema(BaseModel):
    """Schema for Repository."""

    model_config = {"from_attributes": True}

    created_at: datetime
    description: str
    name: str
    updated_at: datetime


@router.get("/", response=list[RepositorySchema])
def get_repository(request: HttpRequest) -> list[RepositorySchema]:
    """Get all repositories."""
    return Repository.objects.all()
