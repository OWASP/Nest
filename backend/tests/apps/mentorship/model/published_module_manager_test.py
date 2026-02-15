"""Tests for mentorship PublishedModuleManager."""

from unittest.mock import MagicMock, patch

from apps.mentorship.models.managers.module import PublishedModuleManager
from apps.mentorship.models.program import Program


class TestPublishedModuleManager:
    """Tests for PublishedModuleManager."""

    @patch("django.db.models.Manager.get_queryset")
    def test_get_queryset_filters_published(self, mock_super_qs):
        """Test get_queryset filters by published program status."""
        mock_qs = MagicMock()
        mock_super_qs.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs

        manager = PublishedModuleManager()
        manager.model = MagicMock()

        result = manager.get_queryset()

        mock_qs.filter.assert_called_once_with(program__status=Program.ProgramStatus.PUBLISHED)
        assert result == mock_qs
