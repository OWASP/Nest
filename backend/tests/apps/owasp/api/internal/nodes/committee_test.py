"""Tests for Committee GraphQL node."""

from unittest.mock import Mock

from apps.owasp.api.internal.nodes.committee import CommitteeNode


class TestCommitteeNode:
    def test_contributors_count_resolver(self):
        """Test contributors_count returns count from repository."""
        mock_repo = Mock()
        mock_repo.contributors_count = 42

        mock_committee = Mock()
        mock_committee.owasp_repository = mock_repo

        result = CommitteeNode.contributors_count(mock_committee)

        assert result == 42

    def test_created_at_resolver(self):
        """Test created_at returns indexed timestamp."""
        mock_committee = Mock()
        mock_committee.idx_created_at = 1234567890.0

        result = CommitteeNode.created_at(mock_committee)

        assert result == 1234567890.0

    def test_forks_count_resolver(self):
        """Test forks_count returns count from repository."""
        mock_repo = Mock()
        mock_repo.forks_count = 15

        mock_committee = Mock()
        mock_committee.owasp_repository = mock_repo

        result = CommitteeNode.forks_count(mock_committee)

        assert result == 15

    def test_issues_count_resolver(self):
        """Test issues_count returns open issues from repository."""
        mock_repo = Mock()
        mock_repo.open_issues_count = 23

        mock_committee = Mock()
        mock_committee.owasp_repository = mock_repo

        result = CommitteeNode.issues_count(mock_committee)

        assert result == 23

    def test_repositories_count_resolver(self):
        """Test repositories_count always returns 1 for committees."""
        mock_committee = Mock()

        result = CommitteeNode.repositories_count(mock_committee)

        assert result == 1

    def test_stars_count_resolver(self):
        """Test stars_count returns count from repository."""
        mock_repo = Mock()
        mock_repo.stars_count = 100

        mock_committee = Mock()
        mock_committee.owasp_repository = mock_repo

        result = CommitteeNode.stars_count(mock_committee)

        assert result == 100
