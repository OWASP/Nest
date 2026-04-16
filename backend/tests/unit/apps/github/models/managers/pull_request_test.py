"""Tests for PullRequest managers."""

from unittest import mock

from apps.github.models.managers.pull_request import OpenPullRequestManager


class TestOpenPullRequestManager:
    def test_get_queryset_adds_select_related(self):
        manager = OpenPullRequestManager()
        manager.model = mock.Mock()

        mock_queryset = mock.Mock()
        mock_super_queryset = mock.Mock()
        mock_super_queryset.get_queryset.return_value = mock_queryset

        with mock.patch("django.db.models.Manager.get_queryset", return_value=mock_queryset):
            mock_queryset.select_related.return_value = mock_queryset
            mock_queryset.prefetch_related.return_value = mock_queryset

            result = manager.get_queryset()

            mock_queryset.select_related.assert_called_once_with("repository")
            mock_queryset.prefetch_related.assert_called_once_with("assignees")
            assert result == mock_queryset
