"""User API."""

from datetime import datetime
from typing import Literal

from django.conf import settings
from django.http import HttpRequest
from django.views.decorators.cache import cache_page
from ninja import Field, FilterSchema, Query, Router, Schema
from ninja.decorators import decorate_view
from ninja.errors import HttpError
from ninja.pagination import PageNumberPagination, paginate

from apps.github.models.user import User

router = Router()


class UserFilterSchema(FilterSchema):
    """Filter schema for User."""

    company: str | None = Field(
        None,
        description="Company of the user",
    )
    location: str | None = Field(None, description="Location of the user", example="India")


class UserSchema(Schema):
    """Schema for User."""

    avatar_url: str
    bio: str
    company: str
    created_at: datetime
    email: str
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


@router.get(
    "/",
    description="Retrieve a paginated list of GitHub users.",
    operation_id="list_users",
    response={200: list[UserSchema]},
    summary="List users",
    tags=["GitHub"],
)
@decorate_view(cache_page(settings.API_CACHE_TIME_SECONDS))
@paginate(PageNumberPagination, page_size=settings.API_PAGE_SIZE)
def list_users(
    request: HttpRequest,
    filters: UserFilterSchema = Query(...),
    ordering: Literal["created_at", "-created_at", "updated_at", "-updated_at"] | None = Query(
        None,
        description="Ordering field",
    ),
) -> list[UserSchema]:
    """Get all users."""
    users = filters.filter(User.objects.all())

    if ordering:
        users = users.order_by(ordering)

    return users


@router.get(
    "/{login}",
    description="Retrieve a GitHub user by login.",
    operation_id="get_user",
    response={200: UserSchema, 404: dict},
    summary="Get user by login",
    tags=["GitHub"],
)
def get_user(request: HttpRequest, login: str) -> UserSchema:
    """Get user by login."""
    user = User.objects.filter(login=login).first()
    if not user:
        raise HttpError(404, "User not found")
    return user
