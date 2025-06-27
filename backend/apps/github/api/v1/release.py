"""Release API."""

from datetime import datetime

from django.http import HttpRequest
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.pagination import PageNumberPagination, paginate

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
@paginate(PageNumberPagination, page_size=100)
def list_release(request: HttpRequest) -> list[ReleaseSchema]:
    """Get all releases."""
    releases = Release.objects.all()
    if not releases:
        raise HttpError(404, "Releases not found")
    return releases
