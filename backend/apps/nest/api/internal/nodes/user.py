"""GraphQL node for User model."""

import strawberry
import strawberry_django

from apps.nest.models import User


@strawberry_django.type(User, fields=["username"])
class AuthUserNode(strawberry.relay.Node):
    """GraphQL node for User model."""

    @strawberry_django.field
    def is_owasp_staff(self) -> bool:
        """Check if the user is an OWASP staff member."""
        if self.github_user and hasattr(self.github_user, "owasp_profile"):
            return self.github_user.owasp_profile.is_owasp_staff
        return False
