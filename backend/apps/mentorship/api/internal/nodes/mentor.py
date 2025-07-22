"""GraphQL node for Mentor model."""

import strawberry


@strawberry.type
class MentorNode:
    """A GraphQL node representing a mentorship mentor."""

    id: strawberry.ID

    @strawberry.field
    def avatar_url(self) -> str:
        """Get the GitHub avatar URL of the mentor."""
        return self.github_user.avatar_url if self.github_user else ""

    @strawberry.field
    def name(self) -> str:
        """Get the GitHub name of the mentor."""
        return self.github_user.name if self.github_user else ""

    @strawberry.field
    def login(self) -> str:
        """Get the GitHub login of the mentor."""
        return self.github_user.login if self.github_user else ""
