import graphene
import requests
from django.db import transaction
from apps.nest.models import User
from apps.nest.graphql.nodes.user import AuthUserNode

class GitHubAuth(graphene.Mutation):
    """Authenticate via GitHub (returns username only)"""
    
    class Arguments:
        access_token = graphene.String(required=True)

    auth_user = graphene.Field(AuthUserNode)

    @transaction.atomic
    def mutate(self, info, access_token):
        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": """query {
                viewer {
                    id
                    login
                    name
                    email
                    avatarUrl
                    url
                }
            }"""},
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            }
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
            name=github_user.get("name") or github_user["login"],
            email=github_user.get("email"),
            avatar_url=github_user.get("avatarUrl"),
            github_profile=github_user.get("url"),
            )

        return GitHubAuth(auth_user=auth_user)

class AuthUserQuery(graphene.ObjectType):
    """GraphQL root query for users."""
    github_auth = GitHubAuth.Field()
