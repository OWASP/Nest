"""User API."""

from datetime import datetime
from http import HTTPStatus
from typing import Literal

from django.http import HttpRequest
from ninja import Field, FilterSchema, Path, Query, Schema
from ninja.decorators import decorate_view
from ninja.pagination import RouterPaginated
from ninja.responses import Response

from apps.api.decorators.cache import cache_response
from apps.github.models.user import User as UserModel

router = RouterPaginated(tags=["Community"])


class MemberBase(Schema):
    """Base schema for Member (used in list endpoints)."""

    avatar_url: str
    created_at: datetime
    login: str
    name: str
    updated_at: datetime
    url: str


class Member(MemberBase):
    """Schema for Member (minimal fields for list display)."""


class MemberDetail(MemberBase):
    """Detail schema for Member (used in single item endpoints)."""

    bio: str
    company: str
    followers_count: int
    following_count: int
    location: str
    public_repositories_count: int
    title: str
    twitter_username: str


class MemberError(Schema):
    """Member error schema."""

    message: str


class MemberFilter(FilterSchema):
    """Filter for User."""

    company: str | None = Field(
        None,
        description="Company of the user",
    )
    location: str | None = Field(None, description="Location of the member")


@router.get(
    "/",
    description="Retrieve a paginated list of OWASP community members.",
    operation_id="list_members",
    response=list[Member],
    summary="List members",
)
@decorate_view(cache_response())
def list_members(
    request: HttpRequest,
    filters: MemberFilter = Query(...),
    ordering: Literal["created_at", "-created_at", "updated_at", "-updated_at"] | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[Member]:
    """Get all members."""
    return filters.filter(UserModel.objects.order_by(ordering or "-created_at"))


@router.get(
    "/{str:member_id}",
    description="Retrieve member details.",
    operation_id="get_member",
    response={
        HTTPStatus.NOT_FOUND: MemberError,
        HTTPStatus.OK: MemberDetail,
    },
    summary="Get member",
)
@decorate_view(cache_response())
def get_member(
    request: HttpRequest,
    member_id: str = Path(example="OWASP"),
) -> MemberDetail | MemberError:
    """Get member."""
    if user := UserModel.objects.filter(login__iexact=member_id).first():
        return user

    return Response({"message": "Member not found"}, status=HTTPStatus.NOT_FOUND)
