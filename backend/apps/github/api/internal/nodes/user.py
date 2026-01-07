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

    @strawberry_django.field
    def badge_count(self) -> int:
        """Resolve badge count."""
        return self.user_badges.filter(is_active=True).count()

    @strawberry_django.field(select_related=["badge"])
    def badges(self) -> list[BadgeNode]:
        """Return user badges."""
        user_badges = self.user_badges.filter(
            is_active=True,
        ).order_by(
            "badge__weight",
            "badge__name",
        )
        return [user_badge.badge for user_badge in user_badges]

    @strawberry.field
    def created_at(self) -> float:
        """Resolve created at."""
        return self.idx_created_at

    @strawberry_django.field
    def first_owasp_contribution_at(self) -> float | None:
        """Resolve first OWASP contribution date."""
        if hasattr(self, "owasp_profile") and self.owasp_profile.first_contribution_at:
            return self.owasp_profile.first_contribution_at.timestamp()
        return None

    @strawberry_django.field
    def is_owasp_board_member(self) -> bool:
        """Resolve if member is currently on OWASP Board of Directors."""
        if hasattr(self, "owasp_profile"):
            return self.owasp_profile.is_owasp_board_member
        return False

    @strawberry_django.field
    def is_former_owasp_staff(self) -> bool:
        """Resolve if member is a former OWASP staff member."""
        if hasattr(self, "owasp_profile"):
            return self.owasp_profile.is_former_owasp_staff
        return False

    @strawberry_django.field
    def is_gsoc_mentor(self) -> bool:
        """Resolve if member is a Google Summer of Code mentor."""
        if hasattr(self, "owasp_profile"):
            return self.owasp_profile.is_gsoc_mentor
        return False

    @strawberry.field
    def issues_count(self) -> int:
        """Resolve issues count."""
        return self.idx_issues_count

    @strawberry.field
    def linkedin_page_id(self) -> str:
        """Resolve LinkedIn page ID."""
        if hasattr(self, "owasp_profile") and self.owasp_profile.linkedin_page_id:
            return self.owasp_profile.linkedin_page_id
        return ""

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
