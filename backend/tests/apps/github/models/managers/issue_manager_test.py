from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest
from django.utils import timezone

from apps.github.models.managers.issue import OpenIssueManager


class TestOpenIssueManager:
    @pytest.fixture
    def mock_queryset(self):
        return MagicMock()

    @pytest.fixture
    def open_issue_manager(self, mock_queryset):
        manager = OpenIssueManager()
        manager.get_queryset = MagicMock(return_value=mock_queryset)
        return manager

    def test_get_queryset(self):
        with patch("django.db.models.Manager.get_queryset") as mock_super_get_queryset:
            mock_qs = MagicMock()
            mock_super_get_queryset.return_value = mock_qs

            mock_qs.select_related.return_value = mock_qs
            mock_qs.prefetch_related.return_value = mock_qs
            mock_qs.filter.return_value = "filtered_queryset"

            manager = OpenIssueManager()
            result = manager.get_queryset()

            mock_qs.select_related.assert_called_once_with("repository")
            mock_qs.prefetch_related.assert_called_once_with("assignees")

            days_90_ago = timezone.now() - timedelta(days=90)
            filter_args = mock_qs.filter.call_args[1]

            assert filter_args["state"] == "open"
            assert filter_args["repository__project__isnull"] is False

            assert abs(filter_args["created_at__gte"].date() - days_90_ago.date()).days <= 1

            assert result == "filtered_queryset"

    def test_assignable_property(self, open_issue_manager, mock_queryset):
        mock_filtered = MagicMock()
        mock_queryset.filter.return_value = mock_filtered

        result = open_issue_manager.assignable

        mock_queryset.filter.assert_called_once()
        assert result == mock_filtered

    def test_without_summary_property(self, open_issue_manager, mock_queryset):
        mock_filtered = MagicMock()
        mock_queryset.filter.return_value = mock_filtered

        result = open_issue_manager.without_summary

        mock_queryset.filter.assert_called_once_with(summary="")
        assert result == mock_filtered
