"""Nest GraphQL utils."""

from django.db import models
from github import Github

from apps.github.models import User as GithubUser
from apps.nest.models import User as NestUser


def get_authenticated_user(request) -> NestUser:
    """Get authenticated user from request."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise Exception("Missing or invalid Authorization header")

    access_token = auth_header.removeprefix("Bearer ").strip()
    try:
        github = Github(access_token)
        gh_user = github.get_user()
        login = gh_user.login
    except Exception as err:
        raise Exception("GitHub token is invalid or expired") from err

    try:
        github_user = GithubUser.objects.get(models.Q(login__iexact=login.lower()))
    except GithubUser.DoesNotExist as err:
        raise Exception("No GithubUser found matching this login or name") from err

    try:
        user = NestUser.objects.get(github_user=github_user)
    except NestUser.DoesNotExist as err:
        raise Exception("No linked Nest user found for this GitHub account") from err

    return user
