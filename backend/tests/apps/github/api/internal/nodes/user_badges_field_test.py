"""Tests for badges field on GitHub UserNode."""

from unittest.mock import MagicMock

from apps.github.api.internal.nodes.user import UserNode


class TestUserNodeBadgesField:
    """Test cases for badges field on UserNode."""

    def test_badges_resolution_orders_and_filters_active(self):
        """Badges resolution should filter active and order by badge weight/name."""
        # Build a lightweight object with required attributes and methods
        user = MagicMock()
        user_badge_qs = MagicMock()
        user.badges.select_related.return_value = user_badge_qs

        # Mock chained calls: filter(...).order_by(...) -> [ub1]
        ordered_qs = MagicMock()
        ub1 = MagicMock()
        ub1.badge = MagicMock()
        user_badge_qs.filter.return_value = ordered_qs
        ordered_qs.order_by.return_value = [ub1]

        # Use the resolver through the class to keep Strawberry decorators intact
        result = UserNode.badges(user)  # pass instance as self

        user.badges.select_related.assert_called_once_with("badge")
        user_badge_qs.filter.assert_called_once_with(is_active=True)
        ordered_qs.order_by.assert_called_once_with("badge__weight", "badge__name")
        assert result == [ub1.badge]
