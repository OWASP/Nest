"""Tests for CommitteeIndexMixin."""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from apps.owasp.models.mixins.committee import CommitteeIndexMixin


class TestCommitteeIndexMixin:
    """Test cases for CommitteeIndexMixin."""

    def create_mock_committee(self, **kwargs):
        """Create a mock committee with CommitteeIndexMixin methods."""
        mock_committee = MagicMock(spec=CommitteeIndexMixin)
        mock_committee.key = kwargs.get("key", "www-committee-test")
        mock_committee.name = kwargs.get("name", "Test Committee")
        mock_committee.related_urls = kwargs.get("related_urls", ["https://example.com"])
        mock_committee.created_at = kwargs.get(
            "created_at", datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)
        )
        mock_committee.updated_at = kwargs.get(
            "updated_at", datetime(2024, 6, 15, 12, 0, 0, tzinfo=UTC)
        )

        return mock_committee

    def test_idx_created_at_with_value(self):
        """Test idx_created_at returns timestamp when created_at exists."""
        test_datetime = datetime(2024, 3, 15, 10, 30, 0, tzinfo=UTC)
        mock_committee = self.create_mock_committee(created_at=test_datetime)

        result = CommitteeIndexMixin.idx_created_at.fget(mock_committee)

        assert result == test_datetime.timestamp()

    def test_idx_created_at_none(self):
        """Test idx_created_at returns None when created_at is None."""
        mock_committee = self.create_mock_committee(created_at=None)

        result = CommitteeIndexMixin.idx_created_at.fget(mock_committee)

        assert result is None

    def test_idx_key(self):
        """Test idx_key strips www-committee- prefix."""
        mock_committee = self.create_mock_committee(key="www-committee-education")

        result = CommitteeIndexMixin.idx_key.fget(mock_committee)

        assert result == "education"

    def test_idx_related_urls(self):
        """Test idx_related_urls returns related URLs list."""
        urls = ["https://owasp.org", "https://wiki.owasp.org"]
        mock_committee = self.create_mock_committee(related_urls=urls)

        result = CommitteeIndexMixin.idx_related_urls.fget(mock_committee)

        assert result == urls

    def test_idx_top_contributors(self):
        """Test idx_top_contributors calls RepositoryContributor."""
        mock_committee = self.create_mock_committee(key="www-committee-test")

        with patch(
            "apps.owasp.models.mixins.committee.RepositoryContributor.get_top_contributors"
        ) as mock_get:
            mock_get.return_value = [{"login": "user1"}, {"login": "user2"}]

            result = CommitteeIndexMixin.idx_top_contributors.fget(mock_committee)

            mock_get.assert_called_once_with(committee="www-committee-test")
            assert len(result) == 2

    def test_idx_updated_at_with_value(self):
        """Test idx_updated_at returns timestamp when updated_at exists."""
        test_datetime = datetime(2024, 8, 20, 14, 0, 0, tzinfo=UTC)
        mock_committee = self.create_mock_committee(updated_at=test_datetime)

        result = CommitteeIndexMixin.idx_updated_at.fget(mock_committee)

        assert result == test_datetime.timestamp()

    def test_idx_updated_at_none(self):
        """Test idx_updated_at returns None when updated_at is None."""
        mock_committee = self.create_mock_committee(updated_at=None)

        result = CommitteeIndexMixin.idx_updated_at.fget(mock_committee)

        assert result is None
