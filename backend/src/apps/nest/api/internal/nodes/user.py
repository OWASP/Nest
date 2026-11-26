"""GraphQL node for User model."""

from typing import TYPE_CHECKING

import strawberry
import strawberry_django

from apps.nest.models import User

if TYPE_CHECKING:
    from apps.github.models.user import User as GitHubUser
    
@strawberry_django.type(User, fields=["username"])
class AuthUserNode(strawberry.relay.Node):
    """GraphQL node for User model."""
    github_user: GitHubUser | None

    @strawberry_django.field
    def is_owasp_staff(self) -> bool:
        """Check if the user is an OWASP staff member."""
        return self.github_user.is_owasp_staff if self.github_user else False
