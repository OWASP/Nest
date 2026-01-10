"""OWASP snapshot GraphQL queries."""

import strawberry
import strawberry_django

from apps.owasp.api.internal.nodes.snapshot import SnapshotNode
from apps.owasp.models.snapshot import Snapshot

MAX_LIMIT = 1000


@strawberry.type
class SnapshotQuery:
    """Snapshot queries."""

    @strawberry_django.field
    def snapshot(self, key: str) -> SnapshotNode | None:
        """Resolve snapshot by key."""
        try:
            return Snapshot.objects.get(
                key=key,
                status=Snapshot.Status.COMPLETED,
            )
        except Snapshot.DoesNotExist:
            return None

    @strawberry_django.field(
        prefetch_related=[
            "new_users__owasp_profile",
            "new_users__user_badges__badge",
            "new_releases__repository__organization",
            "new_releases__repository__owner__owasp_profile",
            "new_releases__author__owasp_profile",
            "new_releases__author__user_badges__badge",
            "new_chapters__owasp_repository__organization",
            "new_chapters__owasp_repository__owner__owasp_profile",
            "new_chapters__leaders__owasp_profile",
            "new_chapters__suggested_leaders__owasp_profile",
            "new_projects__owasp_repository__organization",
            "new_projects__owasp_repository__owner__owasp_profile",
            "new_projects__owners__owasp_profile",
            "new_projects__organizations",
            "new_projects__repositories__organization",
            "new_projects__repositories__owner__owasp_profile",
            "new_projects__published_releases__repository__organization",
            "new_projects__published_releases__author__owasp_profile",
            "new_projects__published_releases__author__user_badges__badge",
            "new_issues__author__owasp_profile",
            "new_issues__author__user_badges__badge",
            "new_issues__repository__organization",
            "new_issues__repository__owner__owasp_profile",
            "new_issues__milestone__author__owasp_profile",
            "new_issues__milestone__repository__organization",
            "new_issues__milestone__repository__owner__owasp_profile",
            "new_issues__labels",
            "new_issues__assignees__owasp_profile",
            "new_issues__assignees__user_badges__badge",
            "new_issues__participant_interests__user__owasp_profile",
            "new_issues__participant_interests__user__user_badges__badge",
            "new_issues__pull_requests__author__owasp_profile",
            "new_issues__pull_requests__author__user_badges__badge",
            "new_issues__pull_requests__repository__organization",
            "new_issues__pull_requests__repository__owner__owasp_profile",
            "new_issues__pull_requests__milestone__author__owasp_profile",
            "new_issues__pull_requests__milestone__repository__organization",
            "new_issues__pull_requests__milestone__repository__owner__owasp_profile",
            "new_issues__pull_requests__labels",
            "new_issues__pull_requests__assignees__owasp_profile",
            "new_pull_requests__author__owasp_profile",
            "new_pull_requests__repository__organization",
            "new_pull_requests__repository__owner__owasp_profile",
            "new_pull_requests__milestone__author__owasp_profile",
            "new_pull_requests__milestone__repository__organization",
            "new_pull_requests__milestone__repository__owner__owasp_profile",
            "new_pull_requests__labels",
            "new_pull_requests__assignees__owasp_profile",
            "new_pull_requests__related_issues__author__owasp_profile",
            "new_pull_requests__related_issues__repository__organization",
            "new_pull_requests__related_issues__repository__owner__owasp_profile",
            "new_pull_requests__related_issues__milestone__author__owasp_profile",
            "new_pull_requests__related_issues__milestone__repository__organization",
            "new_pull_requests__related_issues__milestone__repository__owner__owasp_profile",
        ]
    )
    def snapshots(self, limit: int = 12) -> list[SnapshotNode]:
        """Resolve snapshots."""
        return (
            Snapshot.objects.filter(
                status=Snapshot.Status.COMPLETED,
            ).order_by(
                "-created_at",
            )[:limit]
            if (limit := min(limit, MAX_LIMIT)) > 0
            else []
        )
