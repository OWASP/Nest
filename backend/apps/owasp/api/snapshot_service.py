"""API service module for handling snapshot-related functionality in OWASP."""

from datetime import timedelta

from django.utils import timezone

from apps.owasp.models import snapshot


class SnapshotService:
    """Service class for managing snapshot-related operations."""

    @staticmethod
    def create_snapshot(start_at=None, end_at=None):
        """Create a new snapshot with the given time range or default to last 24 hours."""
        if not start_at:
            end_at = timezone.now()
            start_at = end_at - timedelta(days=1)

        return snapshot.objects.create(
            start_at=start_at, end_at=end_at, status=snapshot.Status.PENDING
        )

    @staticmethod
    def get_latest_snapshot():
        """Get the most recent completed snapshot."""
        return snapshot.objects.filter(status=snapshot.Status.COMPLETED).first()

    @staticmethod
    def get_snapshot_statistics(snapshot):
        """Get statistics for a snapshot."""
        return {
            "new_chapters": snapshot.new_chapters.count(),
            "new_projects": snapshot.new_projects.count(),
            "new_issues": snapshot.new_issues.count(),
            "new_releases": snapshot.new_releases.count(),
            "new_users": snapshot.new_users.count(),
            "period": {
                "start": snapshot.start_at,
                "end": snapshot.end_at,
            },
        }
