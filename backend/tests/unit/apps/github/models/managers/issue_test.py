"""Tests for Issue managers."""

from unittest import mock

from apps.github.models.managers.issue import OpenIssueManager


class TestOpenIssueManager:
    def test_get_queryset_applies_filters(self):
        manager = OpenIssueManager()
        manager.model = mock.Mock()

        mock_queryset = mock.Mock()

        with mock.patch("django.db.models.Manager.get_queryset", return_value=mock_queryset):
            mock_queryset.select_related.return_value = mock_queryset
            mock_queryset.prefetch_related.return_value = mock_queryset
            mock_queryset.filter.return_value = mock_queryset

            result = manager.get_queryset()

            mock_queryset.select_related.assert_called_once_with("repository")
            mock_queryset.prefetch_related.assert_called_once_with("assignees")
            mock_queryset.filter.assert_called_once()
            assert result == mock_queryset

    def test_assignable_property_filters_unassigned_or_stale(self):
        manager = OpenIssueManager()
        manager.model = mock.Mock()

        mock_queryset = mock.Mock()

        with mock.patch.object(manager, "get_queryset", return_value=mock_queryset):
            mock_queryset.filter.return_value = mock_queryset

            result = manager.assignable

            mock_queryset.filter.assert_called_once()
            assert result == mock_queryset

    def test_without_summary_property_filters_empty_summary(self):
        manager = OpenIssueManager()
        manager.model = mock.Mock()

        mock_queryset = mock.Mock()

        with mock.patch.object(manager, "get_queryset", return_value=mock_queryset):
            mock_queryset.filter.return_value = mock_queryset

            result = manager.without_summary

            mock_queryset.filter.assert_called_once_with(summary="")
            assert result == mock_queryset
