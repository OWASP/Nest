from unittest.mock import MagicMock, patch

from django.db import models
from django.test import SimpleTestCase

from apps.owasp.models.snapshot import Snapshot


class SnapshotModelMockTest(SimpleTestCase):
    """Test Snapshot model using mocks to avoid database interactions."""

    def setUp(self):
        """Set up a mocked snapshot object."""
        self.snapshot = MagicMock(spec=Snapshot)  # Mock entire model
        self.snapshot.id = 1  # Set an ID to avoid ManyToMany errors
        self.snapshot.title = "Mock Snapshot Title"
        self.snapshot.key = "2025-02"
        self.snapshot.start_at = "2025-02-21"
        self.snapshot.end_at = "2025-02-21"
        self.snapshot.status = Snapshot.Status.PROCESSING

        # Mock ManyToMany relations
        for field in (
            "chapters",
            "events",
            "issues",
            "posts",
            "projects",
            "pull_requests",
            "releases",
            "users",
        ):
            m2m_mock = MagicMock()
            m2m_mock.all.return_value = []  # Simulate empty queryset
            m2m_mock.set = MagicMock()
            setattr(self.snapshot, field, m2m_mock)  # Assign mock manager

    def test_mocked_many_to_many_relations(self):
        """Test ManyToMany relationships using mocks."""
        self.snapshot.chapters.set(["Mock Chapter"])
        self.snapshot.chapters.set.assert_called_once_with(["Mock Chapter"])

    def test_snapshot_attributes(self):
        """Test that title and key are correctly assigned."""
        assert self.snapshot.title == "Mock Snapshot Title"
        assert self.snapshot.key == "2025-02"


class SnapshotModelPropertyTest(SimpleTestCase):
    """Test Snapshot model properties."""

    def test_str_representation(self):
        """Test __str__ returns the snapshot title."""
        snapshot = Snapshot.__new__(Snapshot)
        snapshot.title = "January 2025 Snapshot"
        assert str(snapshot) == "January 2025 Snapshot"

    def test_chapters_count(self):
        """Test chapters_count property."""
        mock_snapshot = MagicMock(spec=Snapshot)
        mock_snapshot.chapters.count.return_value = 5
        result = Snapshot.chapters_count.fget(mock_snapshot)
        assert result == 5

    def test_events_count(self):
        """Test events_count property."""
        mock_snapshot = MagicMock(spec=Snapshot)
        mock_snapshot.events.count.return_value = 4
        result = Snapshot.events_count.fget(mock_snapshot)
        assert result == 4

    def test_issues_count(self):
        """Test issues_count property."""
        mock_snapshot = MagicMock(spec=Snapshot)
        mock_snapshot.issues.count.return_value = 10
        result = Snapshot.issues_count.fget(mock_snapshot)
        assert result == 10

    def test_posts_count(self):
        """Test posts_count property."""
        mock_snapshot = MagicMock(spec=Snapshot)
        mock_snapshot.posts.count.return_value = 6
        result = Snapshot.posts_count.fget(mock_snapshot)
        assert result == 6

    def test_projects_count(self):
        """Test projects_count property."""
        mock_snapshot = MagicMock(spec=Snapshot)
        mock_snapshot.projects.count.return_value = 3
        result = Snapshot.projects_count.fget(mock_snapshot)
        assert result == 3

    def test_pull_requests_count(self):
        """Test pull_requests_count property."""
        mock_snapshot = MagicMock(spec=Snapshot)
        mock_snapshot.pull_requests.count.return_value = 8
        result = Snapshot.pull_requests_count.fget(mock_snapshot)
        assert result == 8

    def test_releases_count(self):
        """Test releases_count property."""
        mock_snapshot = MagicMock(spec=Snapshot)
        mock_snapshot.releases.count.return_value = 7
        result = Snapshot.releases_count.fget(mock_snapshot)
        assert result == 7

    def test_users_count(self):
        """Test users_count property."""
        mock_snapshot = MagicMock(spec=Snapshot)
        mock_snapshot.users.count.return_value = 15
        result = Snapshot.users_count.fget(mock_snapshot)
        assert result == 15

    def test_save_generates_weekly_key_when_empty(self):
        """Test save method auto-generates weekly key from start_at date."""
        snapshot = Snapshot.__new__(Snapshot)
        snapshot.key = ""
        snapshot.frequency = Snapshot.Frequency.WEEKLY
        snapshot.start_at = MagicMock()
        snapshot.start_at.isocalendar.return_value = (2025, 8, 1)

        with patch.object(models.Model, "save"):
            snapshot.save()

        assert snapshot.key == "2025-W08"

    def test_save_generates_monthly_key_when_empty(self):
        """Test save method auto-generates monthly key from start_at date."""
        snapshot = Snapshot.__new__(Snapshot)
        snapshot.key = ""
        snapshot.frequency = Snapshot.Frequency.MONTHLY
        snapshot.start_at = MagicMock()
        snapshot.start_at.strftime.return_value = "2025-02"

        with patch.object(models.Model, "save"):
            snapshot.save()

        assert snapshot.key == "2025-02"

    def test_save_preserves_existing_key(self):
        """Test save method preserves existing key."""
        snapshot = Snapshot.__new__(Snapshot)
        snapshot.key = "2024-12"

        with patch.object(models.Model, "save"):
            snapshot.save()

        assert snapshot.key == "2024-12"
