from datetime import datetime, timezone

import pytest

from apps.github.models.issue import Issue
from apps.github.models.release import Release
from apps.github.models.user import User
from apps.owasp.models.snapshot import Snapshot


class TestSnapshotModel:
    """Test cases for the Snapshot model."""

    @pytest.mark.parametrize(
        ("start_at", "end_at", "status", "expected_str"),
        [
            (
                datetime(2024, 2, 10, 10, 0, 0, tzinfo=timezone.utc),
                datetime(2024, 2, 10, 12, 0, 0, tzinfo=timezone.utc),
                "pending",
                "Snapshot 2024-02-10 10:00:00+00:00 to 2024-02-10 12:00:00+00:00 (pending)",
            ),
            (
                datetime(2024, 2, 11, 14, 0, 0, tzinfo=timezone.utc),
                datetime(2024, 2, 11, 16, 0, 0, tzinfo=timezone.utc),
                "completed",
                "Snapshot 2024-02-11 14:00:00+00:00 to 2024-02-11 16:00:00+00:00 (completed)",
            ),
        ],
    )
    def test_str_representation(self, start_at, end_at, status, expected_str):
        """Test the string representation of Snapshot."""
        snapshot = Snapshot(start_at=start_at, end_at=end_at, status=status)
        assert str(snapshot) == expected_str

    def test_default_status(self):
        """Ensure that default status is 'pending'."""
        snapshot = Snapshot(
            start_at=datetime(2024, 2, 10, 10, 0, 0, tzinfo=timezone.utc),
            end_at=datetime(2024, 2, 10, 12, 0, 0, tzinfo=timezone.utc),
        )
        assert snapshot.status == "pending"

    def test_ordering(self):
        """Ensure that snapshots are ordered by '-start_at'."""
        assert Snapshot._meta.ordering == ["-start_at"]

    def test_indexes(self):
        """Check if indexes are correctly set in the model metadata."""
        index_fields = [{tuple(index.fields)} for index in Snapshot._meta.indexes]
        assert {"status"} in index_fields
        assert {"start_at", "end_at"} in index_fields

    def test_many_to_many_relationships(self):
        """Test that Snapshot correctly associates with Issues, Releases, and Users."""
        snapshot = Snapshot(
            start_at=datetime(2024, 2, 10, 10, 0, 0, tzinfo=timezone.utc),
            end_at=datetime(2024, 2, 10, 12, 0, 0, tzinfo=timezone.utc),
        )

        issue = Issue(title="Test Issue")
        release = Release(version="1.0.0")
        user = User(username="testuser")

        # Mock Many-to-Many Fields without DB
        snapshot.new_issues.set([issue])
        snapshot.new_releases.set([release])
        snapshot.new_users.set([user])

        assert len(snapshot.new_issues.all()) == 1
        assert len(snapshot.new_releases.all()) == 1
        assert len(snapshot.new_users.all()) == 1
