"""Chapter API."""

from datetime import datetime
from http import HTTPStatus
from typing import Literal

from django.conf import settings
from django.http import HttpRequest
from django.views.decorators.cache import cache_page
from ninja import Field, FilterSchema, Path, Query, Router, Schema
from ninja.decorators import decorate_view
from ninja.pagination import PageNumberPagination, paginate
from ninja.responses import Response

from apps.owasp.models.chapter import Chapter

router = Router()


class ChapterErrorResponse(Schema):
    """Chapter error response schema."""

    message: str


class ChapterFilterSchema(FilterSchema):
    """Filter schema for Chapter."""

    country: str | None = Field(None, description="Country of the chapter")
    region: str | None = Field(None, description="Region of the chapter")


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
    tags=["Chapters"],
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
    """Get chapters."""
    return filters.filter(Chapter.active_chapters.order_by(ordering or "-created_at"))


@router.get(
    "/{str:chapter_id}",
    description="Retrieve chapter details.",
    operation_id="get_chapter",
    response={
        HTTPStatus.NOT_FOUND: ChapterErrorResponse,
        HTTPStatus.OK: ChapterSchema,
    },
    summary="Get chapter",
    tags=["Chapters"],
)
def get_chapter(
    request: HttpRequest,
    chapter_id: str = Path(example="London"),
) -> ChapterSchema | ChapterErrorResponse:
    """Get chapter."""
    if chapter := Chapter.active_chapters.filter(
        key__iexact=(
            chapter_id if chapter_id.startswith("www-chapter-") else f"www-chapter-{chapter_id}"
        )
    ).first():
        return chapter

    return Response({"message": "Chapter not found"}, status=HTTPStatus.NOT_FOUND)
