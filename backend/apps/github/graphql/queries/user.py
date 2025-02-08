"""OWASP github GraphQL queries."""

import graphene

from apps.common.graphql.queries import BaseQuery
from apps.github.graphql.nodes.user import UserNode
from apps.github.models.user import User


class UserQuery(BaseQuery):
    """User queries."""

    user = graphene.Field(UserNode, key=graphene.String(required=True))

    def resolve_user(root, info, key):
        """Resolve user by login."""
        try:
            return User.objects.get(key=key)
        except User.DoesNotExist:
            return None