"""GraphQL node for Mentor model."""

import strawberry


@strawberry.type
class MentorNode:
    """A GraphQL node representing a mentorship mentor."""

    id: strawberry.ID

    @strawberry.field
    def avatar_url(self) -> str:
        """Get the GitHub avatar url of the mentor."""
        if not self.github_user:
            return ""
        return self.github_user.avatar_url

    @strawberry.field
    def name(self) -> str:
        """Get the GitHub name of the mentor."""
        if not self.github_user:
            return ""
        return self.github_user.name

    @strawberry.field
    def login(self) -> str:
        """Get the GitHub login of the mentor."""
        if not self.github_user:
            return ""
        return self.github_user.login
