"""Test cases for RepositoryContributorQuery."""

from unittest.mock import patch

import pytest

from apps.github.api.internal.queries.repository_contributor import RepositoryContributorQuery


class TestRepositoryContributorQuery:
    """Test cases for RepositoryContributorQuery class."""

    @pytest.fixture
    def mock_contributor_data(self):
        """Mock contributor data."""
        return [
            {
                "avatar_url": "https://example.com/avatar1.jpg",
                "contributions_count": 50,
                "login": "alice",
                "name": "Alice Smith",
                "project_key": "www-project-test",
                "project_name": "Test Project",
            },
            {
                "avatar_url": "https://example.com/avatar2.jpg",
                "contributions_count": 30,
                "login": "bob",
                "name": "Bob Jones",
                "project_key": None,
                "project_name": None,
            },
        ]

    @patch("apps.github.models.repository_contributor.RepositoryContributor.get_top_contributors")
    def test_top_contributors_basic(self, mock_get_top_contributors, mock_contributor_data):
        """Test fetching top contributors with default parameters."""
        mock_get_top_contributors.return_value = mock_contributor_data

        result = RepositoryContributorQuery().top_contributors()

        assert len(result) == 2
        assert result[0].login == "alice"
        assert result[0].contributions_count == 50
        assert result[0].project_key == "www-project-test"
        assert result[1].login == "bob"
        assert result[1].project_key is None

        mock_get_top_contributors.assert_called_once_with(
            limit=20,
            chapter=None,
            committee=None,
            excluded_usernames=None,
            organization=None,
            project=None,
            repository=None,
        )

    @patch("apps.github.models.repository_contributor.RepositoryContributor.get_top_contributors")
    def test_top_contributors_with_limit(self, mock_get_top_contributors, mock_contributor_data):
        """Test fetching top contributors with custom limit."""
        mock_get_top_contributors.return_value = mock_contributor_data[:1]

        result = RepositoryContributorQuery().top_contributors(limit=1)

        assert len(result) == 1
        assert result[0].login == "alice"

        mock_get_top_contributors.assert_called_once_with(
            limit=1,
            chapter=None,
            committee=None,
            excluded_usernames=None,
            organization=None,
            project=None,
            repository=None,
        )

    @patch("apps.github.models.repository_contributor.RepositoryContributor.get_top_contributors")
    def test_top_contributors_with_filters(self, mock_get_top_contributors, mock_contributor_data):
        """Test fetching top contributors with various filters."""
        mock_get_top_contributors.return_value = mock_contributor_data

        result = RepositoryContributorQuery().top_contributors(
            limit=10,
            chapter="test-chapter",
            committee="test-committee",
            excluded_usernames=["excluded_user"],
            organization="owasp",
            project="test-project",
            repository="test-repo",
        )

        assert len(result) == 2

        mock_get_top_contributors.assert_called_once_with(
            limit=10,
            chapter="test-chapter",
            committee="test-committee",
            excluded_usernames=["excluded_user"],
            organization="owasp",
            project="test-project",
            repository="test-repo",
        )

    @patch("apps.github.models.repository_contributor.RepositoryContributor.get_top_contributors")
    def test_top_contributors_empty_result(self, mock_get_top_contributors):
        """Test fetching top contributors when no contributors are found."""
        mock_get_top_contributors.return_value = []

        result = RepositoryContributorQuery().top_contributors()

        assert len(result) == 0
        mock_get_top_contributors.assert_called_once()

    @patch("apps.github.models.repository_contributor.RepositoryContributor.get_top_contributors")
    def test_top_contributors_node_creation(self, mock_get_top_contributors):
        """Test that RepositoryContributorNode objects are created correctly."""
        mock_data = [
            {
                "avatar_url": "https://example.com/avatar.jpg",
                "contributions_count": 25,
                "login": "testuser",
                "name": "Test User",
                "project_key": "www-project-example",
                "project_name": "Example Project",
            }
        ]
        mock_get_top_contributors.return_value = mock_data

        result = RepositoryContributorQuery().top_contributors()

        assert len(result) == 1
        node = result[0]
        assert node.avatar_url == "https://example.com/avatar.jpg"
        assert node.contributions_count == 25
        assert node.login == "testuser"
        assert node.name == "Test User"
        assert node.project_key == "www-project-example"
        assert node.project_name == "Example Project"
