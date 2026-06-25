"""GraphQL node for Admin model."""

import strawberry
import strawberry_django
from asgiref.sync import sync_to_async

from apps.mentorship.models.admin import Admin


@strawberry.type
class AdminNode:
    """A GraphQL node representing a mentorship admin."""

    id: strawberry.ID

    @strawberry_django.field(name="avatarUrl", select_related=["github_user"])
    async def avatar_url(self, root: Admin) -> str:
        """Get the GitHub avatar URL of the admin."""
        user = await sync_to_async(lambda: root.github_user)()
        return user.avatar_url if user else ""

    @strawberry_django.field(select_related=["github_user"])
    async def login(self, root: Admin) -> str:
        """Get the GitHub login of the admin."""
        user = await sync_to_async(lambda: root.github_user)()
        return user.login if user else ""

    @strawberry_django.field(select_related=["github_user"])
    async def name(self, root: Admin) -> str:
        """Get the GitHub name of the admin."""
        user = await sync_to_async(lambda: root.github_user)()
        return user.name if user else ""
