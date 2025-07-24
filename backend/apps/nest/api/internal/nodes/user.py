"""GraphQL node for User model."""

import strawberry_django

from apps.nest.models import User


@strawberry_django.type(User, fields=["username"])
class AuthUserNode:
    """GraphQL node for User model."""
