"""Nest user GraphQL queries."""

import graphene
import requests
from django.db import transaction

from apps.nest.graphql.nodes.user import AuthUserNode
from apps.nest.models import User


class GitHubAuth(graphene.Mutation):
    """Authenticate via GitHub OAuth2."""

    class Arguments:
        """Arguments for GitHub authentication."""

        access_token = graphene.String(required=True)

    auth_user = graphene.Field(AuthUserNode)

    @transaction.atomic
    def mutate(self, info, access_token):
        """Mutate method for user authentication."""
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

        return GitHubAuth(auth_user=auth_user)


class AuthUserMutation(graphene.ObjectType):
    """GraphQL root mutation for users."""

    github_auth = GitHubAuth.Field()
