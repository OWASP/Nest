"""User API."""

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

from apps.github.models.user import User

router = Router()


class MemberFilterSchema(FilterSchema):
    """Filter schema for User."""

    company: str | None = Field(
        None,
        description="Company of the user",
    )
    location: str | None = Field(None, description="Location of the member")


class MemberSchema(Schema):
    """Schema for Member."""

    avatar_url: str
    bio: str
    company: str
    created_at: datetime
    followers_count: int
    following_count: int
    location: str
    login: str
    name: str
    public_repositories_count: int
    title: str
    twitter_username: str
    updated_at: datetime
    url: str


class MemberErrorResponse(Schema):
    """Member error response schema."""

    message: str


@router.get(
    "/",
    description="Retrieve a paginated list of OWASP community members.",
    operation_id="list_members",
    response={HTTPStatus.OK: list[MemberSchema]},
    summary="List members",
    tags=["Community"],
)
@decorate_view(cache_page(settings.API_CACHE_TIME_SECONDS))
@paginate(PageNumberPagination, page_size=settings.API_PAGE_SIZE)
def list_members(
    request: HttpRequest,
    filters: MemberFilterSchema = Query(...),
    ordering: Literal["created_at", "-created_at", "updated_at", "-updated_at"] | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[MemberSchema]:
    """Get all members."""
    return filters.filter(User.objects.order_by(ordering or "-created_at"))


@router.get(
    "/{str:member_id}",
    description="Retrieve member details.",
    operation_id="get_member",
    response={
        HTTPStatus.NOT_FOUND: MemberErrorResponse,
        HTTPStatus.OK: MemberSchema,
    },
    summary="Get member",
    tags=["Community"],
)
def get_member(
    request: HttpRequest,
    member_id: str = Path(example="OWASP"),
) -> MemberSchema | MemberErrorResponse:
    """Get member."""
    if user := User.objects.filter(login__iexact=member_id).first():
        return user

    return Response({"message": "Member not found"}, status=HTTPStatus.NOT_FOUND)
