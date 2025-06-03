"""Nest user GraphQL Mutations."""

import requests
import strawberry
from github import Github

from apps.github.models import User as GithubUser
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
            gh_user = github.get_user()

            github_user = GithubUser.update_data(gh_user)
            if not github_user:
                return GitHubAuthResult(auth_user=None)

            try:
                auth_user = User.objects.get(github_id=gh_user.id)
            except User.DoesNotExist:
                auth_user = User.objects.create(
                    github_id=str(gh_user.id),
                    github_user=github_user,
                    username=gh_user.login,
                )

            return GitHubAuthResult(auth_user=auth_user)

        except requests.exceptions.RequestException:
            return GitHubAuthResult(auth_user=None)
