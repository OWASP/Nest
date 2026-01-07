"""GraphQL node for Mentee model."""

import strawberry

from apps.mentorship.api.internal.nodes.enum import ExperienceLevelEnum


@strawberry.type
class MenteeNode:
    """A GraphQL node representing a mentorship mentee."""

    # TODO (@arkid15r): migrate to decorator for consistency.
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
        """
        Return the mentee's experience level, defaulting to "beginner" when not set.
        
        Returns:
            experience_level (str): The mentee's experience level, or "beginner" if the field is empty or falsy.
        """
        return self.experience_level if self.experience_level else "beginner"