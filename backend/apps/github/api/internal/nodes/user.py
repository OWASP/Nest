"""GitHub user GraphQL node."""

import strawberry
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

    @strawberry.field
    def badges(self) -> list[BadgeNode]:
        """List badges assigned to the user sorted by weight and name."""
        user_badges = self.badges.filter(is_active=True).select_related("badge")
        return [user_badge.badge for user_badge in user_badges]

    @strawberry.field
    def badge_count(self) -> int:
        """Resolve badge count."""
        return self.badges.filter(is_active=True).count()

    @strawberry.field
    def created_at(self) -> float:
        """Resolve created at."""
        return self.idx_created_at

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
