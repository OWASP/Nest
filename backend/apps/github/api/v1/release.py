"""Release API."""

from datetime import datetime

from django.http import HttpRequest
from ninja import Router, Schema

from apps.github.models.release import Release

router = Router()


class ReleaseSchema(Schema):
    """Schema for Release."""

    created_at: datetime
    description: str
    name: str
    published_at: datetime
    tag_name: str


@router.get("/", response=list[ReleaseSchema])
def list_release(request: HttpRequest) -> list[ReleaseSchema]:
    """Get all releases."""
    return Release.objects.all()
