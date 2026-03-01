from datetime import datetime
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest

from apps.api.rest.v0.repository import RepositoryDetail, get_repository, list_repository


class TestRepositorySchema:
    @pytest.mark.parametrize(
        "repository_data",
        [
            {
                "commits_count": 0,
                "contributors_count": 0,
                "created_at": "2024-12-30T00:00:00Z",
                "description": "Description for Repo1",
                "forks_count": 0,
                "name": "Repo1",
                "open_issues_count": 0,
                "stars_count": 0,
                "updated_at": "2024-12-30T00:00:00Z",
            },
            {
                "commits_count": 20,
                "contributors_count": 5,
                "created_at": "2024-12-29T00:00:00Z",
                "description": "Description for Repo2",
                "forks_count": 3,
                "name": "Repo2",
                "open_issues_count": 2,
                "stars_count": 10,
                "updated_at": "2024-12-30T00:00:00Z",
            },
        ],
    )
    def test_repository_schema(self, repository_data):
        repository = RepositoryDetail(**repository_data)

        assert repository.commits_count == repository_data["commits_count"]
        assert repository.contributors_count == repository_data["contributors_count"]
        assert repository.created_at == datetime.fromisoformat(repository_data["created_at"])
        assert repository.description == repository_data["description"]
        assert repository.forks_count == repository_data["forks_count"]
        assert repository.name == repository_data["name"]
        assert repository.open_issues_count == repository_data["open_issues_count"]
        assert repository.stars_count == repository_data["stars_count"]
        assert repository.updated_at == datetime.fromisoformat(repository_data["updated_at"])


class TestListRepository:
    """Tests for list_repository endpoint."""

    @patch("apps.api.rest.v0.repository.RepositoryModel")
    def test_list_repository_without_filter(self, mock_repo_model):
        """Test list repositories without organization filter."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_filters.organization_id = None

        mock_queryset = MagicMock()
        mock_repo_model.objects.select_related.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset

        result = list_repository(mock_request, mock_filters, ordering=None)

        mock_queryset.order_by.assert_called_with("-created_at", "-updated_at")
        assert result == mock_queryset

    @patch("apps.api.rest.v0.repository.RepositoryModel")
    def test_list_repository_with_organization_filter(self, mock_repo_model):
        """Test list repositories with organization filter."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_filters.organization_id = "OWASP"

        mock_queryset = MagicMock()
        mock_filtered_queryset = MagicMock()
        mock_repo_model.objects.select_related.return_value = mock_queryset
        mock_queryset.filter.return_value = mock_filtered_queryset
        mock_filtered_queryset.order_by.return_value = mock_filtered_queryset

        result = list_repository(mock_request, mock_filters, ordering="created_at")

        mock_queryset.filter.assert_called_with(organization__login__iexact="OWASP")
        mock_filtered_queryset.order_by.assert_called_with("created_at", "-updated_at")
        assert result == mock_filtered_queryset


class TestGetRepository:
    """Tests for get_repository endpoint."""

    @patch("apps.api.rest.v0.repository.RepositoryModel")
    def test_get_repository_success(self, mock_repo_model):
        """Test get repository when found."""
        mock_request = MagicMock()
        mock_repo = MagicMock()
        mock_repo_model.objects.select_related.return_value.get.return_value = mock_repo

        result = get_repository(mock_request, "OWASP", "Nest")

        mock_repo_model.objects.select_related.assert_called_with("organization")
        assert result == mock_repo

    @patch("apps.api.rest.v0.repository.RepositoryModel")
    def test_get_repository_not_found(self, mock_repo_model):
        """Test get repository when not found."""
        mock_request = MagicMock()
        mock_repo_model.DoesNotExist = Exception
        mock_repo_model.objects.select_related.return_value.get.side_effect = (
            mock_repo_model.DoesNotExist
        )

        result = get_repository(mock_request, "OWASP", "NonExistent")

        assert result.status_code == HTTPStatus.NOT_FOUND
