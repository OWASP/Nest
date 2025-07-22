"""Release API."""

from datetime import datetime

from django.conf import settings
from django.http import HttpRequest
from django.views.decorators.cache import cache_page
from ninja import FilterSchema, Query, Router, Schema
from ninja.decorators import decorate_view
from ninja.pagination import PageNumberPagination, paginate

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


VALID_RELEASE_ORDERING_FIELDS = {"created_at", "published_at"}


@router.get(
    "/",
    summary="Get all releases",
    tags=["Releases"],
    response={200: list[ReleaseSchema]},
)
@decorate_view(cache_page(settings.API_CACHE_TIME_SECONDS))
@paginate(PageNumberPagination, page_size=settings.API_PAGE_SIZE)
def list_release(
    request: HttpRequest,
    filters: ReleaseFilterSchema = Query(...),
    ordering: str | None = Query(None),
) -> list[ReleaseSchema]:
    """Get all releases."""
    releases = filters.filter(Release.objects.all())
    if ordering and ordering in VALID_RELEASE_ORDERING_FIELDS:
        releases = releases.order_by(ordering)
    return releases
