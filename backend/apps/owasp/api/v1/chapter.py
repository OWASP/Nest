"""Chapter API."""

from datetime import datetime

from django.http import HttpRequest
from ninja import FilterSchema, Query, Router, Schema
from ninja.errors import HttpError
from ninja.pagination import PageNumberPagination, paginate

from apps.common.constants import PAGE_SIZE
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


@router.get("/", response={200: list[ChapterSchema], 404: dict})
@paginate(PageNumberPagination, page_size=PAGE_SIZE)
def list_chapters(
    request: HttpRequest, filters: ChapterFilterSchema = Query(...)
) -> list[ChapterSchema] | dict:
    """Get all chapters."""
    chapters = filters.filter(Chapter.objects.all())
    if not chapters.exists():
        raise HttpError(404, "Chapters not found")
    return chapters
