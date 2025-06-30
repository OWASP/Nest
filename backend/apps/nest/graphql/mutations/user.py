"""Nest user GraphQL Mutations."""

import logging

import requests
import strawberry
from github import Github

from apps.github.models import User as GithubUser
from apps.nest.graphql.nodes.user import AuthUserNode
from apps.nest.models import User
from apps.owasp.models import Project

logger = logging.getLogger(__name__)


@strawberry.type
class GitHubAuthResult:
    """Payload for GitHubAuth mutation."""

    auth_user: AuthUserNode | None


@strawberry.type
class UserMutations:
    """GraphQL mutations related to user."""

    @strawberry.mutation
    def github_auth(self, access_token: str) -> GitHubAuthResult:
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

            role = "contributor"
            gh_username = gh_user.login.lower()
            gh_full_name = (gh_user.name or "").lower()

            for project in Project.objects.all():
                for leader in project.leaders_raw or []:
                    if leader.lower() in {gh_username, gh_full_name}:
                        role = "mentor"
                        break
                if role == "mentor":
                    break

            auth_user, created = User.objects.get_or_create(
                username=gh_user.login,
                defaults={
                    "email": gh_user_email,
                    "github_user": github_user,
                    "role": role,
                },
            )

            if not created and auth_user.role != role:
                auth_user.role = role
                auth_user.save(update_fields=["role"])

            return GitHubAuthResult(auth_user=auth_user)

        except requests.exceptions.RequestException as e:
            logger.warning("GitHub request failed: %s", e)

        return GitHubAuthResult(auth_user=None)
