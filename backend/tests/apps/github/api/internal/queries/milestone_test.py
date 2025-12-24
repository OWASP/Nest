"""Test cases for MilestoneQuery."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from apps.github.api.internal.queries.milestone import MilestoneQuery, MilestoneStateEnum
from apps.github.models.milestone import Milestone


class TestMilestoneQuery:
    """Unit tests for MilestoneQuery."""

    @pytest.fixture
    def mock_milestone(self):
        milestone = Mock(spec=Milestone)
        milestone.id = 1
        return milestone

    @pytest.fixture
    def get_queryset(self):
        """Return a mocked queryset."""
        queryset = MagicMock()
        queryset.select_related.return_value.prefetch_related.return_value = queryset
        queryset.filter.return_value = queryset
        queryset.order_by.return_value = queryset
        queryset.__getitem__.return_value = [Mock()]
        return queryset

    @pytest.mark.parametrize(
        ("state", "manager"),
        [
            (MilestoneStateEnum.OPEN, "open_milestones"),
            (MilestoneStateEnum.CLOSED, "closed_milestones"),
            (None, "objects"),
        ],
    )
    def test_recent_milestones_by_state(self, get_queryset, state, manager):
        """Test fetching milestones with different valid states."""
        with patch.object(Milestone, manager, new_callable=Mock) as mock_manager:
            mock_manager.all.return_value = get_queryset

            get_queryset.select_related.return_value = get_queryset
            get_queryset.prefetch_related.return_value = get_queryset

            result = MilestoneQuery().recent_milestones(
                distinct=False,
                limit=5,
                login=None,
                organization=None,
                state=state,
            )

            assert isinstance(result, list)
            assert get_queryset.select_related.called
            assert get_queryset.prefetch_related.called

    def test_recent_milestones_with_filters(self, get_queryset):
        """Test recent milestones with login and organization filters."""
        with patch.object(Milestone, "open_milestones", new_callable=Mock) as mock_manager:
            mock_manager.all.return_value = get_queryset

            result = MilestoneQuery().recent_milestones(
                distinct=False,
                limit=3,
                login="user",
                organization="github",
                state=MilestoneStateEnum.OPEN,
            )

            get_queryset.filter.assert_any_call(author__login="user")
            get_queryset.filter.assert_any_call(repository__organization__login="github")
            assert isinstance(result, list)

    def test_recent_milestones_distinct(self):
        """Test distinct filtering with Subquery for milestones."""
        with patch.object(Milestone, "open_milestones", new_callable=Mock) as mock_manager:
            base_queryset = MagicMock()
            filtered_queryset = MagicMock()
            base_queryset.select_related.return_value.prefetch_related.return_value = base_queryset
            base_queryset.filter.return_value = filtered_queryset
            filtered_queryset.filter.return_value = filtered_queryset
            filtered_queryset.order_by.return_value = filtered_queryset
            filtered_queryset.__getitem__.return_value = [Mock()]
            mock_manager.all.return_value = base_queryset

            result = MilestoneQuery().recent_milestones(
                distinct=True,
                limit=1,
                login=None,
                organization=None,
                state=MilestoneStateEnum.OPEN,
            )

            assert isinstance(result, list)
            assert filtered_queryset.__getitem__.called

    def test_recent_milestones_with_all_parameters(self, get_queryset):
        """Test recent milestones with all parameters provided."""
        with patch.object(Milestone, "closed_milestones", new_callable=Mock) as mock_manager:
            mock_manager.all.return_value = get_queryset

            result = MilestoneQuery().recent_milestones(
                distinct=False,
                limit=10,
                login="testuser",
                organization="owasp",
                state=MilestoneStateEnum.CLOSED,
            )

        assert isinstance(result, list)
        get_queryset.filter.assert_any_call(author__login="testuser")
        get_queryset.filter.assert_any_call(repository__organization__login="owasp")
        get_queryset.__getitem__.assert_called_with(slice(None, 10))
