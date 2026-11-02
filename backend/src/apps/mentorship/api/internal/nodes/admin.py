"""GraphQL node for Admin model."""

from typing import TYPE_CHECKING

import strawberry

if TYPE_CHECKING:
    from apps.github.models.user import User as GitHubUser

@strawberry.type
class AdminNode:
    """A GraphQL node representing a mentorship admin."""

    id: strawberry.ID
    github_user: GitHubUser | None

    @strawberry.field(name="avatarUrl")
    def avatar_url(self) -> str:
        """Get the GitHub avatar URL of the admin."""
        return self.github_user.avatar_url if self.github_user else ""

    @strawberry.field
    def login(self) -> str:
        """Get the GitHub login of the admin."""
        return self.github_user.login if self.github_user else ""

    @strawberry.field
    def name(self) -> str:
        """Get the GitHub name of the admin."""
        return self.github_user.name if self.github_user else ""
