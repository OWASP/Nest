"""OWASP member snapshot GraphQL queries."""

import strawberry

from apps.github.models.user import User
from apps.owasp.api.internal.nodes.member_snapshot import MemberSnapshotNode
from apps.owasp.models.member_snapshot import MemberSnapshot


@strawberry.type
class MemberSnapshotQuery:
    """GraphQL queries for MemberSnapshot model."""

    @strawberry.field
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

            query = MemberSnapshot.objects.filter(github_user=user)

            if start_year:
                query = query.filter(start_at__year=start_year)

            return query.order_by("-start_at").first()

        except User.DoesNotExist:
            return None

    @strawberry.field
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
        query = MemberSnapshot.objects.all()

        if user_login:
            try:
                user = User.objects.get(login=user_login)
                query = query.filter(github_user=user)
            except User.DoesNotExist:
                return []

        return query.order_by("-start_at")[:limit] if limit > 0 else []
