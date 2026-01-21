"""GitHub user GraphQL node."""

import strawberry_django

from apps.github.models.user import User
from apps.nest.api.internal.nodes.badge import BadgeNode


@strawberry_django.type(
    User,
    fields=[
        "avatar_url",
        "bio",
        "company",
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

    @strawberry_django.field(prefetch_related=["user_badges"])
    def badge_count(self, root: User) -> int:
        """Resolve badge count."""
        return root.user_badges.filter(is_active=True).count()

    @strawberry_django.field(prefetch_related=["user_badges__badge"])
    def badges(self, root: User) -> list[BadgeNode]:
        """Return user badges."""
        user_badges = (
            root.user_badges.filter(
                is_active=True,
            )
            .select_related("badge")
            .order_by(
                "badge__weight",
                "badge__name",
            )
        )
        return [user_badge.badge for user_badge in user_badges]

    @strawberry_django.field
    def created_at(self, root: User) -> float:
        """Resolve created at."""
        return root.idx_created_at

    @strawberry_django.field(select_related=["owasp_profile"])
    def first_owasp_contribution_at(self, root: User) -> float | None:
        """Resolve first OWASP contribution date."""
        return (
            root.owasp_profile.first_contribution_at.timestamp()
            if hasattr(root, "owasp_profile") and root.owasp_profile.first_contribution_at
            else None
        )

    @strawberry_django.field(select_related=["owasp_profile"])
    def is_owasp_board_member(self, root: User) -> bool:
        """Resolve if member is currently on OWASP Board of Directors."""
        return (
            root.owasp_profile.is_owasp_board_member if hasattr(root, "owasp_profile") else False
        )

    @strawberry_django.field(select_related=["owasp_profile"])
    def is_former_owasp_staff(self, root: User) -> bool:
        """Resolve if member is a former OWASP staff member."""
        return (
            root.owasp_profile.is_former_owasp_staff if hasattr(root, "owasp_profile") else False
        )

    @strawberry_django.field(select_related=["owasp_profile"])
    def is_gsoc_mentor(self, root: User) -> bool:
        """Resolve if member is a Google Summer of Code mentor."""
        return root.owasp_profile.is_gsoc_mentor if hasattr(root, "owasp_profile") else False

    @strawberry_django.field
    def issues_count(self, root: User) -> int:
        """Resolve issues count."""
        return root.idx_issues_count

    @strawberry_django.field(select_related=["owasp_profile"])
    def linkedin_page_id(self, root: User) -> str:
        """Resolve LinkedIn page ID."""
        return (
            root.owasp_profile.linkedin_page_id
            if hasattr(root, "owasp_profile") and root.owasp_profile.linkedin_page_id
            else ""
        )

    @strawberry_django.field
    def releases_count(self, root: User) -> int:
        """Resolve releases count."""
        return root.idx_releases_count

    @strawberry_django.field
    def updated_at(self, root: User) -> float:
        """Resolve updated at."""
        return root.idx_updated_at

    @strawberry_django.field
    def url(self, root: User) -> str:
        """Resolve URL."""
        return root.url
