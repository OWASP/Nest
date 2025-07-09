"""Nest GraphQL utils."""

import logging

from django.core.exceptions import PermissionDenied
from github import Github, GithubException

from apps.github.models import User as GithubUser
from apps.nest.models import User as NestUser

logger = logging.getLogger(__name__)


def get_authenticated_user(request) -> NestUser:
    """Get authenticated user from request."""
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        msg = "Missing or invalid Authorization header."
        logger.warning("Authentication failed: %s", msg)
        raise PermissionDenied(msg)

    access_token = auth_header.removeprefix("Bearer ").strip()
    try:
        github = Github(access_token)
        gh_user = github.get_user()
        login = gh_user.login
    except GithubException as err:
        msg = "GitHub token is invalid or expired."
        logger.warning("Authentication failed: %s", msg, exc_info=True)
        raise PermissionDenied(msg) from err

    try:
        github_user = GithubUser.objects.get(login__iexact=login.lower())
    except GithubUser.DoesNotExist as err:
        msg = "No GithubUser found matching this login or name."
        logger.warning("Authentication failed for GitHub login '%s': %s", login, msg)
        raise PermissionDenied(msg) from err

    try:
        user = NestUser.objects.get(github_user=github_user)
    except NestUser.DoesNotExist as err:
        msg = "No linked Nest user found for this GitHub account."
        logger.warning("Authentication failed for GitHub user '%s': %s", github_user.login, msg)
        raise PermissionDenied(msg) from err

    return user


def get_authenticated_user_by_token(access_token: str) -> NestUser:
    """Get authenticated user from request."""
    try:
        github = Github(access_token)
        gh_user = github.get_user()
        login = gh_user.login
    except GithubException as err:
        msg = "GitHub token is invalid or expired."
        logger.warning("Authentication failed: %s", msg, exc_info=True)
        raise PermissionDenied(msg) from err

    try:
        github_user = GithubUser.objects.get(login__iexact=login.lower())
    except GithubUser.DoesNotExist as err:
        msg = "No GithubUser found matching this login or name."
        logger.warning("Authentication failed for GitHub login '%s': %s", login, msg)
        raise PermissionDenied(msg) from err

    try:
        user = NestUser.objects.get(github_user=github_user)
    except NestUser.DoesNotExist as err:
        msg = "No linked Nest user found for this GitHub account."
        logger.warning("Authentication failed for GitHub user '%s': %s", github_user.login, msg)
        raise PermissionDenied(msg) from err

    return user
