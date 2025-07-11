"""Utils."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.exceptions import ObjectDoesNotExist

from apps.nest.models import User as NestUser

if TYPE_CHECKING:
    from apps.github.models import User as GithubUser


def get_user_entities_by_github_username(
    username: str,
) -> tuple[GithubUser, NestUser] | None:
    """Get the GithubUser and NestUser for a given GitHub username.

    Returns a (GithubUser, NestUser) tuple, or None if not found.
    """
    try:
        nest_user = NestUser.objects.select_related("github_user").get(github_user__login=username)
    except ObjectDoesNotExist:
        return None

    return nest_user.github_user, nest_user
