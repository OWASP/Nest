"""GraphQL node for Mentee model."""

import strawberry

from apps.mentorship.api.internal.nodes.enum import ExperienceLevelEnum


@strawberry.type
class MenteeNode:
    """A GraphQL node representing a mentorship mentee."""

    id: str
    login: str
    name: str
    avatar_url: str
    bio: str | None = None
    experience_level: ExperienceLevelEnum
    domains: list[str] | None = None
    tags: list[str] | None = None

    @strawberry.field(name="avatarUrl")
    def resolve_avatar_url(self) -> str:
        """Get the GitHub avatar URL of the mentee."""
        return self.avatar_url

    @strawberry.field(name="experienceLevel")
    def resolve_experience_level(self) -> str:
        """Get the experience level of the mentee."""
        return self.experience_level if self.experience_level else "beginner"
