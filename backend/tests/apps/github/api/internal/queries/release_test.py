"""Test cases for ReleaseQuery."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from apps.github.api.internal.queries.release import ReleaseQuery
from apps.github.models.release import Release


class TestReleaseQuery:
    """Test cases for ReleaseQuery class."""

    @pytest.fixture
    def mock_release(self):
        """Mock Release instance."""
        release = Mock(spec=Release)
        release.id = 1
        release.author_id = 42
        return release

    @pytest.fixture
    def mock_queryset(self):
        """Mock queryset with all necessary methods."""
        queryset = MagicMock()
        queryset.filter.return_value = queryset
        queryset.order_by.return_value = queryset
        queryset.annotate.return_value = queryset
        queryset.__getitem__.return_value = []
        return queryset

    @patch("apps.github.models.release.Release.objects")
    def test_recent_releases_basic(self, mock_objects, mock_queryset, mock_release):
        """Test fetching recent releases with default parameters."""
        mock_objects.filter.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_release]

        result = ReleaseQuery().recent_releases()

        assert result == [mock_release]
        mock_objects.filter.assert_called_once_with(
            is_draft=False,
            is_pre_release=False,
            published_at__isnull=False,
        )
        mock_queryset.order_by.assert_called_with("-published_at")

    @patch("apps.github.models.release.Release.objects")
    def test_recent_releases_with_login(self, mock_objects, mock_queryset, mock_release):
        """Test filtering releases by login."""
        mock_objects.filter.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_release]

        result = ReleaseQuery().recent_releases(login="alice")

        assert result == [mock_release]
        mock_queryset.filter.assert_called_with(author__login="alice")

    @patch("apps.github.models.release.Release.objects")
    def test_recent_releases_with_organization(self, mock_objects, mock_queryset, mock_release):
        """Test filtering releases by organization."""
        mock_objects.filter.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_release]

        result = ReleaseQuery().recent_releases(organization="owasp")

        assert result == [mock_release]
        mock_queryset.filter.assert_called_with(repository__organization__login="owasp")

    @patch("apps.github.models.release.Release.objects")
    def test_recent_releases_distinct(self, mock_objects, mock_queryset, mock_release):
        """Test distinct filtering with Window/Rank for releases."""
        mock_objects.filter.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_release]

        result = ReleaseQuery().recent_releases(distinct=True)

        assert result == [mock_release]
        mock_queryset.annotate.assert_called_once()
        mock_queryset.filter.assert_called()
        assert mock_queryset.order_by.call_count == 2  # Once initially, once after filter

    @patch("apps.github.models.release.Release.objects")
    def test_recent_releases_with_limit(self, mock_objects, mock_queryset, mock_release):
        """Test limiting the number of releases returned."""
        mock_objects.filter.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_release]

        result = ReleaseQuery().recent_releases(limit=3)

        assert result == [mock_release]
        mock_queryset.__getitem__.assert_called_with(slice(None, 3))

    @patch("apps.github.models.release.Release.objects")
    def test_recent_releases_multiple_filters(self, mock_objects, mock_queryset, mock_release):
        """Test releases with multiple filters applied."""
        mock_objects.filter.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_release]

        result = ReleaseQuery().recent_releases(login="alice", organization="owasp", limit=2)

        assert result == [mock_release]
        # Verify both filters were applied
        filter_calls = mock_queryset.filter.call_args_list
        assert len(filter_calls) >= 2
        mock_queryset.__getitem__.assert_called_with(slice(None, 2))

    @patch("apps.github.models.release.Release.objects")
    def test_recent_releases_distinct_with_login(self, mock_objects, mock_queryset, mock_release):
        """Test distinct filtering with login filter."""
        mock_objects.filter.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_release]

        result = ReleaseQuery().recent_releases(distinct=True, login="alice")

        assert result == [mock_release]
        mock_queryset.annotate.assert_called_once()
        # One filter for login, one for rank=1
        # (initial filter is on Release.objects, not mock_queryset)
        assert mock_queryset.filter.call_count == 2

    @patch("apps.github.models.release.Release.objects")
    def test_recent_releases_distinct_with_organization(
        self, mock_objects, mock_queryset, mock_release
    ):
        """Test distinct filtering with organization filter."""
        mock_objects.filter.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_release]

        result = ReleaseQuery().recent_releases(distinct=True, organization="owasp")

        assert result == [mock_release]
        mock_queryset.annotate.assert_called_once()
        # One filter for organization, one for rank=1
        # (initial filter is on Release.objects not mock_queryset)
        assert mock_queryset.filter.call_count == 2

    @patch("apps.github.models.release.Release.objects")
    def test_recent_releases_distinct_with_all_filters(
        self, mock_objects, mock_queryset, mock_release
    ):
        """Test distinct filtering with all filters."""
        mock_objects.filter.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_release]

        result = ReleaseQuery().recent_releases(
            distinct=True, login="alice", organization="owasp", limit=5
        )

        assert result == [mock_release]
        mock_queryset.annotate.assert_called_once()
        # One filter for initial filters (is_draft, is_pre_release, published_at),
        # one for login, one for organization, one for rank=1
        # Note: There's also filter() calls for login and organization parameters
        mock_queryset.__getitem__.assert_called_with(slice(None, 5))

    @patch("apps.github.models.release.Release.objects")
    def test_recent_releases_login_only(self, mock_objects, mock_queryset, mock_release):
        """Test filtering releases by login only."""
        mock_objects.filter.return_value = mock_queryset
        mock_queryset.__getitem__.return_value = [mock_release]

        result = ReleaseQuery().recent_releases(login="alice")

        assert result == [mock_release]
        # Verify login filter was applied
        assert len(mock_queryset.filter.call_args_list) >= 1
