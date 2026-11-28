"""Nest user GraphQL Mutations."""

import logging

import strawberry
from django.contrib.auth import login, logout
from github import Github
from github.AuthenticatedUser import AuthenticatedUser
from github.GithubException import BadCredentialsException
from strawberry.types import Info

from apps.github.models import User as GithubUser
from apps.nest.api.internal.nodes.user import AuthUserNode
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

    message: str
    ok: bool
    user: AuthUserNode | None = None


@strawberry.type
class UserMutations:
    """GraphQL mutations related to user."""

    @strawberry.mutation
    def github_auth(self, info: Info, access_token: str) -> GitHubAuthResult:
        """Authenticate via GitHub OAuth2."""
        try:
            github = Github(access_token)
            gh_user = github.get_user()

            if isinstance(gh_user, AuthenticatedUser):
                gh_user_email = next(
                    (e.email for e in gh_user.get_emails() if e.primary and e.verified), ""
                )
                if not gh_user_email:
                    return GitHubAuthResult(
                        message="Verified primary email is required on your GitHub account.",
                        ok=False,
                    )
            else:
                logger.warning(
                    "GitHub user is not AuthenticatedUser. Cannot fetch emails for %s.", gh_user
                )
                return GitHubAuthResult(
                    message="Authenticated user required to fetch primary email.",
                    ok=False,
                )

            github_user = GithubUser.update_data(gh_user, email=gh_user_email)
            if not github_user:
                logger.warning("Failed to retrieve GitHub user data for %s.", gh_user)
                return GitHubAuthResult(
                    message="Failed to retrieve GitHub user.",
                    ok=False,
                )

            nest_user, _ = User.objects.get_or_create(
                defaults={
                    "email": gh_user_email,
                    "github_user": github_user,
                },
                username=gh_user.login,
            )

            # Log the user in and attach it to a session.
            # https://docs.djangoproject.com/en/5.2/topics/auth/default/#django.contrib.auth.login
            # https://docs.djangoproject.com/en/5.2/topics/http/sessions/
            login(info.context.request, nest_user)

            return GitHubAuthResult(
                message="Successfully authenticated with GitHub.",
                ok=True,
                user=nest_user,
            )
        except BadCredentialsException:
            return GitHubAuthResult(
                message="GitHub authentication request failed.",
                ok=False,
            )

    @strawberry.mutation
    def logout_user(self, info: Info) -> LogoutResult:
        """Logout the current user."""
        if not info.context.request.user.is_authenticated:
            return LogoutResult(
                message="User is not logged in.",
                ok=False,
            )

        # Log the user out and clear the session.
        # https://docs.djangoproject.com/en/5.2/topics/auth/default/#django.contrib.auth.logout
        logout(info.context.request)

        return LogoutResult(
            message="User logged out successfully.",
            ok=True,
        )
