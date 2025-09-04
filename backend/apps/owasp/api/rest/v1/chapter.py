"""Chapter API."""

from datetime import datetime
from typing import Literal

from django.conf import settings
from django.http import HttpRequest
from django.views.decorators.cache import cache_page
from ninja import Field, FilterSchema, Query, Router, Schema
from ninja.decorators import decorate_view
from ninja.pagination import PageNumberPagination, paginate

from apps.owasp.models.chapter import Chapter

router = Router()


class ChapterFilterSchema(FilterSchema):
    """Filter schema for Chapter."""

    country: str | None = Field(None, description="Country of the chapter", example="India")
    region: str | None = Field(None, description="Region of the chapter", example="Asia")


class ChapterSchema(Schema):
    """Schema for Chapter."""

    country: str
    created_at: datetime
    name: str
    region: str
    updated_at: datetime


@router.get(
    "/",
    description="Retrieve a paginated list of OWASP chapters.",
    operation_id="list_chapters",
    response={200: list[ChapterSchema]},
    summary="List chapters",
    tags=["owasp"],
)
@decorate_view(cache_page(settings.API_CACHE_TIME_SECONDS))
@paginate(PageNumberPagination, page_size=settings.API_PAGE_SIZE)
def list_chapters(
    request: HttpRequest,
    filters: ChapterFilterSchema = Query(...),
    ordering: Literal["created_at", "-created_at", "updated_at", "-updated_at"] | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[ChapterSchema]:
    """Get all chapters."""
    chapters = filters.filter(Chapter.objects.all())

    if ordering:
        chapters = chapters.order_by(ordering)

    return chapters
