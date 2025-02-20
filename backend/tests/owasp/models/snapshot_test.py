from unittest.mock import MagicMock

from django.test import SimpleTestCase

from apps.owasp.models.snapshot import Snapshot


class SnapshotModelMockTest(SimpleTestCase):
    """Test Snapshot model using mocks to avoid database interactions."""

    def setUp(self):
        """Set up a mocked snapshot object."""
        self.snapshot = MagicMock(spec=Snapshot)  # Mock entire model
        self.snapshot.id = 1  # Set an ID to avoid ManyToMany errors
        self.snapshot.start_at = "2025-02-21 12:00:00"
        self.snapshot.end_at = "2025-02-21 14:00:00"
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
