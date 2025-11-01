from datetime import datetime
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest

from apps.api.rest.v0.repository import RepositoryDetail, get_repository, list_repository
from apps.github.models.repository import Repository as RepositoryModel


class TestRepositorySchema:
    @pytest.mark.parametrize(
        "repository_data",
        [
            {
                "created_at": "2024-12-30T00:00:00Z",
                "description": "Description for Repo1",
                "name": "Repo1",
                "updated_at": "2024-12-30T00:00:00Z",
            },
            {
                "created_at": "2024-12-29T00:00:00Z",
                "description": "Description for Repo2",
                "name": "Repo2",
                "updated_at": "2024-12-30T00:00:00Z",
            },
        ],
    )
    def test_repository_schema(self, repository_data):
        repository = RepositoryDetail(**repository_data)

        assert repository.created_at == datetime.fromisoformat(repository_data["created_at"])
        assert repository.description == repository_data["description"]
        assert repository.name == repository_data["name"]
        assert repository.updated_at == datetime.fromisoformat(repository_data["updated_at"])


class TestListRepository:
    """Test cases for list_repository endpoint."""

    @patch("apps.api.rest.v0.repository.RepositoryModel.objects")
    def test_list_repository_with_custom_ordering(self, mock_objects):
        """Test listing repositories with custom ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_filters.organization_id = None

        mock_select = MagicMock()
        mock_ordered = MagicMock()

        mock_objects.select_related.return_value = mock_select
        mock_select.order_by.return_value = mock_ordered

        result = list_repository(mock_request, filters=mock_filters, ordering="created_at")

        mock_objects.select_related.assert_called_once_with("organization")
        mock_select.order_by.assert_called_once_with("created_at", "-updated_at")
        assert result == mock_ordered

    @patch("apps.api.rest.v0.repository.RepositoryModel.objects")
    def test_list_repository_with_default_ordering(self, mock_objects):
        """Test listing repositories with default ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_filters.organization_id = None

        mock_select = MagicMock()
        mock_ordered = MagicMock()

        mock_objects.select_related.return_value = mock_select
        mock_select.order_by.return_value = mock_ordered

        result = list_repository(mock_request, filters=mock_filters, ordering=None)

        mock_objects.select_related.assert_called_once_with("organization")
        mock_select.order_by.assert_called_once_with("-created_at", "-updated_at")
        assert result == mock_ordered

    @patch("apps.api.rest.v0.repository.RepositoryModel.objects")
    def test_list_repository_with_organization_filter(self, mock_objects):
        """Test listing repositories with organization filter."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_filters.organization_id = "OWASP"

        mock_select = MagicMock()
        mock_filter = MagicMock()
        mock_ordered = MagicMock()

        mock_objects.select_related.return_value = mock_select
        mock_select.filter.return_value = mock_filter
        mock_filter.order_by.return_value = mock_ordered

        result = list_repository(mock_request, filters=mock_filters, ordering=None)

        mock_objects.select_related.assert_called_once_with("organization")
        mock_select.filter.assert_called_once_with(organization__login__iexact="OWASP")
        mock_filter.order_by.assert_called_once_with("-created_at", "-updated_at")
        assert result == mock_ordered

    @patch("apps.api.rest.v0.repository.RepositoryModel.objects")
    def test_list_repository_without_organization_filter(self, mock_objects):
        """Test listing repositories without organization filter."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_filters.organization_id = None

        mock_select = MagicMock()
        mock_ordered = MagicMock()

        mock_objects.select_related.return_value = mock_select
        mock_select.order_by.return_value = mock_ordered

        result = list_repository(mock_request, filters=mock_filters, ordering=None)

        mock_objects.select_related.assert_called_once_with("organization")
        # Filter should not be called when organization_id is None
        mock_select.filter.assert_not_called()
        mock_select.order_by.assert_called_once_with("-created_at", "-updated_at")
        assert result == mock_ordered


class TestGetRepository:
    """Test cases for get_repository endpoint."""

    @patch("apps.api.rest.v0.repository.RepositoryModel.objects")
    def test_get_repository_found(self, mock_objects):
        """Test getting a repository that exists."""
        mock_request = MagicMock()
        mock_select = MagicMock()
        mock_repo = MagicMock()

        mock_objects.select_related.return_value = mock_select
        mock_select.get.return_value = mock_repo

        result = get_repository(mock_request, organization_id="OWASP", repository_id="Nest")

        mock_objects.select_related.assert_called_once_with("organization")
        mock_select.get.assert_called_once_with(
            organization__login__iexact="OWASP",
            name__iexact="Nest",
        )
        assert result == mock_repo

    @patch("apps.api.rest.v0.repository.RepositoryModel.objects")
    def test_get_repository_not_found(self, mock_objects):
        """Test getting a repository that does not exist returns 404."""
        mock_request = MagicMock()
        mock_select = MagicMock()

        mock_objects.select_related.return_value = mock_select
        mock_select.get.side_effect = RepositoryModel.DoesNotExist

        result = get_repository(mock_request, organization_id="OWASP", repository_id="NonExistent")

        mock_objects.select_related.assert_called_once_with("organization")
        mock_select.get.assert_called_once_with(
            organization__login__iexact="OWASP",
            name__iexact="NonExistent",
        )
        assert result.status_code == HTTPStatus.NOT_FOUND
        assert b"Repository not found" in result.content
