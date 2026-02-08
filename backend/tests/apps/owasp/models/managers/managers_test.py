from unittest.mock import MagicMock

from django.db.models import Q

from apps.owasp.models.managers.chapter import ActiveChapterManager
from apps.owasp.models.managers.committee import ActiveCommitteeManager
from apps.owasp.models.managers.project import ActiveProjectManager


class TestActiveChapterManager:
    """Test ActiveChapterManager."""

    def test_get_queryset(self, mocker):
        """Test get_queryset filters for active chapters with non-empty repos."""
        mock_qs = MagicMock()
        mocker.patch("django.db.models.Manager.get_queryset", return_value=mock_qs)
        manager = ActiveChapterManager()
        manager.model = MagicMock()
        result = manager.get_queryset()
        mock_qs.select_related.assert_called_with("owasp_repository")
        mock_qs.select_related.return_value.filter.assert_called_with(
            is_active=True,
            owasp_repository__is_empty=False,
        )
        assert result == mock_qs.select_related.return_value.filter.return_value

    def test_without_geo_data(self, mocker):
        """Test without_geo_data property."""
        manager = ActiveChapterManager()
        mock_qs = MagicMock()
        manager.get_queryset = MagicMock(return_value=mock_qs)

        result = manager.without_geo_data
        manager.get_queryset.assert_called_once()
        mock_qs.filter.assert_called_once()
        args, _ = mock_qs.filter.call_args
        assert len(args) == 1
        q_obj = args[0]
        assert isinstance(q_obj, Q)
        assert result == mock_qs.filter.return_value


class TestActiveCommitteeManager:
    """Test ActiveCommitteeManager."""

    def test_get_queryset(self, mocker):
        """Test get_queryset logic."""
        mock_qs = MagicMock()
        mocker.patch("django.db.models.Manager.get_queryset", return_value=mock_qs)

        manager = ActiveCommitteeManager()

        result = manager.get_queryset()

        mock_qs.filter.assert_called_with(is_active=True)
        assert result == mock_qs.filter.return_value

    def test_without_summary(self):
        """Test without_summary property."""
        manager = ActiveCommitteeManager()
        mock_qs = MagicMock()
        manager.get_queryset = MagicMock(return_value=mock_qs)

        result = manager.without_summary

        manager.get_queryset.assert_called_once()
        mock_qs.filter.assert_called_with(summary="")
        assert result == mock_qs.filter.return_value


class TestActiveProjectManager:
    """Test ActiveProjectManager."""

    def test_get_queryset(self, mocker):
        """Test get_queryset logic."""
        mock_qs = MagicMock()
        mocker.patch("django.db.models.Manager.get_queryset", return_value=mock_qs)

        manager = ActiveProjectManager()

        result = manager.get_queryset()

        mock_qs.filter.assert_called_with(is_active=True)
        assert result == mock_qs.filter.return_value

    def test_without_summary(self):
        """Test without_summary property."""
        manager = ActiveProjectManager()
        mock_qs = MagicMock()
        manager.get_queryset = MagicMock(return_value=mock_qs)

        result = manager.without_summary

        manager.get_queryset.assert_called_once()
        mock_qs.filter.assert_called_with(summary="")
        assert result == mock_qs.filter.return_value
