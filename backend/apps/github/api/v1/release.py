"""Release API."""

from datetime import datetime

from django.http import HttpRequest
from ninja import Schema
from ninja.errors import HttpError
from ninja.pagination import RouterPaginated

from apps.github.models.release import Release

router = RouterPaginated()


class ReleaseSchema(Schema):
    """Schema for Release."""

    created_at: datetime
    description: str
    name: str
    published_at: datetime
    tag_name: str


@router.get("/", response=list[ReleaseSchema])
def list_release(request: HttpRequest) -> list[ReleaseSchema] | HttpError:
    """Get all releases."""
    releases = Release.objects.all()
    if not releases:
        raise HttpError(404, "Releases not found")
    return releases
