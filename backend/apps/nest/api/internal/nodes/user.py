"""GraphQL node for User model."""

import strawberry_django

from apps.nest.models import User


@strawberry_django.type(User, fields=["username"])
class AuthUserNode:
    """GraphQL node for User model."""

    @strawberry_django.field
    def is_owasp_staff(self) -> bool:
        """Check if the user is an OWASP staff member."""
        return self.github_user.is_owasp_staff if self.github_user else False
