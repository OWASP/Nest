"""User API."""

from datetime import datetime

from django.conf import settings
from django.http import HttpRequest
from django.views.decorators.cache import cache_page
from ninja import FilterSchema, Query, Router, Schema
from ninja.decorators import decorate_view
from ninja.errors import HttpError
from ninja.pagination import PageNumberPagination, paginate

from apps.github.models.user import User

router = Router()


class UserFilterSchema(FilterSchema):
    """Filter schema for User."""

    company: str | None = None
    location: str | None = None


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


VALID_USER_ORDERING_FIELDS = {"created_at", "updated_at"}


@router.get("/", response={200: list[UserSchema]})
@decorate_view(cache_page(settings.CACHE_TIME))
@paginate(PageNumberPagination, page_size=settings.PAGE_SIZE)
def list_users(
    request: HttpRequest,
    filters: UserFilterSchema = Query(...),
    ordering: str | None = Query(None),
) -> list[UserSchema]:
    """Get all users."""
    users = filters.filter(User.objects.all())

    if ordering and ordering in VALID_USER_ORDERING_FIELDS:
        users = users.order_by(ordering)

    return users


@router.get("/{login}", response={200: UserSchema, 404: dict})
def get_user(request: HttpRequest, login: str) -> UserSchema:
    """Get user by login."""
    user = User.objects.filter(login=login).first()
    if not user:
        raise HttpError(404, "User not found")
    return user
