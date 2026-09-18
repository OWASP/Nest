"""Board Motion API."""

from datetime import datetime
from http import HTTPStatus
from typing import Annotated, Literal

from django.http import HttpRequest
from ninja import Field, FilterLookup, FilterSchema, Path, Query, Schema
from ninja.decorators import decorate_view
from ninja.pagination import RouterPaginated
from ninja.responses import Response

from apps.api.decorators.cache import cache_response
from apps.api.rest.v0.common import Person, ValidationErrorSchema, annotate_meeting_date
from apps.owasp.models.board_motion import BoardMotion as BoardMotionModel

router = RouterPaginated(tags=["Board Motions"])


class BoardMotionBase(Schema):
    """Base schema for BoardMotion (used in list endpoints)."""

    created_at: datetime
    id: int
    meeting_date: datetime | None = None
    sponsor: Person | None = None
    title: str
    updated_at: datetime

    @staticmethod
    def resolve_created_at(obj: BoardMotionModel) -> datetime:
        """Resolve the DB creation timestamp."""
        return obj.nest_created_at

    @staticmethod
    def resolve_updated_at(obj: BoardMotionModel) -> datetime:
        """Resolve the DB update timestamp."""
        return obj.nest_updated_at


class BoardMotion(BoardMotionBase):
    """Schema for BoardMotion (minimal fields for list display)."""


class BoardMotionDetail(BoardMotionBase):
    """Detail schema for BoardMotion (used in single item endpoints)."""

    amends_motion_id: int | None = None
    background: str
    description: str
    metadata: dict
    references: list[dict]
    second: Person | None = None


class BoardMotionError(Schema):
    """Board motion error schema."""

    message: str


class BoardMotionFilter(FilterSchema):
    """Filter for BoardMotion."""

    date_gte: Annotated[
        datetime | None,
        FilterLookup(q="meeting_date__gte"),
    ] = Field(
        None,
        description="Parent meeting date greater than or equal to (ISO 8601)",
    )
    date_lte: Annotated[
        datetime | None,
        FilterLookup(q="meeting_date__lte"),
    ] = Field(
        None,
        description="Parent meeting date less than or equal to (ISO 8601)",
    )
    sponsor: Annotated[
        int | None,
        FilterLookup(q="sponsor_id"),
    ] = Field(
        None,
        description="Sponsor EntityMember id",
    )


@router.get(
    "/",
    description="Retrieve a paginated list of OWASP board motions.",
    operation_id="list_board_motions",
    response=list[BoardMotion],
    summary="List board motions",
)
@decorate_view(cache_response())
def list_board_motions(
    request: HttpRequest,
    filters: BoardMotionFilter = Query(...),
    ordering: Literal["meeting_date", "-meeting_date"] | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[BoardMotion]:
    """List board motions."""
    motions = filters.filter(
        annotate_meeting_date(
            BoardMotionModel.objects.select_related("sponsor", "sponsor__member"),
            action_field="motion",
        )
    )
    return motions.order_by(ordering or "-meeting_date")


@router.get(
    "/{int:motion_id}",
    description="Retrieve a board motion by id.",
    operation_id="get_board_motion",
    response={
        HTTPStatus.BAD_REQUEST: ValidationErrorSchema,
        HTTPStatus.NOT_FOUND: BoardMotionError,
        HTTPStatus.OK: BoardMotionDetail,
    },
    summary="Get board motion",
)
@decorate_view(cache_response())
def get_board_motion(
    request: HttpRequest,
    motion_id: int = Path(example=1),
) -> BoardMotionDetail | BoardMotionError:
    """Get a board motion by id."""
    motion = (
        annotate_meeting_date(BoardMotionModel.objects, action_field="motion")
        .select_related("sponsor", "sponsor__member", "second", "second__member", "amends_motion")
        .filter(id=motion_id)
        .first()
    )
    if motion is None:
        return Response({"message": "Board motion not found"}, status=HTTPStatus.NOT_FOUND)

    return motion
