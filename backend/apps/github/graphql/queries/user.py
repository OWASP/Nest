"""OWASP user GraphQL queries."""

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.github.graphql.nodes.user import UserNode
from apps.github.models.user import User


class UserQuery(BaseQuery):
    """User queries."""

    user = graphene.Field(UserNode, login=graphene.String(required=True))

    def resolve_user(root, info, login):
        """Resolve user by login."""
        try:
            return User.objects.get(login=login)
        except User.DoesNotExist:
            return None
