"""Release API."""

from datetime import datetime

from django.http import HttpRequest
from ninja import FilterSchema, Query, Router, Schema
from ninja.errors import HttpError
from ninja.pagination import PageNumberPagination, paginate

from apps.common.constants import PAGE_SIZE
from apps.github.models.release import Release

router = Router()


class ReleaseFilterSchema(FilterSchema):
    """Filter schema for Release."""

    tag_name: str | None = None


class ReleaseSchema(Schema):
    """Schema for Release."""

    created_at: datetime
    description: str
    name: str
    published_at: datetime
    tag_name: str


@router.get("/", response={200: list[ReleaseSchema], 404: dict})
@paginate(PageNumberPagination, page_size=PAGE_SIZE)
def list_release(
    request: HttpRequest, filters: ReleaseFilterSchema = Query(...)
) -> list[ReleaseSchema] | dict:
    """Get all releases."""
    releases = filters.filter(Release.objects.all())
    if not releases.exists():
        raise HttpError(404, "Releases not found")
    return releases
