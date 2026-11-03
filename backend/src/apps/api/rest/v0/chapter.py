"""Chapter API."""

from datetime import datetime
from http import HTTPStatus
from typing import Literal

from django.db.models.functions import Coalesce
from django.http import HttpRequest
from ninja import Field, Path, Query, Schema
from ninja.decorators import decorate_view
from ninja.pagination import RouterPaginated
from ninja.responses import Response

from apps.api.decorators.cache import cache_response
from apps.api.rest.v0.common import Leader, LocationFilter, ValidationErrorSchema
from apps.owasp.models.chapter import Chapter as ChapterModel

router = RouterPaginated(tags=["Chapters"])

TIMESTAMP_ORDERING = {
    "created_at": Coalesce("created_at", "nest_created_at"),
    "-created_at": Coalesce("created_at", "nest_created_at").desc(),
    "updated_at": Coalesce("updated_at", "nest_updated_at"),
    "-updated_at": Coalesce("updated_at", "nest_updated_at").desc(),
}


class ChapterBase(Schema):
    """Base schema for Chapter (used in list endpoints)."""

    created_at: datetime
    key: str
    latitude: float | None = None
    longitude: float | None = None
    name: str
    updated_at: datetime

    @staticmethod
    def resolve_key(obj: ChapterModel) -> str:
        """Resolve key."""
        return obj.nest_key

    @staticmethod
    def resolve_created_at(obj: ChapterModel) -> datetime:
        """Return the source timestamp, or when Nest stored the chapter."""
        return obj.created_at or obj.nest_created_at

    @staticmethod
    def resolve_updated_at(obj: ChapterModel) -> datetime:
        """Return the source timestamp, or when Nest last stored the chapter."""
        return obj.updated_at or obj.nest_updated_at


class Chapter(ChapterBase):
    """Schema for Chapter (minimal fields for list display)."""


class ChapterDetail(ChapterBase):
    """Detail schema for Chapter (used in single item endpoints)."""

    country: str
    leaders: list[Leader]
    region: str

    @staticmethod
    def resolve_leaders(obj):
        """Resolve leaders."""
        return [
            Leader(key=leader.member.login if leader.member else None, name=leader.member_name)
            for leader in obj.entity_leaders
        ]


class ChapterError(Schema):
    """Chapter error schema."""

    message: str


class ChapterFilter(LocationFilter):
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
    ordering: Literal[
        "created_at",
        "-created_at",
        "updated_at",
        "-updated_at",
        "latitude",
        "-latitude",
        "longitude",
        "-longitude",
    ]
    | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[Chapter]:
    """Get chapters."""
    order = ordering or "-created_at"
    return filters.filter(
        ChapterModel.active_chapters.order_by(TIMESTAMP_ORDERING.get(order, order))
    )


@router.get(
    "/{str:chapter_id}",
    description="Retrieve chapter details.",
    operation_id="get_chapter",
    response={
        HTTPStatus.BAD_REQUEST: ValidationErrorSchema,
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
    if chapter := ChapterModel.get_by_key(chapter_id):
        return chapter

    return Response({"message": "Chapter not found"}, status=HTTPStatus.NOT_FOUND)
