"""Tests for Milestone managers."""

from unittest import mock

from apps.github.models.managers.milestone import (
    ClosedMilestoneManager,
    OpenMilestoneManager,
)


class TestOpenMilestoneManager:
    def test_get_queryset_filters_by_open_state(self):
        manager = OpenMilestoneManager()
        manager.model = mock.Mock()

        mock_queryset = mock.Mock()

        with mock.patch("django.db.models.Manager.get_queryset", return_value=mock_queryset):
            mock_queryset.filter.return_value = mock_queryset

            result = manager.get_queryset()

            mock_queryset.filter.assert_called_once_with(state="open")
            assert result == mock_queryset


class TestClosedMilestoneManager:
    def test_get_queryset_filters_by_closed_state(self):
        manager = ClosedMilestoneManager()
        manager.model = mock.Mock()

        mock_queryset = mock.Mock()

        with mock.patch("django.db.models.Manager.get_queryset", return_value=mock_queryset):
            mock_queryset.filter.return_value = mock_queryset

            result = manager.get_queryset()

            mock_queryset.filter.assert_called_once_with(state="closed")
            assert result == mock_queryset
