"""Chapter API."""

from datetime import datetime
from http import HTTPStatus
from typing import Literal

from django.http import HttpRequest
from ninja import Field, FilterSchema, Path, Query, Schema
from ninja.decorators import decorate_view
from ninja.pagination import RouterPaginated
from ninja.responses import Response

from apps.api.decorators.cache import cache_response
from apps.owasp.models.chapter import Chapter as ChapterModel

router = RouterPaginated(tags=["Chapters"])


class ChapterBase(Schema):
    """Base schema for Chapter (used in list endpoints)."""

    created_at: datetime
    key: str
    name: str
    updated_at: datetime

    @staticmethod
    def resolve_key(obj) -> str:
        """Resolve key."""
        return obj.nest_key


class Chapter(ChapterBase):
    """Schema for Chapter (minimal fields for list display)."""


class ChapterDetail(ChapterBase):
    """Detail schema for Chapter (used in single item endpoints)."""

    country: str
    region: str


class ChapterError(Schema):
    """Chapter error schema."""

    message: str


class ChapterFilter(FilterSchema):
    """Filter for Chapter."""

    country: str | None = Field(None, description="Country of the chapter")


@router.get(
    "/",
    description="Retrieve a paginated list of OWASP chapters.",
    operation_id="list_chapters",
    response=list[Chapter],
    summary="List chapters",
)
@decorate_view(cache_response())
def list_chapters(
    request: HttpRequest,
    filters: ChapterFilter = Query(...),
    ordering: Literal["created_at", "-created_at", "updated_at", "-updated_at"] | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[Chapter]:
    """Get chapters."""
    return filters.filter(ChapterModel.active_chapters.order_by(ordering or "-created_at"))


@router.get(
    "/{str:chapter_id}",
    description="Retrieve chapter details.",
    operation_id="get_chapter",
    response={
        HTTPStatus.NOT_FOUND: ChapterError,
        HTTPStatus.OK: ChapterDetail,
    },
    summary="Get chapter",
)
@decorate_view(cache_response())
def get_chapter(
    request: HttpRequest,
    chapter_id: str = Path(example="London"),
) -> ChapterDetail | ChapterError:
    """Get chapter."""
    if chapter := ChapterModel.active_chapters.filter(
        key__iexact=(
            chapter_id if chapter_id.startswith("www-chapter-") else f"www-chapter-{chapter_id}"
        )
    ).first():
        return chapter

    return Response({"message": "Chapter not found"}, status=HTTPStatus.NOT_FOUND)
