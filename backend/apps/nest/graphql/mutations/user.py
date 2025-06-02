"""Nest user GraphQL Mutations."""

import requests
import strawberry
from github import Github

from apps.nest.graphql.nodes.user import AuthUserNode
from apps.nest.models import User


@strawberry.type
class GitHubAuthResult:
    """Payload for GitHubAuth mutation."""

    auth_user: AuthUserNode | None


@strawberry.type
class UserMutations:
    """GraphQL mutations related to user."""

    @strawberry.mutation
    def github_auth(self, info, access_token: str) -> GitHubAuthResult:
        """Authenticate via GitHub OAuth2."""
        try:
            github = Github(access_token)
            user = github.get_user()
            github_user = {"id": user.id, "login": user.login, "email": user.email}

            existing_user = User.objects.filter(github_id=github_user["id"]).first()
            if existing_user:
                auth_user = existing_user
            else:
                auth_user = User.objects.create(
                    github_id=github_user["id"],
                    username=github_user["login"],
                    email=github_user.get("email"),
                )
            return GitHubAuthResult(auth_user=auth_user)
        except requests.exceptions.RequestException:
            return GitHubAuthResult(auth_user=None)
