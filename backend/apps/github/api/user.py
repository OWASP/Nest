"""User API."""

from datetime import datetime

from django.http import HttpRequest
from ninja import Router
from ninja.responses import Response
from pydantic import BaseModel

from apps.github.models.user import User

router = Router()


class UserSchema(BaseModel):
    """Schema for User."""

    model_config = {"from_attributes": True}

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


@router.get("/", response=list[UserSchema])
def get_user(request: HttpRequest) -> list[UserSchema]:
    """Get all users."""
    return User.objects.all()


@router.get("/{login}", response=UserSchema)
def get_user(request: HttpRequest, login: str) -> UserSchema | None:
    """Get user by login."""
    try:
        return User.objects.get(login=login)
    except User.DoesNotExist:
        return Response({"detail": "User not found."}, status=200)
