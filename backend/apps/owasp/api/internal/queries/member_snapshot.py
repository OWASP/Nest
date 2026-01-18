"""OWASP member snapshot GraphQL queries."""

import strawberry
import strawberry_django

from apps.github.models.user import User
from apps.owasp.api.internal.nodes.member_snapshot import MemberSnapshotNode
from apps.owasp.models.member_snapshot import MemberSnapshot

MAX_LIMIT = 1000


@strawberry.type
class MemberSnapshotQuery:
    """GraphQL queries for MemberSnapshot model."""

    @strawberry_django.field
    def member_snapshot(
        self, user_login: str, start_year: int | None = None
    ) -> MemberSnapshotNode | None:
        """Resolve member snapshot by user login and optional year.

        Args:
            user_login: GitHub username
            start_year: Optional year filter (filters by start_at year)

        Returns:
            MemberSnapshotNode or None if not found

        """
        try:
            user = User.objects.get(login=user_login)

            query = (
                MemberSnapshot.objects.select_related("github_user")
                .prefetch_related("issues", "pull_requests", "messages")
                .filter(github_user=user)
            )

            if start_year:
                query = query.filter(start_at__year=start_year)

            return query.order_by("-start_at").first()

        except User.DoesNotExist:
            return None

    @strawberry_django.field(
        select_related=["github_user__owasp_profile", "github_user__user_badges__badge"],
        prefetch_related=["issues", "pull_requests", "messages"],
    )
    def member_snapshots(
        self, user_login: str | None = None, limit: int = 10
    ) -> list[MemberSnapshotNode]:
        """Resolve member snapshots with optional filtering.

        Args:
            user_login: Optional filter by GitHub username
            limit: Maximum number of snapshots to return (default: 10)

        Returns:
            List of MemberSnapshotNode objects

        """
        snapshots = MemberSnapshot.objects.all().select_related("github_user")

        if user_login:
            try:
                snapshots = snapshots.filter(github_user=User.objects.get(login=user_login))
            except User.DoesNotExist:
                return []

        return (
            snapshots.order_by("-start_at")[:limit] if (limit := min(limit, MAX_LIMIT)) > 0 else []
        )
