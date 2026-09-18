"""Board Outcome API."""

from datetime import date, datetime
from http import HTTPStatus
from typing import Annotated, Literal

from django.http import HttpRequest
from ninja import Field, FilterLookup, FilterSchema, Path, Query, Schema
from ninja.decorators import decorate_view
from ninja.pagination import RouterPaginated
from ninja.responses import Response

from apps.api.decorators.cache import cache_response
from apps.api.rest.v0.common import Person, ValidationErrorSchema, annotate_meeting_date
from apps.owasp.models.board_outcome import BoardOutcome as BoardOutcomeModel

router = RouterPaginated(tags=["Board Outcomes"])


class BoardOutcomeBase(Schema):
    """Base schema for BoardOutcome (used in list endpoints)."""

    created_at: datetime
    due_date: date | None = None
    id: int
    meeting_date: datetime | None = None
    status: BoardOutcomeModel.Status
    updated_at: datetime

    @staticmethod
    def resolve_created_at(obj: BoardOutcomeModel) -> datetime:
        """Resolve the DB creation timestamp."""
        return obj.nest_created_at

    @staticmethod
    def resolve_updated_at(obj: BoardOutcomeModel) -> datetime:
        """Resolve the DB update timestamp."""
        return obj.nest_updated_at


class BoardOutcome(BoardOutcomeBase):
    """Schema for BoardOutcome (minimal fields for list display)."""


class BoardOutcomeDetail(BoardOutcomeBase):
    """Detail schema for BoardOutcome (used in single item endpoints)."""

    assignees: list[Person]
    description: str
    metadata: dict

    @staticmethod
    def resolve_assignees(obj: BoardOutcomeModel) -> list:
        """Resolve assignee EntityMember rows."""
        return list(obj.assignees.all())


class BoardOutcomeError(Schema):
    """Board outcome error schema."""

    message: str


class BoardOutcomeFilter(FilterSchema):
    """Filter for BoardOutcome."""

    assignee: Annotated[
        int | None,
        FilterLookup(q="assignees__id"),
    ] = Field(
        None,
        description="Assignee EntityMember id",
    )
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
    status: BoardOutcomeModel.Status | None = Field(
        None,
        description="Outcome status",
    )


@router.get(
    "/",
    description="Retrieve a paginated list of OWASP board outcomes.",
    operation_id="list_board_outcomes",
    response=list[BoardOutcome],
    summary="List board outcomes",
)
@decorate_view(cache_response())
def list_board_outcomes(
    request: HttpRequest,
    filters: BoardOutcomeFilter = Query(...),
    ordering: Literal["meeting_date", "-meeting_date", "due_date", "-due_date"] | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[BoardOutcome]:
    """List board outcomes."""
    outcomes = filters.filter(
        annotate_meeting_date(BoardOutcomeModel.objects.all(), action_field="outcome")
    )
    return outcomes.order_by(ordering or "-meeting_date")


@router.get(
    "/{int:outcome_id}",
    description="Retrieve a board outcome by id.",
    operation_id="get_board_outcome",
    response={
        HTTPStatus.BAD_REQUEST: ValidationErrorSchema,
        HTTPStatus.NOT_FOUND: BoardOutcomeError,
        HTTPStatus.OK: BoardOutcomeDetail,
    },
    summary="Get board outcome",
)
@decorate_view(cache_response())
def get_board_outcome(
    request: HttpRequest,
    outcome_id: int = Path(example=1),
) -> BoardOutcomeDetail | BoardOutcomeError:
    """Get a board outcome by id."""
    outcome = (
        annotate_meeting_date(BoardOutcomeModel.objects, action_field="outcome")
        .prefetch_related("assignees", "assignees__member")
        .filter(id=outcome_id)
        .first()
    )
    if outcome is None:
        return Response({"message": "Board outcome not found"}, status=HTTPStatus.NOT_FOUND)

    return outcome
