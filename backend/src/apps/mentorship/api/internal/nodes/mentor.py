"""GraphQL node for Mentor model."""

import strawberry
import strawberry_django
from asgiref.sync import sync_to_async

from apps.mentorship.models.mentor import Mentor


@strawberry.type
class MentorNode:
    """A GraphQL node representing a mentorship mentor."""

    id: strawberry.ID

    @strawberry_django.field(select_related=["github_user"])
    async def avatar_url(self, root: Mentor) -> str:
        """Get the GitHub avatar URL of the mentor."""
        return user.avatar_url if (user := await sync_to_async(lambda: root.github_user)()) else ""

    @strawberry_django.field(select_related=["github_user"])
    async def name(self, root: Mentor) -> str:
        """Get the GitHub name of the mentor."""
        return user.name if (user := await sync_to_async(lambda: root.github_user)()) else ""

    @strawberry_django.field(select_related=["github_user"])
    async def login(self, root: Mentor) -> str:
        """Get the GitHub login of the mentor."""
        return user.login if (user := await sync_to_async(lambda: root.github_user)()) else ""
