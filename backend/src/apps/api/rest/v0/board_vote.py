"""Board Vote API."""

from datetime import datetime
from http import HTTPStatus
from typing import Annotated, Literal

from django.http import HttpRequest
from ninja import Field, FilterLookup, FilterSchema, Path, Query, Schema
from ninja.decorators import decorate_view
from ninja.pagination import RouterPaginated
from ninja.responses import Response
from pydantic import AfterValidator

from apps.api.decorators.cache import cache_response
from apps.api.rest.v0.common import (
    Person,
    ValidationErrorSchema,
    annotate_meeting_date,
    normalize_datetime,
    order_by_date_field,
)
from apps.owasp.models.board_vote import BoardVote as BoardVoteModel

router = RouterPaginated(tags=["Board Votes"])


class BoardVoteBase(Schema):
    """Base schema for BoardVote (used in list endpoints)."""

    created_at: datetime
    id: int
    meeting_date: datetime | None = None
    motion_id: int
    result: BoardVoteModel.Result
    tally: str
    type: BoardVoteModel.Type
    updated_at: datetime

    @staticmethod
    def resolve_created_at(obj: BoardVoteModel) -> datetime:
        """Resolve the DB creation timestamp."""
        return obj.nest_created_at

    @staticmethod
    def resolve_updated_at(obj: BoardVoteModel) -> datetime:
        """Resolve the DB update timestamp."""
        return obj.nest_updated_at


class BoardVote(BoardVoteBase):
    """Schema for BoardVote (minimal fields for list display)."""


class BoardVoteDetail(BoardVoteBase):
    """Detail schema for BoardVote (used in single item endpoints)."""

    abstain: list[Person]
    against: list[Person]
    in_favor: list[Person]
    metadata: dict
    recused: list[Person]

    @staticmethod
    def resolve_abstain(obj: BoardVoteModel) -> list:
        """Resolve abstaining EntityMember rows."""
        return list(obj.abstain.all())

    @staticmethod
    def resolve_against(obj: BoardVoteModel) -> list:
        """Resolve against EntityMember rows."""
        return list(obj.against.all())

    @staticmethod
    def resolve_in_favor(obj: BoardVoteModel) -> list:
        """Resolve in-favor EntityMember rows."""
        return list(obj.in_favor.all())

    @staticmethod
    def resolve_recused(obj: BoardVoteModel) -> list:
        """Resolve recused EntityMember rows."""
        return list(obj.recused.all())


class BoardVoteError(Schema):
    """Board vote error schema."""

    message: str


class BoardVoteFilter(FilterSchema):
    """Filter for BoardVote."""

    date_gte: Annotated[
        datetime | None,
        FilterLookup(q="meeting_date__gte"),
        AfterValidator(normalize_datetime),
    ] = Field(
        None,
        description="Parent meeting date greater than or equal to (ISO 8601)",
    )
    date_lte: Annotated[
        datetime | None,
        FilterLookup(q="meeting_date__lte"),
        AfterValidator(normalize_datetime),
    ] = Field(
        None,
        description="Parent meeting date less than or equal to (ISO 8601)",
    )
    motion_id: int | None = Field(
        None,
        description="Motion the vote belongs to",
    )
    result: BoardVoteModel.Result | None = Field(
        None,
        description="Vote result",
    )
    type: BoardVoteModel.Type | None = Field(
        None,
        description="Vote type",
    )


@router.get(
    "/",
    description="Retrieve a paginated list of OWASP board votes.",
    operation_id="list_board_votes",
    response=list[BoardVote],
    summary="List board votes",
)
@decorate_view(cache_response())
def list_board_votes(
    request: HttpRequest,
    filters: BoardVoteFilter = Query(...),
    ordering: Literal["meeting_date", "-meeting_date"] | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[BoardVote]:
    """List board votes."""
    votes = filters.filter(
        annotate_meeting_date(
            BoardVoteModel.objects.all(), action_field="motion", outer_ref="motion_id"
        )
    )
    return order_by_date_field(votes, ordering or "-meeting_date")


@router.get(
    "/{int:vote_id}",
    description="Retrieve a board vote by id.",
    operation_id="get_board_vote",
    response={
        HTTPStatus.BAD_REQUEST: ValidationErrorSchema,
        HTTPStatus.NOT_FOUND: BoardVoteError,
        HTTPStatus.OK: BoardVoteDetail,
    },
    summary="Get board vote",
)
@decorate_view(cache_response())
def get_board_vote(
    request: HttpRequest,
    vote_id: int = Path(example=1),
) -> BoardVoteDetail | BoardVoteError:
    """Get a board vote by id."""
    vote = (
        annotate_meeting_date(BoardVoteModel.objects, action_field="motion", outer_ref="motion_id")
        .prefetch_related(
            "abstain",
            "abstain__member",
            "against",
            "against__member",
            "in_favor",
            "in_favor__member",
            "recused",
            "recused__member",
        )
        .filter(id=vote_id)
        .first()
    )
    if vote is None:
        return Response({"message": "Board vote not found"}, status=HTTPStatus.NOT_FOUND)

    return vote
