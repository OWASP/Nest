"""Nest user GraphQL Mutations."""

import requests
import strawberry

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
        response = requests.post(
            "https://api.github.com/graphql",
            json={
                "query": """query {
                    viewer {
                        id
                        login
                    }
                }"""
            },
            headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
            timeout=5,
        )
        response.raise_for_status()
        github_user = response.json()["data"]["viewer"]
        existing_user = User.objects.filter(github_id=github_user["id"]).first()
        if existing_user:
            auth_user = existing_user
        else:
            auth_user = User.objects.create(
                github_id=github_user["id"],
                username=github_user["login"],
            )
        return GitHubAuthResult(auth_user=auth_user)
