"""GraphQL node for Mentee model."""

import strawberry
import strawberry_django

from apps.mentorship.api.internal.nodes.enum import ExperienceLevelEnum
from apps.mentorship.models.mentee import Mentee


@strawberry_django.type(Mentee)
class MenteeNode(strawberry.relay.Node):
    """A GraphQL node representing a mentorship mentee."""

    experience_level: ExperienceLevelEnum
    domains: list[str] | None
    tags: list[str] | None

    @strawberry_django.field
    def avatar_url(self, root: Mentee) -> str:
        """Get the GitHub avatar URL of the mentee."""
        return root.github_user.avatar_url

    @strawberry_django.field
    def bio(self, root: Mentee) -> str | None:
        """Resolve bio."""
        return root.github_user.bio

    @strawberry_django.field
    def login(self, root: Mentee) -> str:
        """Resolve login."""
        return root.github_user.login

    @strawberry_django.field
    def name(self, root: Mentee) -> str:
        """Resolve name."""
        return root.github_user.name or root.github_user.login
