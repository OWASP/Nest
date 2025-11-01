from datetime import datetime
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest

from apps.api.rest.v0.release import ReleaseDetail, get_release, list_release
from apps.github.models.release import Release as ReleaseModel


class TestReleaseSchema:
    @pytest.mark.parametrize(
        "release_data",
        [
            {
                "created_at": "2024-12-30T00:00:00Z",
                "description": "First stable release",
                "name": "v1.0",
                "published_at": "2024-12-30T00:00:00Z",
                "tag_name": "v1.0.0",
            },
            {
                "created_at": "2024-12-29T00:00:00Z",
                "description": "Minor improvements and bug fixes",
                "name": "v1.1",
                "published_at": "2024-12-30T00:00:00Z",
                "tag_name": "v1.1.0",
            },
        ],
    )
    def test_release_schema(self, release_data):
        release = ReleaseDetail(**release_data)

        assert release.created_at == datetime.fromisoformat(release_data["created_at"])
        assert release.description == release_data["description"]
        assert release.name == release_data["name"]
        assert release.published_at == datetime.fromisoformat(release_data["published_at"])
        assert release.tag_name == release_data["tag_name"]


class TestListRelease:
    """Test cases for list_release endpoint."""

    @patch("apps.api.rest.v0.release.ReleaseModel.objects")
    def test_list_release_with_custom_ordering(self, mock_objects):
        """Test listing releases with custom ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_filters.organization = None
        mock_filters.repository = None
        mock_filters.tag_name = None

        mock_exclude = MagicMock()
        mock_select = MagicMock()
        mock_ordered = MagicMock()

        mock_objects.exclude.return_value = mock_exclude
        mock_exclude.select_related.return_value = mock_select
        mock_select.order_by.return_value = mock_ordered

        result = list_release(mock_request, filters=mock_filters, ordering="created_at")

        mock_objects.exclude.assert_called_once_with(published_at__isnull=True)
        mock_exclude.select_related.assert_called_once_with(
            "repository", "repository__organization"
        )
        mock_select.order_by.assert_called_once_with("created_at", "-created_at")
        assert result == mock_ordered

    @patch("apps.api.rest.v0.release.ReleaseModel.objects")
    def test_list_release_with_default_ordering(self, mock_objects):
        """Test listing releases with default ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_filters.organization = None
        mock_filters.repository = None
        mock_filters.tag_name = None

        mock_exclude = MagicMock()
        mock_select = MagicMock()
        mock_ordered = MagicMock()

        mock_objects.exclude.return_value = mock_exclude
        mock_exclude.select_related.return_value = mock_select
        mock_select.order_by.return_value = mock_ordered

        result = list_release(mock_request, filters=mock_filters, ordering=None)

        mock_objects.exclude.assert_called_once_with(published_at__isnull=True)
        mock_exclude.select_related.assert_called_once_with(
            "repository", "repository__organization"
        )
        mock_select.order_by.assert_called_once_with("-published_at", "-created_at")
        assert result == mock_ordered

    @patch("apps.api.rest.v0.release.ReleaseModel.objects")
    def test_list_release_with_organization_filter(self, mock_objects):
        """Test listing releases with organization filter."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_filters.organization = "OWASP"
        mock_filters.repository = None
        mock_filters.tag_name = None

        mock_exclude = MagicMock()
        mock_select = MagicMock()
        mock_filter_org = MagicMock()
        mock_ordered = MagicMock()

        mock_objects.exclude.return_value = mock_exclude
        mock_exclude.select_related.return_value = mock_select
        mock_select.filter.return_value = mock_filter_org
        mock_filter_org.order_by.return_value = mock_ordered

        result = list_release(mock_request, filters=mock_filters, ordering=None)

        mock_objects.exclude.assert_called_once_with(published_at__isnull=True)
        mock_exclude.select_related.assert_called_once_with(
            "repository", "repository__organization"
        )
        mock_select.filter.assert_called_once_with(repository__organization__login__iexact="OWASP")
        mock_filter_org.order_by.assert_called_once_with("-published_at", "-created_at")
        assert result == mock_ordered

    @patch("apps.api.rest.v0.release.ReleaseModel.objects")
    def test_list_release_with_repository_filter(self, mock_objects):
        """Test listing releases with repository filter."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_filters.organization = None
        mock_filters.repository = "Nest"
        mock_filters.tag_name = None

        mock_exclude = MagicMock()
        mock_select = MagicMock()
        mock_filter_repo = MagicMock()
        mock_ordered = MagicMock()

        mock_objects.exclude.return_value = mock_exclude
        mock_exclude.select_related.return_value = mock_select
        mock_select.filter.return_value = mock_filter_repo
        mock_filter_repo.order_by.return_value = mock_ordered

        result = list_release(mock_request, filters=mock_filters, ordering=None)

        mock_objects.exclude.assert_called_once_with(published_at__isnull=True)
        mock_exclude.select_related.assert_called_once_with(
            "repository", "repository__organization"
        )
        mock_select.filter.assert_called_once_with(repository__name__iexact="Nest")
        mock_filter_repo.order_by.assert_called_once_with("-published_at", "-created_at")
        assert result == mock_ordered

    @patch("apps.api.rest.v0.release.ReleaseModel.objects")
    def test_list_release_with_tag_name_filter(self, mock_objects):
        """Test listing releases with tag_name filter."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_filters.organization = None
        mock_filters.repository = None
        mock_filters.tag_name = "v1.0.0"

        mock_exclude = MagicMock()
        mock_select = MagicMock()
        mock_filter_tag = MagicMock()
        mock_ordered = MagicMock()

        mock_objects.exclude.return_value = mock_exclude
        mock_exclude.select_related.return_value = mock_select
        mock_select.filter.return_value = mock_filter_tag
        mock_filter_tag.order_by.return_value = mock_ordered

        result = list_release(mock_request, filters=mock_filters, ordering=None)

        mock_objects.exclude.assert_called_once_with(published_at__isnull=True)
        mock_exclude.select_related.assert_called_once_with(
            "repository", "repository__organization"
        )
        mock_select.filter.assert_called_once_with(tag_name="v1.0.0")
        mock_filter_tag.order_by.assert_called_once_with("-published_at", "-created_at")
        assert result == mock_ordered


class TestGetRelease:
    """Test cases for get_release endpoint."""

    @patch("apps.api.rest.v0.release.ReleaseModel.objects")
    def test_get_release_found(self, mock_objects):
        """Test getting a release that exists."""
        mock_request = MagicMock()
        mock_release = MagicMock()

        mock_objects.get.return_value = mock_release

        result = get_release(
            mock_request,
            organization_id="OWASP",
            repository_id="Nest",
            release_id="v1.0.0",
        )

        mock_objects.get.assert_called_once_with(
            repository__organization__login__iexact="OWASP",
            repository__name__iexact="Nest",
            tag_name="v1.0.0",
        )
        assert result == mock_release

    @patch("apps.api.rest.v0.release.ReleaseModel.objects")
    def test_get_release_not_found(self, mock_objects):
        """Test getting a release that does not exist returns 404."""
        mock_request = MagicMock()

        mock_objects.get.side_effect = ReleaseModel.DoesNotExist

        result = get_release(
            mock_request,
            organization_id="OWASP",
            repository_id="NonExistent",
            release_id="v99.99.99",
        )

        mock_objects.get.assert_called_once_with(
            repository__organization__login__iexact="OWASP",
            repository__name__iexact="NonExistent",
            tag_name="v99.99.99",
        )
        assert result.status_code == HTTPStatus.NOT_FOUND
        assert b"Release not found" in result.content
