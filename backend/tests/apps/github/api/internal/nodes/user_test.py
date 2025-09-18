"""Test cases for UserNode."""

from unittest.mock import Mock

import pytest

from apps.github.api.internal.nodes.user import UserNode


class TestUserNode:
    """Test cases for UserNode class."""

    def test_user_node_inheritance(self):
        """Test if UserNode inherits from BaseNode."""
        assert hasattr(UserNode, "__strawberry_definition__")

    def test_meta_configuration(self):
        """Test if Meta is properly configured."""
        field_names = {field.name for field in UserNode.__strawberry_definition__.fields}
        expected_field_names = {
            "avatar_url",
            "badges",
            "bio",
            "company",
            "contributions_count",
            "created_at",
            "email",
            "followers_count",
            "following_count",
            "id",
            "is_owasp_staff",
            "issues_count",
            "location",
            "login",
            "name",
            "public_repositories_count",
            "releases_count",
            "updated_at",
            "url",
        }
        missing = expected_field_names - field_names
        assert not missing, f"Missing fields on UserNode: {sorted(missing)}"

    def test_created_at_field(self):
        """Test created_at field resolution."""
        mock_user = Mock()
        mock_user.idx_created_at = 1234567890.0

        result = UserNode.created_at(mock_user)
        assert result == pytest.approx(1234567890.0)

    def test_issues_count_field(self):
        """Test issues_count field resolution."""
        mock_user = Mock()
        mock_user.idx_issues_count = 42

        result = UserNode.issues_count(mock_user)
        assert result == 42

    def test_releases_count_field(self):
        """Test releases_count field resolution."""
        mock_user = Mock()
        mock_user.idx_releases_count = 15

        result = UserNode.releases_count(mock_user)
        assert result == 15

    def test_updated_at_field(self):
        """Test updated_at field resolution."""
        mock_user = Mock()
        mock_user.idx_updated_at = 1234567890.0

        result = UserNode.updated_at(mock_user)
        assert result == pytest.approx(1234567890.0)

    def test_url_field(self):
        """Test url field resolution."""
        mock_user = Mock()
        mock_user.url = "https://github.com/testuser"

        result = UserNode.url(mock_user)
        assert result == "https://github.com/testuser"

    def test_badges_resolver_behavior(self):
        """Unit test verifies the badges method returns badges sorted by weight."""
        badge_high = Mock()
        badge_high.weight = 1
        badge_high.name = "High Priority Badge"

        badge_medium = Mock()
        badge_medium.weight = 5
        badge_medium.name = "Medium Priority Badge"

        badge_low = Mock()
        badge_low.weight = 10
        badge_low.name = "Low Priority Badge"

        user_badge_high = Mock()
        user_badge_high.badge = badge_high

        user_badge_medium = Mock()
        user_badge_medium.badge = badge_medium

        user_badge_low = Mock()
        user_badge_low.badge = badge_low

        sorted_user_badges = [user_badge_high, user_badge_medium, user_badge_low]

        mock_user = Mock()
        mock_queryset = Mock()
        mock_queryset.filter.return_value.order_by.return_value = sorted_user_badges
        mock_user.user_badges.select_related.return_value = mock_queryset

        result = UserNode.badges(mock_user)

        mock_user.user_badges.select_related.assert_called_once_with("badge")
        mock_queryset.filter.assert_called_once_with(is_active=True)
        mock_queryset.filter.return_value.order_by.assert_called_once_with(
            "badge__weight", "badge__name"
        )

        assert result == [ub.badge for ub in sorted_user_badges]
