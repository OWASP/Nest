"""GraphQL node for User model."""

import strawberry
import strawberry_django

from apps.nest.models import User
from apps.nest.models.badge import Badge

from .badge import BadgeNode


@strawberry_django.type(User, fields=["username"])
class AuthUserNode(strawberry.relay.Node):
    """GraphQL node for User model."""

    @strawberry_django.field
    def is_owasp_staff(self) -> bool:
        """Check if the user is an OWASP staff member."""
        return self.github_user.is_owasp_staff if self.github_user else False

    @strawberry_django.field
    def badges(self) -> list[BadgeNode]:
        """List badges assigned to the user sorted by weight and name."""
        return Badge.objects.filter(userbadge__user=self.instance).order_by("weight", "name")
