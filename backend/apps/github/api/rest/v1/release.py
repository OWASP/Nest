"""Release API."""

from datetime import datetime
from typing import Literal

from django.conf import settings
from django.http import HttpRequest
from django.views.decorators.cache import cache_page
from ninja import Field, FilterSchema, Query, Router, Schema
from ninja.decorators import decorate_view
from ninja.pagination import PageNumberPagination, paginate

from apps.github.models.release import Release

router = Router()


class ReleaseFilterSchema(FilterSchema):
    """Filter schema for Release."""

    tag_name: str | None = Field(None, description="Tag name of the release", example="v1.0.0")


class ReleaseSchema(Schema):
    """Schema for Release."""

    created_at: datetime
    description: str
    name: str
    published_at: datetime
    tag_name: str


@router.get(
    "/",
    description="Retrieve a paginated list of GitHub releases.",
    operation_id="list_releases",
    summary="Get all releases",
    tags=["Releases"],
    response={200: list[ReleaseSchema]},
)
@decorate_view(cache_page(settings.API_CACHE_TIME_SECONDS))
@paginate(PageNumberPagination, page_size=settings.API_PAGE_SIZE)
def list_release(
    request: HttpRequest,
    filters: ReleaseFilterSchema = Query(..., description="Filter criteria for releases"),
    ordering: Literal["created_at", "-created_at", "published_at", "-published_at"] | None = Query(
        None, description="Ordering field"
    ),
) -> list[ReleaseSchema]:
    """Get all releases."""
    releases = filters.filter(Release.objects.all())
    if ordering:
        releases = releases.order_by(ordering)
    return releases
