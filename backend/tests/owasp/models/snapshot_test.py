# import pytest

# from apps.owasp.models.snapshot import Snapshot


# class TestSnapshotModel:
#     @pytest.mark.parametrize(
#         ("start_at", "end_at", "status", "expected_str"),
#         [
#             (
#                 "2024-02-10 10:00:00",
#                 "2024-02-10 12:00:00",
#                 "pending",
#                 "Snapshot 2024-02-10 10:00:00 to 2024-02-10 12:00:00 (pending)",
#             ),
#             (
#                 "2024-02-11 14:00:00",
#                 "2024-02-11 16:00:00",
#                 "completed",
#                 "Snapshot 2024-02-11 14:00:00 to 2024-02-11 16:00:00 (completed)",
#             ),
#         ],
#     )
#     def test_str_representation(self, start_at, end_at, status, expected_str):
#         snapshot = Snapshot(start_at=start_at, end_at=end_at, status=status)
#         assert str(snapshot) == expected_str

#     def test_default_status(self):
#         """Ensure that default status is 'pending'."""
#         snapshot = Snapshot()
#         assert snapshot.status == Snapshot.Status.PENDING

#     def test_ordering(self):
#         """Ensure that snapshots are ordered by '-start_at'."""
#         assert Snapshot._meta.ordering == ["-start_at"]

#     def test_indexes(self):
#         """Check if indexes are correctly set."""
#         index_fields = [list(index.fields) for index in Snapshot._meta.indexes]
#         assert ["status"] in index_fields
#         assert ["start_at", "end_at"] in index_fields

import pytest
from django.utils.timezone import now

from apps.github.models.issue import Issue
from apps.github.models.release import Release
from apps.github.models.user import User
from apps.owasp.models.snapshot import Snapshot


@pytest.mark.django_db()
class TestSnapshotModel:
    @pytest.mark.parametrize(
        ("start_at", "end_at", "status", "expected_str"),
        [
            (
                "2024-02-10 10:00:00",
                "2024-02-10 12:00:00",
                "pending",
                "Snapshot 2024-02-10 10:00:00 to 2024-02-10 12:00:00 (pending)",
            ),
            (
                "2024-02-11 14:00:00",
                "2024-02-11 16:00:00",
                "completed",
                "Snapshot 2024-02-11 14:00:00 to 2024-02-11 16:00:00 (completed)",
            ),
        ],
    )
    def test_str_representation(self, start_at, end_at, status, expected_str):
        snapshot = Snapshot(start_at=start_at, end_at=end_at, status=status)
        assert str(snapshot) == expected_str

    def test_default_status(self):
        """Ensure that default status is 'pending'."""
        snapshot = Snapshot()
        assert snapshot.status == Snapshot.Status.PENDING

    def test_ordering(self):
        """Ensure that snapshots are ordered by '-start_at'."""
        assert Snapshot._meta.ordering == ["-start_at"]

    def test_indexes(self):
        """Check if indexes are correctly set."""
        index_fields = [list(index.fields) for index in Snapshot._meta.indexes]
        assert ["status"] in index_fields
        assert ["start_at", "end_at"] in index_fields

    def test_many_to_many_relationships(self, django_db_blocker):
        """Test that Snapshot correctly associates with Issues, Releases, and Users."""
        with django_db_blocker.unblock():
            snapshot = Snapshot.objects.create(start_at=now(), end_at=now())

            # Create dummy GitHub objects
            issue = Issue.objects.create(title="Bug Fix")
            release = Release.objects.create(version="v1.0.0")
            user = User.objects.create(username="dev123")

            # Add to Many-to-Many fields
            snapshot.new_issues.add(issue)
            snapshot.new_releases.add(release)
            snapshot.new_users.add(user)

            # Assertions
            assert snapshot.new_issues.count() == 1
            assert snapshot.new_releases.count() == 1
            assert snapshot.new_users.count() == 1

            assert issue in snapshot.new_issues.all()
            assert release in snapshot.new_releases.all()
            assert user in snapshot.new_users.all()
