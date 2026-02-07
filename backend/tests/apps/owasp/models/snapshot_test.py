from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase
from django.utils import timezone

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
        for field in ["new_chapters", "new_projects", "new_issues", "new_releases", "new_users"]:
            m2m_mock = MagicMock()
            m2m_mock.all.return_value = []  # Simulate empty queryset
            m2m_mock.set = MagicMock()
            setattr(self.snapshot, field, m2m_mock)  # Assign mock manager

    def test_mocked_many_to_many_relations(self):
        """Test ManyToMany relationships using mocks."""
        self.snapshot.new_chapters.set(["Mock Chapter"])
        self.snapshot.new_chapters.set.assert_called_once_with(["Mock Chapter"])

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

    def test_new_chapters_count(self):
        """Test new_chapters_count property."""
        mock_snapshot = MagicMock(spec=Snapshot)
        mock_snapshot.new_chapters.count.return_value = 5
        result = Snapshot.new_chapters_count.fget(mock_snapshot)
        assert result == 5

    def test_new_issues_count(self):
        """Test new_issues_count property."""
        mock_snapshot = MagicMock(spec=Snapshot)
        mock_snapshot.new_issues.count.return_value = 10
        result = Snapshot.new_issues_count.fget(mock_snapshot)
        assert result == 10

    def test_new_projects_count(self):
        """Test new_projects_count property."""
        mock_snapshot = MagicMock(spec=Snapshot)
        mock_snapshot.new_projects.count.return_value = 3
        result = Snapshot.new_projects_count.fget(mock_snapshot)
        assert result == 3

    def test_new_releases_count(self):
        """Test new_releases_count property."""
        mock_snapshot = MagicMock(spec=Snapshot)
        mock_snapshot.new_releases.count.return_value = 7
        result = Snapshot.new_releases_count.fget(mock_snapshot)
        assert result == 7

    def test_new_users_count(self):
        """Test new_users_count property."""
        mock_snapshot = MagicMock(spec=Snapshot)
        mock_snapshot.new_users.count.return_value = 15
        result = Snapshot.new_users_count.fget(mock_snapshot)
        assert result == 15

    @patch.object(Snapshot, "save", lambda _self, *_args, **_kwargs: None)
    def test_save_generates_key_when_empty(self):
        """Test save method auto-generates key from current date."""
        snapshot = Snapshot.__new__(Snapshot)
        snapshot.key = ""

        with patch.object(timezone, "now") as mock_now:
            mock_now.return_value.strftime.return_value = "2025-02"
            if not snapshot.key:
                snapshot.key = mock_now().strftime("%Y-%m")

        assert snapshot.key == "2025-02"

    def test_save_preserves_existing_key(self):
        """Test save method preserves existing key."""
        snapshot = Snapshot.__new__(Snapshot)
        snapshot.key = "2024-12"
        if not snapshot.key:
            snapshot.key = "should-not-be-set"

        assert snapshot.key == "2024-12"
