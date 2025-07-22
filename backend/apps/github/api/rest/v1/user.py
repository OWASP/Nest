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


@router.get(
    "/",
    summary="Get all users",
    tags=["Users"],
    response={200: list[UserSchema]},
)
@decorate_view(cache_page(settings.API_CACHE_TIME_SECONDS))
@paginate(PageNumberPagination, page_size=settings.API_PAGE_SIZE)
def list_users(
    request: HttpRequest,
    filters: UserFilterSchema = Query(...),
    ordering: str | None = Query(None),
) -> list[UserSchema]:
    """
    Retrieve a paginated list of users, optionally filtered by company and location, and ordered by creation or update date.
    
    Parameters:
        filters (UserFilterSchema): Optional filters for company and location.
        ordering (str, optional): Field to order results by; must be "created_at" or "updated_at".
    
    Returns:
        list[UserSchema]: A list of users matching the specified filters and ordering.
    """
    users = filters.filter(User.objects.all())

    if ordering and ordering in VALID_USER_ORDERING_FIELDS:
        users = users.order_by(ordering)

    return users


@router.get(
    "/{login}",
    summary="Get user by login",
    tags=["Users"],
    response={200: UserSchema, 404: dict},
)
def get_user(request: HttpRequest, login: str) -> UserSchema:
    """
    Retrieve a user's details by their login identifier.
    
    Parameters:
    	login (str): The unique login name of the user to retrieve.
    
    Returns:
    	UserSchema: The user's data if found.
    
    Raises:
    	HttpError: If no user with the specified login exists, raises a 404 error.
    """
    user = User.objects.filter(login=login).first()
    if not user:
        raise HttpError(404, "User not found")
    return user
