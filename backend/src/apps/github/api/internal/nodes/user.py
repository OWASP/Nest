"""GitHub user GraphQL node."""

import strawberry_django
from django.db.models.query import Prefetch
from strawberry.types.info import Info

from apps.github.api.internal.dataloaders.user import (
    USER_BADGES_BY_USER_ID_LOADER,
    USER_ISSUES_COUNT_LOADER,
    USER_RELEASES_COUNT_LOADER,
)
from apps.github.models.user import User
from apps.nest.api.internal.nodes.badge import BadgeNode
from apps.nest.models.user_badge import UserBadge

USER_BADGES_PREFETCH = Prefetch(
    "user_badges",
    queryset=UserBadge.objects.filter(is_active=True)
    .select_related("badge")
    .order_by(
        "badge__weight",
        "badge__name",
    ),
    to_attr="user_badges_list",
)


@strawberry_django.type(
    User,
    fields=[
        "avatar_url",
        "bio",
        "company",
        "contribution_data",
        "contributions_count",
        "email",
        "followers_count",
        "following_count",
        "id",
        "is_owasp_staff",
        "location",
        "login",
        "name",
        "public_repositories_count",
    ],
)
class UserNode:
    """GitHub user node."""

    @strawberry_django.field
    async def badges(self, root: User, info: Info) -> list[BadgeNode]:
        """Return user badges."""
        return await info.context.github_dataloaders[USER_BADGES_BY_USER_ID_LOADER].load(root.pk)

    @strawberry_django.field(only=["created_at"])
    def created_at(self, root: User) -> str:
        """Resolve created at."""
        return root.idx_created_at

    @strawberry_django.field(
        select_related=["owasp_profile"], only=["owasp_profile__first_contribution_at"]
    )
    def first_owasp_contribution_at(self, root: User) -> str | None:
        """Resolve first OWASP contribution date."""
        return (
            root.owasp_profile.first_contribution_at.isoformat()
            if hasattr(root, "owasp_profile") and root.owasp_profile.first_contribution_at
            else None
        )

    @strawberry_django.field(
        select_related=["owasp_profile"], only=["owasp_profile__is_owasp_board_member"]
    )
    def is_owasp_board_member(self, root: User) -> bool:
        """Resolve if member is currently on OWASP Board of Directors."""
        return (
            root.owasp_profile.is_owasp_board_member if hasattr(root, "owasp_profile") else False
        )

    @strawberry_django.field(
        select_related=["owasp_profile"], only=["owasp_profile__is_former_owasp_staff"]
    )
    def is_former_owasp_staff(self, root: User) -> bool:
        """Resolve if member is a former OWASP staff member."""
        return (
            root.owasp_profile.is_former_owasp_staff if hasattr(root, "owasp_profile") else False
        )

    @strawberry_django.field(
        select_related=["owasp_profile"], only=["owasp_profile__is_gsoc_mentor"]
    )
    def is_gsoc_mentor(self, root: User) -> bool:
        """Resolve if member is a Google Summer of Code mentor."""
        return root.owasp_profile.is_gsoc_mentor if hasattr(root, "owasp_profile") else False

    @strawberry_django.field
    async def issues_count(self, root: User, info: Info) -> int:
        """Resolve issues count."""
        return await info.context.github_dataloaders[USER_ISSUES_COUNT_LOADER].load(root.pk)

    @strawberry_django.field(
        select_related=["owasp_profile"], only=["owasp_profile__linkedin_page_id"]
    )
    def linkedin_page_id(self, root: User) -> str:
        """Resolve LinkedIn page ID."""
        return (
            root.owasp_profile.linkedin_page_id
            if hasattr(root, "owasp_profile") and root.owasp_profile.linkedin_page_id
            else ""
        )

    @strawberry_django.field
    async def releases_count(self, root: User, info: Info) -> int:
        """Resolve releases count."""
        return await info.context.github_dataloaders[USER_RELEASES_COUNT_LOADER].load(root.pk)

    @strawberry_django.field(only=["updated_at"])
    def updated_at(self, root: User) -> str:
        """Resolve updated at."""
        return root.idx_updated_at

    @strawberry_django.field(only=["login"])
    def url(self, root: User) -> str:
        """Resolve URL."""
        return root.url
