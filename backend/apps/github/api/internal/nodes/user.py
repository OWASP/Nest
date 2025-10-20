"""GitHub user GraphQL node."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django

from apps.github.models.user import User

if TYPE_CHECKING:
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

    @strawberry.field
    def badge_count(self) -> int:
        """Resolve badge count."""
        return self.user_badges.filter(is_active=True).count()

    @strawberry.field
    def badges(
        self,
    ) -> list[Annotated[BadgeNode, strawberry.lazy("apps.nest.api.internal.nodes.badge")]]:
        """Return user badges."""
        user_badges = (
            self.user_badges.filter(
                is_active=True,
            )
            .select_related(
                "badge",
            )
            .order_by(
                "badge__weight",
                "badge__name",
            )
        )
        return [user_badge.badge for user_badge in user_badges]

    @strawberry.field
    def created_at(self) -> float:
        """Resolve created at."""
        return self.idx_created_at

    @strawberry.field
    def first_owasp_contribution_at(self) -> float | None:
        """Resolve first OWASP contribution date."""
        if hasattr(self, "owasp_profile") and self.owasp_profile.first_contribution_at:
            return self.owasp_profile.first_contribution_at.timestamp()
        return None

    @strawberry.field
    def issues_count(self) -> int:
        """Resolve issues count."""
        return self.idx_issues_count

    @strawberry.field
    def releases_count(self) -> int:
        """Resolve releases count."""
        return self.idx_releases_count

    @strawberry.field
    def updated_at(self) -> float:
        """Resolve updated at."""
        return self.idx_updated_at

    @strawberry.field
    def url(self) -> str:
        """Resolve URL."""
        return self.url
