import pytest
from django.utils.timezone import now, timedelta

from apps.github.models.issue import Issue
from apps.github.models.release import Release
from apps.github.models.user import User
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.project import Project
from apps.owasp.models.snapshot import Snapshot


class TestSnapshotModel:
    @pytest.mark.parametrize(
        ("start_at", "end_at", "status", "expected_str"),
        [
            (
                "2024-02-10 10:00:00+00:00",
                "2024-02-10 12:00:00+00:00",
                "pending",
                "Snapshot 2024-02-10 10:00:00+00:00 to 2024-02-10 12:00:00+00:00 (pending)",
            ),
            (
                "2024-02-11 14:00:00+00:00",
                "2024-02-11 16:00:00+00:00",
                "completed",
                "Snapshot 2024-02-11 14:00:00+00:00 to 2024-02-11 16:00:00+00:00 (completed)",
            ),
        ],
    )
    def test_str_representation(self, start_at, end_at, status, expected_str):
        snapshot = Snapshot(start_at=start_at, end_at=end_at, status=status)
        assert str(snapshot) == expected_str

    def test_default_status(self):
        snapshot = Snapshot(start_at=now(), end_at=now() + timedelta(hours=1))
        assert snapshot.status == Snapshot.Status.PENDING

    def test_timestamps(self):
        snapshot = Snapshot(start_at=now(), end_at=now() + timedelta(hours=1))
        assert snapshot.created_at is None  # Not saved yet
        assert snapshot.updated_at is None  # Not saved yet

    def test_ordering(self):
        assert Snapshot._meta.ordering == ["-start_at"]

    def test_indexes(self):
        """Check if indexes are correctly set in the database."""
        index_fields = {tuple(index.fields) for index in Snapshot._meta.indexes}
        assert ("status",) in index_fields  # Ensure 'status' index exists
        assert (
            "start_at",
            "end_at",
        ) in index_fields  # Ensure 'start_at' and 'end_at' index exists

    def test_many_to_many_relationships(self, db):
        snapshot = Snapshot.objects.create(start_at=now(), end_at=now() + timedelta(hours=1))

        chapter = Chapter.objects.create(name="Test Chapter")
        project = Project.objects.create(name="Test Project")
        issue = Issue.objects.create(title="Test Issue")
        release = Release.objects.create(version="v1.0.0")
        user = User.objects.create(username="testuser")

        snapshot.new_chapters.add(chapter)
        snapshot.new_projects.add(project)
        snapshot.new_issues.add(issue)
        snapshot.new_releases.add(release)
        snapshot.new_users.add(user)

        assert snapshot.new_chapters.count() == 1
        assert snapshot.new_projects.count() == 1
        assert snapshot.new_issues.count() == 1
        assert snapshot.new_releases.count() == 1
        assert snapshot.new_users.count() == 1
