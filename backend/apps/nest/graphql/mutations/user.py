"""Nest user GraphQL Mutations."""

import logging

import requests
import strawberry
from django.contrib.auth import login, logout
from github import Github

from apps.github.models import User as GithubUser
from apps.nest.graphql.nodes.user import AuthUserNode
from apps.nest.graphql.permissions import IsAuthenticated
from apps.nest.models import User

logger = logging.getLogger(__name__)


@strawberry.type
class GitHubAuthResult:
    """Payload for GitHubAuth mutation."""

    auth_user: AuthUserNode | None


@strawberry.type
class UserMutations:
    """GraphQL mutations related to user."""

    @strawberry.mutation
    def github_auth(self, info: strawberry.Info, access_token: str) -> GitHubAuthResult:
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
                logger.info(
                    "User %s successfully logged into Django session.",
                    auth_user.username,
                )

            return GitHubAuthResult(auth_user=auth_user)

        except requests.exceptions.RequestException as e:
            logger.warning("GitHub authentication failed: %s", e)
            return GitHubAuthResult(auth_user=None)

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def logout_user(self, info: strawberry.Info) -> bool:
        """Log the current user out of their Django session."""
        try:
            if info.context.request.user.is_authenticated:
                logger.info("User %s is logging out.", info.context.request.user.username)
                logout(info.context.request)
            else:
                return False
        except Exception:
            logger.exception("Logout failed")
            return False
        return True
