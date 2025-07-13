"""Nest user GraphQL Mutations."""

import logging

import requests
import strawberry
from django.contrib.auth import login, logout
from django.core.exceptions import SuspiciousOperation
from github import Github
from strawberry.types import Info

from apps.github.models import User as GithubUser
from apps.nest.graphql.nodes.user import AuthUserNode
from apps.nest.graphql.permissions import IsAuthenticated
from apps.nest.models import User

logger = logging.getLogger(__name__)


@strawberry.type
class LogoutResult:
    """Payload for logout mutation."""

    ok: bool
    code: str | None = None
    message: str | None = None


@strawberry.type
class GitHubAuthResult:
    """Payload for GitHubAuth mutation."""

    auth_user: AuthUserNode | None


@strawberry.type
class UserMutations:
    """GraphQL mutations related to user."""

    @strawberry.mutation
    def github_auth(self, info: Info, access_token: str) -> GitHubAuthResult:
        """Authenticate via GitHub OAuth2."""
        try:
            github = Github(access_token)
            gh_user = github.get_user()
            gh_user_email = next(
                (e.email for e in gh_user.get_emails() if e.primary and e.verified), ""
            )
            if not gh_user_email:
                # TODO(arkid15r): let user know that primary verified email is required.
                return GitHubAuthResult(auth_user=None)

            github_user = GithubUser.update_data(gh_user, email=gh_user_email)
            if not github_user:
                return GitHubAuthResult(auth_user=None)

            auth_user, _ = User.objects.get_or_create(
                defaults={
                    "email": gh_user_email,
                    "github_user": github_user,
                },
                username=gh_user.login,
            )

            if auth_user:
                auth_user.backend = "django.contrib.auth.backends.ModelBackend"
                login(info.context.request, auth_user)

            return GitHubAuthResult(auth_user=auth_user)

        except requests.exceptions.RequestException as e:
            logger.warning("GitHub authentication failed: %s", e)
            return GitHubAuthResult(auth_user=None)

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def logout_user(self, info: Info) -> LogoutResult:
        """Logout the current user out of their Django session."""
        try:
            logout(info.context.request)
            return LogoutResult(
                ok=True,
                code="SUCCESS",
                message="User logged out successfully.",
            )
        except SuspiciousOperation as exc:
            logger.warning("Logout failed: %s", exc)
            return LogoutResult(
                ok=False,
                code="INVALID_SESSION",
                message="Invalid session.",
            )
