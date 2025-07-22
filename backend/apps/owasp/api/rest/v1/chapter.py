"""Chapter API."""

from datetime import datetime

from django.conf import settings
from django.http import HttpRequest
from django.views.decorators.cache import cache_page
from ninja import FilterSchema, Query, Router, Schema
from ninja.decorators import decorate_view
from ninja.pagination import PageNumberPagination, paginate

from apps.owasp.models.chapter import Chapter

router = Router()


class ChapterFilterSchema(FilterSchema):
    """Filter schema for Chapter."""

    country: str | None = None
    region: str | None = None


class ChapterSchema(Schema):
    """Schema for Chapter."""

    country: str
    created_at: datetime
    name: str
    region: str
    updated_at: datetime


VALID_CHAPTER_ORDERING_FIELDS = {"created_at", "updated_at"}


@router.get("/", response={200: list[ChapterSchema]})
@decorate_view(cache_page(settings.API_CACHE_TIME_SECONDS))
@paginate(PageNumberPagination, page_size=settings.API_PAGE_SIZE)
def list_chapters(
    request: HttpRequest,
    filters: ChapterFilterSchema = Query(...),
    ordering: str | None = Query(None),
) -> list[ChapterSchema]:
    """Get all chapters."""
    chapters = filters.filter(Chapter.objects.all())

    if ordering and ordering in VALID_CHAPTER_ORDERING_FIELDS:
        chapters = chapters.order_by(ordering)

    return chapters
