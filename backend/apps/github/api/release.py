"""Release API."""

from datetime import datetime

from django.http import HttpRequest
from ninja import Router
from pydantic import BaseModel

from apps.github.models.release import Release

router = Router()


class ReleaseSchema(BaseModel):
    """Schema for Release."""

    model_config = {"from_attributes": True}

    created_at: datetime
    description: str
    name: str
    published_at: datetime
    tag_name: str


@router.get("/", response=list[ReleaseSchema])
def get_release(request: HttpRequest) -> list[ReleaseSchema]:
    """Get all releases."""
    return Release.objects.all()
