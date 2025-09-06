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
        """Unit test verifies the resolver's interaction with the ORM and sorting logic."""
        user = Mock()

        # Created some mock user badges with specific weights (unsorted order)
        ub_heavy = Mock()
        ub_heavy.badge = Mock()
        ub_heavy.badge.weight = 30
        ub_heavy.badge.name = "Heavy Badge"

        ub_light = Mock()
        ub_light.badge = Mock()
        ub_light.badge.weight = 10
        ub_light.badge.name = "Light Badge"

        ub_medium = Mock()
        ub_medium.badge = Mock()
        ub_medium.badge.weight = 20
        ub_medium.badge.name = "Medium Badge"

        unsorted_badges = [ub_heavy, ub_light, ub_medium]

        (
            user.user_badges.select_related.return_value.filter.return_value.order_by.return_value
        ) = unsorted_badges

        result = UserNode.badges(user)

        user.user_badges.select_related.assert_called_once_with("badge")
        user.user_badges.select_related.return_value.filter.assert_called_once_with(is_active=True)
        user.user_badges.select_related.return_value.filter.return_value.order_by.assert_called_once_with(
            "-badge__weight", "badge__name"
        )

        assert result == [ub.badge for ub in unsorted_badges]

        result_weights = [badge.weight for badge in result]
        assert result_weights == [
            30,
            10,
            20,
        ]
