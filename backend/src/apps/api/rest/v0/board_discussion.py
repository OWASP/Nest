"""Board Discussion API."""

from datetime import datetime
from http import HTTPStatus
from typing import Literal

from django.http import HttpRequest
from ninja import Field, FilterSchema, Path, Query, Schema
from ninja.decorators import decorate_view
from ninja.pagination import RouterPaginated
from ninja.responses import Response

from apps.api.decorators.cache import cache_response
from apps.api.rest.v0.common import Person, ValidationErrorSchema, annotate_meeting_date
from apps.owasp.models.board_discussion import BoardDiscussion as BoardDiscussionModel

router = RouterPaginated(tags=["Board Discussions"])


class BoardDiscussionBase(Schema):
    """Base schema for BoardDiscussion (used in list endpoints)."""

    created_at: datetime
    id: int
    meeting_date: datetime | None = None
    topic: str
    updated_at: datetime

    @staticmethod
    def resolve_created_at(obj: BoardDiscussionModel) -> datetime:
        """Resolve the DB creation timestamp."""
        return obj.nest_created_at

    @staticmethod
    def resolve_updated_at(obj: BoardDiscussionModel) -> datetime:
        """Resolve the DB update timestamp."""
        return obj.nest_updated_at


class BoardDiscussion(BoardDiscussionBase):
    """Schema for BoardDiscussion (minimal fields for list display)."""


class BoardDiscussionDetail(BoardDiscussionBase):
    """Detail schema for BoardDiscussion (used in single item endpoints)."""

    description: str
    metadata: dict
    participants: list[Person]

    @staticmethod
    def resolve_participants(obj: BoardDiscussionModel) -> list:
        """Resolve participant EntityMember rows."""
        return list(obj.participants.all())


class BoardDiscussionError(Schema):
    """Board discussion error schema."""

    message: str


class BoardDiscussionFilter(FilterSchema):
    """Filter for BoardDiscussion."""

    date_gte: datetime | None = Field(
        None,
        description="Parent meeting date greater than or equal to (ISO 8601)",
        q="meeting_date__gte",
    )
    date_lte: datetime | None = Field(
        None,
        description="Parent meeting date less than or equal to (ISO 8601)",
        q="meeting_date__lte",
    )


@router.get(
    "/",
    description="Retrieve a paginated list of OWASP board discussions.",
    operation_id="list_board_discussions",
    response=list[BoardDiscussion],
    summary="List board discussions",
)
@decorate_view(cache_response())
def list_board_discussions(
    request: HttpRequest,
    filters: BoardDiscussionFilter = Query(...),
    ordering: Literal["meeting_date", "-meeting_date"] | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[BoardDiscussion]:
    """List board discussions."""
    discussions = filters.filter(
        annotate_meeting_date(BoardDiscussionModel.objects.all(), action_field="discussion")
    )
    return discussions.order_by(ordering or "-meeting_date")


@router.get(
    "/{int:discussion_id}",
    description="Retrieve a board discussion by id.",
    operation_id="get_board_discussion",
    response={
        HTTPStatus.BAD_REQUEST: ValidationErrorSchema,
        HTTPStatus.NOT_FOUND: BoardDiscussionError,
        HTTPStatus.OK: BoardDiscussionDetail,
    },
    summary="Get board discussion",
)
@decorate_view(cache_response())
def get_board_discussion(
    request: HttpRequest,
    discussion_id: int = Path(example=1),
) -> BoardDiscussionDetail | BoardDiscussionError:
    """Get a board discussion by id."""
    discussion = (
        annotate_meeting_date(BoardDiscussionModel.objects, action_field="discussion")
        .prefetch_related("participants", "participants__member")
        .filter(id=discussion_id)
        .first()
    )
    if discussion is None:
        return Response({"message": "Board discussion not found"}, status=HTTPStatus.NOT_FOUND)

    return discussion
