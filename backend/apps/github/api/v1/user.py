"""User API."""

from datetime import datetime

from django.http import HttpRequest
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.pagination import PageNumberPagination, paginate

from apps.github.models.user import User

router = Router()


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


@router.get("/", response={200: list[UserSchema], 404: dict})
@paginate(PageNumberPagination, page_size=100)
def list_users(request: HttpRequest) -> list[UserSchema]:
    """Get all users."""
    users = User.objects.all()
    if not users.exists():
        raise HttpError(404, "Users not found")
    return users


@router.get("/{login}", response={200: UserSchema, 404: dict})
def get_user(request: HttpRequest, login: str) -> UserSchema:
    """Get user by login."""
    user = User.objects.filter(login=login).first()
    if not user:
        raise HttpError(404, "User not found")
    return user
