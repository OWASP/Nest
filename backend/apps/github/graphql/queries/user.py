"""OWASP user GraphQL queries."""

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.github.graphql.nodes.repository import RepositoryNode
from apps.github.graphql.nodes.user import UserNode
from apps.github.models.repository_contributor import RepositoryContributor
from apps.github.models.user import User


class UserQuery(BaseQuery):
    """User queries."""

    top_contributed_repositories = graphene.List(
        RepositoryNode,
        login=graphene.String(required=True),
    )
    user = graphene.Field(
        UserNode,
        login=graphene.String(required=True),
    )

    def resolve_top_contributed_repositories(root, info, login):
        """Resolve user top repositories.

        Args:
            root (Any): The root query object.
            info (ResolveInfo): The GraphQL execution context.
            login (str): The login of the user.

        Returns:
            list: List of repositories the user has contributed to.

        """
        return [
            rc.repository
            for rc in RepositoryContributor.objects.select_related("repository")
            .filter(user__login=login)
            .order_by("-contributions_count")
        ]

    def resolve_user(root, info, login):
        """Resolve user by login.

        Args:
            root (Any): The root query object.
            info (ResolveInfo): The GraphQL execution context.
            login (str): The login of the user.

        Returns:
            User or None: The user object if found, otherwise None.

        """
        try:
            return User.objects.get(login=login)
        except User.DoesNotExist:
            return None
