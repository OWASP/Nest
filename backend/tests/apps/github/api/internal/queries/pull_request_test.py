"""Test cases for PullRequestQuery."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from apps.github.api.internal.queries.pull_request import PullRequestQuery
from apps.github.models.pull_request import PullRequest


class TestPullRequestQuery:
    """Test cases for PullRequestQuery class."""

    @pytest.fixture
    def mock_pull_request(self):
        """Mock PullRequest instance."""
        pr = Mock(spec=PullRequest)
        pr.id = 1
        pr.author_id = 42
        return pr

    @pytest.fixture
    def mock_queryset(self):
        """Mock queryset with all necessary methods."""
        queryset = MagicMock()
        queryset.select_related.return_value = queryset
        queryset.exclude.return_value = queryset
        queryset.order_by.return_value = queryset
        queryset.filter.return_value = queryset
        queryset.__getitem__.return_value = []
        return queryset

    @patch("apps.github.models.pull_request.PullRequest.objects")
    def test_recent_pull_requests_basic(self, mock_objects, mock_queryset, mock_pull_request):
        """Test fetching recent pull requests with default parameters."""
        mock_objects.select_related.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_pull_request]

        result = PullRequestQuery().recent_pull_requests()

        assert result == [mock_pull_request]
        mock_objects.select_related.assert_called_once_with(
            "author", "repository", "repository__organization"
        )
        mock_queryset.exclude.assert_called_once_with(author__is_bot=True)
        mock_queryset.order_by.assert_called_once_with("-created_at")

    @patch("apps.github.models.pull_request.PullRequest.objects")
    def test_recent_pull_requests_with_login(self, mock_objects, mock_queryset, mock_pull_request):
        """Test filtering pull requests by login."""
        mock_objects.select_related.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_pull_request]

        result = PullRequestQuery().recent_pull_requests(login="alice")

        assert result == [mock_pull_request]
        mock_queryset.filter.assert_called_with(author__login="alice")

    @patch("apps.github.models.pull_request.PullRequest.objects")
    def test_recent_pull_requests_with_organization(
        self, mock_objects, mock_queryset, mock_pull_request
    ):
        """Test filtering pull requests by organization."""
        mock_objects.select_related.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_pull_request]

        result = PullRequestQuery().recent_pull_requests(organization="owasp")

        assert result == [mock_pull_request]
        mock_queryset.filter.assert_called_with(repository__organization__login="owasp")

    @patch("apps.owasp.models.project.Project.objects")
    @patch("apps.github.models.pull_request.PullRequest.objects")
    def test_recent_pull_requests_with_project(
        self, mock_pr_objects, mock_project_objects, mock_queryset, mock_pull_request
    ):
        """Test filtering pull requests by project."""
        mock_project = Mock()
        mock_project.repositories.values_list.return_value = [1, 2, 3]
        mock_project_objects.filter.return_value.first.return_value = mock_project

        mock_pr_objects.select_related.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_pull_request]

        result = PullRequestQuery().recent_pull_requests(project="test-project")

        assert result == [mock_pull_request]
        mock_project_objects.filter.assert_called_once_with(key__iexact="www-project-test-project")
        mock_queryset.filter.assert_called_with(repository_id__in=[1, 2, 3])

    @patch("apps.github.models.pull_request.PullRequest.objects")
    def test_recent_pull_requests_with_repository(
        self, mock_objects, mock_queryset, mock_pull_request
    ):
        """Test filtering pull requests by repository."""
        mock_objects.select_related.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_pull_request]

        result = PullRequestQuery().recent_pull_requests(repository="test-repo")

        assert result == [mock_pull_request]
        mock_queryset.filter.assert_called_with(repository__key__iexact="test-repo")

    @patch("apps.github.api.internal.queries.pull_request.Subquery")
    @patch("apps.github.models.pull_request.PullRequest.objects")
    def test_recent_pull_requests_distinct(
        self, mock_objects, mock_subquery, mock_queryset, mock_pull_request
    ):
        """Test distinct filtering with Subquery for pull requests."""
        mock_objects.select_related.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_pull_request]

        mock_subquery_instance = Mock()
        mock_subquery.return_value = mock_subquery_instance

        result = PullRequestQuery().recent_pull_requests(distinct=True)

        assert result == [mock_pull_request]
        mock_queryset.filter.assert_called()
        mock_subquery.assert_called_once()

    @patch("apps.github.models.pull_request.PullRequest.objects")
    def test_recent_pull_requests_with_limit(self, mock_objects, mock_queryset, mock_pull_request):
        """Test limiting the number of pull requests returned."""
        mock_objects.select_related.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_pull_request]

        result = PullRequestQuery().recent_pull_requests(limit=3)

        assert result == [mock_pull_request]
        mock_queryset.__getitem__.assert_called_with(slice(None, 3))

    @patch("apps.github.models.pull_request.PullRequest.objects")
    def test_recent_pull_requests_multiple_filters(
        self, mock_objects, mock_queryset, mock_pull_request
    ):
        """Test pull requests with multiple filters applied."""
        mock_objects.select_related.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_pull_request]

        result = PullRequestQuery().recent_pull_requests(
            login="alice", organization="owasp", repository="test-repo", limit=2
        )

        assert result == [mock_pull_request]
        assert mock_queryset.filter.call_count >= 3
        mock_queryset.__getitem__.assert_called_with(slice(None, 2))

    @patch("apps.github.api.internal.queries.pull_request.OuterRef")
    @patch("apps.github.api.internal.queries.pull_request.Subquery")
    @patch("apps.github.models.pull_request.PullRequest.objects")
    def test_recent_pull_requests_distinct_with_filters(
        self, mock_objects, mock_subquery, mock_outer_ref, mock_queryset, mock_pull_request
    ):
        """Test distinct filtering with additional filters."""
        mock_objects.select_related.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_pull_request]

        mock_subquery_instance = Mock()
        mock_subquery.return_value = mock_subquery_instance
        mock_outer_ref_instance = Mock()
        mock_outer_ref.return_value = mock_outer_ref_instance

        result = PullRequestQuery().recent_pull_requests(
            distinct=True, login="alice", organization="owasp"
        )

        assert result == [mock_pull_request]
        mock_queryset.filter.assert_called()
        mock_subquery.assert_called_once()
        mock_outer_ref.assert_called_once_with("author_id")

    @patch("apps.github.models.pull_request.PullRequest.objects")
    def test_recent_pull_requests_with_multiple_filters_no_project(
        self, mock_objects, mock_queryset, mock_pull_request
    ):
        """Test pull requests with multiple filters (no project to avoid DB issues)."""
        mock_objects.select_related.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_pull_request]

        result = PullRequestQuery().recent_pull_requests(
            login="testuser", organization="owasp", repository="test-repo", limit=5
        )

        assert result == [mock_pull_request]
        # Verify filters were applied
        assert mock_queryset.filter.call_count >= 3  # login, organization, repository

    @patch("apps.github.api.internal.queries.pull_request.OuterRef")
    @patch("apps.github.api.internal.queries.pull_request.Subquery")
    @patch("apps.github.models.pull_request.PullRequest.objects")
    def test_recent_pull_requests_distinct_comprehensive(
        self, mock_objects, mock_subquery, mock_outer_ref, mock_queryset, mock_pull_request
    ):
        """Test distinct filtering with multiple filters."""
        mock_objects.select_related.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_pull_request]

        mock_subquery_instance = Mock()
        mock_subquery.return_value = mock_subquery_instance
        mock_outer_ref_instance = Mock()
        mock_outer_ref.return_value = mock_outer_ref_instance

        result = PullRequestQuery().recent_pull_requests(
            distinct=True, login="alice", organization="owasp", repository="test-repo"
        )

        assert result == [mock_pull_request]
        mock_subquery.assert_called_once()
        mock_outer_ref.assert_called_once_with("author_id")
        # Verify multiple filters were applied
        assert mock_queryset.filter.call_count >= 4  # login, org, repo, distinct
