"""Board Meeting API."""

from datetime import datetime
from http import HTTPStatus
from typing import Annotated, Literal

from django.http import HttpRequest
from ninja import Field, FilterLookup, FilterSchema, Path, Query, Schema
from ninja.decorators import decorate_view
from ninja.pagination import RouterPaginated
from ninja.responses import Response

from apps.api.decorators.cache import cache_response
from apps.api.rest.v0.common import Person, ValidationErrorSchema
from apps.owasp.models.board_meeting import BoardMeeting as BoardMeetingModel

router = RouterPaginated(tags=["Board Meetings"])


class BoardMeetingBase(Schema):
    """Base schema for BoardMeeting (used in list endpoints)."""

    created_at: datetime
    date: datetime
    id: int
    quorum_present: bool | None = None
    source_path: str
    title: str
    type: BoardMeetingModel.Type
    updated_at: datetime

    @staticmethod
    def resolve_created_at(obj: BoardMeetingModel) -> datetime:
        """Resolve the DB creation timestamp."""
        return obj.nest_created_at

    @staticmethod
    def resolve_updated_at(obj: BoardMeetingModel) -> datetime:
        """Resolve the DB update timestamp."""
        return obj.nest_updated_at


class BoardMeeting(BoardMeetingBase):
    """Schema for BoardMeeting (minimal fields for list display)."""


class BoardMeetingAction(Schema):
    """Nested action row attached to a meeting."""

    discussion_id: int | None = None
    id: int
    motion_id: int | None = None
    order: int
    outcome_id: int | None = None


class BoardMeetingDetail(BoardMeetingBase):
    """Detail schema for BoardMeeting (used in single item endpoints)."""

    absentees: list[Person]
    actions: list[BoardMeetingAction]
    attachments: list
    attendees: list[Person]
    board_year: int
    call_in_url: str
    guests: list
    location: str
    metadata: dict
    recording_url: str
    source_checksum: str

    @staticmethod
    def resolve_absentees(obj: BoardMeetingModel) -> list:
        """Resolve absentee EntityMember rows."""
        return list(obj.absentees.all())

    @staticmethod
    def resolve_actions(obj: BoardMeetingModel) -> list:
        """Resolve ordered action rows for the meeting."""
        return list(obj.actions.order_by("order"))

    @staticmethod
    def resolve_attendees(obj: BoardMeetingModel) -> list:
        """Resolve attendee EntityMember rows."""
        return list(obj.attendees.all())

    @staticmethod
    def resolve_board_year(obj: BoardMeetingModel) -> int:
        """Resolve the year of the board this meeting belongs to."""
        return obj.board.year


class BoardMeetingError(Schema):
    """Board meeting error schema."""

    message: str


class BoardMeetingFilter(FilterSchema):
    """Filter for BoardMeeting."""

    date_gte: Annotated[
        datetime | None,
        FilterLookup(q="date__gte"),
    ] = Field(None, description="Meeting date greater than or equal to (ISO 8601)")
    date_lte: Annotated[
        datetime | None,
        FilterLookup(q="date__lte"),
    ] = Field(None, description="Meeting date less than or equal to (ISO 8601)")
    quorum_present: bool | None = Field(
        None,
        description="Whether quorum was reached at the meeting",
    )
    type: BoardMeetingModel.Type | None = Field(
        None,
        description="Meeting type",
    )


@router.get(
    "/",
    description="Retrieve a paginated list of OWASP board meetings.",
    operation_id="list_board_meetings",
    response=list[BoardMeeting],
    summary="List board meetings",
)
@decorate_view(cache_response())
def list_board_meetings(
    request: HttpRequest,
    filters: BoardMeetingFilter = Query(...),
    ordering: Literal["date", "-date"] | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[BoardMeeting]:
    """List board meetings."""
    return filters.filter(BoardMeetingModel.objects.order_by(ordering or "-date"))


@router.get(
    "/{int:meeting_id}",
    description="Retrieve a board meeting by id.",
    operation_id="get_board_meeting",
    response={
        HTTPStatus.BAD_REQUEST: ValidationErrorSchema,
        HTTPStatus.NOT_FOUND: BoardMeetingError,
        HTTPStatus.OK: BoardMeetingDetail,
    },
    summary="Get board meeting",
)
@decorate_view(cache_response())
def get_board_meeting(
    request: HttpRequest,
    meeting_id: int = Path(example=1),
) -> BoardMeetingDetail | BoardMeetingError:
    """Get a board meeting by id."""
    meeting = (
        BoardMeetingModel.objects.select_related("board")
        .prefetch_related(
            "absentees",
            "absentees__member",
            "attendees",
            "attendees__member",
            "actions",
        )
        .filter(id=meeting_id)
        .first()
    )
    if meeting is None:
        return Response({"message": "Board meeting not found"}, status=HTTPStatus.NOT_FOUND)

    return meeting
