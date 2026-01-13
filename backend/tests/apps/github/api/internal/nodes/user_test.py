"""Test cases for UserNode."""

import math
from unittest.mock import Mock

from apps.github.api.internal.nodes.user import UserNode
from apps.nest.api.internal.nodes.badge import BadgeNode


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
            "badge_count",
            "badges",
            "bio",
            "company",
            "contribution_data",
            "contributions_count",
            "created_at",
            "email",
            "first_owasp_contribution_at",
            "followers_count",
            "following_count",
            "id",
            "is_former_owasp_staff",
            "is_gsoc_mentor",
            "is_owasp_board_member",
            "is_owasp_staff",
            "issues_count",
            "linkedin_page_id",
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
        assert math.isclose(result, 1234567890.0)

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
        assert math.isclose(result, 1234567890.0)

    def test_url_field(self):
        """Test url field resolution."""
        mock_user = Mock()
        mock_user.url = "https://github.com/testuser"

        result = UserNode.url(mock_user)
        assert result == "https://github.com/testuser"

    def test_badge_count_field(self):
        """Test badge_count field resolution."""
        mock_user = Mock()
        mock_badges_queryset = Mock()
        mock_badges_queryset.filter.return_value.count.return_value = 3
        mock_user.user_badges = mock_badges_queryset

        result = UserNode.badge_count(mock_user)
        assert result == 3
        mock_badges_queryset.filter.assert_called_once_with(is_active=True)
        mock_badges_queryset.filter.return_value.count.assert_called_once()

    def test_badges_field_empty(self):
        """Test badges field resolution with no badges."""
        mock_user = Mock()
        mock_badges_queryset = Mock()
        mock_filter = mock_badges_queryset.filter.return_value
        mock_select_related = mock_filter.select_related.return_value
        mock_select_related.order_by.return_value = []
        mock_user.user_badges = mock_badges_queryset

        result = UserNode.badges(mock_user)
        assert result == []
        mock_badges_queryset.filter.assert_called_once_with(is_active=True)
        mock_filter.select_related.assert_called_once_with("badge")
        mock_select_related.order_by.assert_called_once_with("badge__weight", "badge__name")

    def test_badges_field_single_badge(self):
        """Test badges field resolution with single badge."""
        mock_user = Mock()
        mock_badge = Mock(spec=BadgeNode)
        mock_user_badge = Mock()
        mock_user_badge.badge = mock_badge

        mock_badges_queryset = Mock()
        mock_filter = mock_badges_queryset.filter.return_value
        mock_select_related = mock_filter.select_related.return_value
        mock_select_related.order_by.return_value = [mock_user_badge]
        mock_user.user_badges = mock_badges_queryset

        result = UserNode.badges(mock_user)
        assert result == [mock_badge]
        mock_badges_queryset.filter.assert_called_once_with(is_active=True)
        mock_filter.select_related.assert_called_once_with("badge")
        mock_select_related.order_by.assert_called_once_with("badge__weight", "badge__name")

    def test_badges_field_sorted_by_weight_and_name(self):
        """Test badges field resolution with multiple badges sorted by weight and name."""
        # Create mock badges with different weights and names
        mock_badge_high_weight = Mock(spec=BadgeNode)
        mock_badge_high_weight.weight = 100
        mock_badge_high_weight.name = "High Weight Badge"

        mock_badge_medium_weight_a = Mock(spec=BadgeNode)
        mock_badge_medium_weight_a.weight = 50
        mock_badge_medium_weight_a.name = "Medium Weight A"

        mock_badge_medium_weight_b = Mock(spec=BadgeNode)
        mock_badge_medium_weight_b.weight = 50
        mock_badge_medium_weight_b.name = "Medium Weight B"

        mock_badge_low_weight = Mock(spec=BadgeNode)
        mock_badge_low_weight.weight = 10
        mock_badge_low_weight.name = "Low Weight Badge"

        # Create mock user badges
        mock_user_badge_high = Mock()
        mock_user_badge_high.badge = mock_badge_high_weight

        mock_user_badge_medium_a = Mock()
        mock_user_badge_medium_a.badge = mock_badge_medium_weight_a

        mock_user_badge_medium_b = Mock()
        mock_user_badge_medium_b.badge = mock_badge_medium_weight_b

        mock_user_badge_low = Mock()
        mock_user_badge_low.badge = mock_badge_low_weight

        # Set up the mock queryset to return badges in the expected sorted order
        # (lowest weight first, then by name for same weight)
        mock_badges_queryset = Mock()
        mock_filter = mock_badges_queryset.filter.return_value
        mock_select_related = mock_filter.select_related.return_value
        mock_select_related.order_by.return_value = [
            mock_user_badge_low,  # weight 10
            mock_user_badge_medium_a,  # weight 50, name "Medium Weight A"
            mock_user_badge_medium_b,  # weight 50, name "Medium Weight B"
            mock_user_badge_high,  # weight 100
        ]
        mock_user = Mock()
        mock_user.user_badges = mock_badges_queryset

        result = UserNode.badges(mock_user)

        # Verify the badges are returned in the correct order
        expected_badges = [
            mock_badge_low_weight,
            mock_badge_medium_weight_a,
            mock_badge_medium_weight_b,
            mock_badge_high_weight,
        ]
        assert result == expected_badges

        # Verify the queryset was called with correct ordering
        mock_badges_queryset.filter.assert_called_once_with(is_active=True)
        mock_filter.select_related.assert_called_once_with("badge")
        mock_select_related.order_by.assert_called_once_with("badge__weight", "badge__name")

    def test_first_owasp_contribution_at_with_profile(self):
        """Test first_owasp_contribution_at returns timestamp when profile exists."""
        from datetime import UTC, datetime

        mock_profile = Mock()
        mock_profile.first_contribution_at = datetime(2025, 1, 15, tzinfo=UTC)

        mock_user = Mock()
        mock_user.owasp_profile = mock_profile

        result = UserNode.first_owasp_contribution_at(mock_user)

        assert result == mock_profile.first_contribution_at.timestamp()

    def test_first_owasp_contribution_at_without_profile(self):
        """Test first_owasp_contribution_at returns None when no profile."""
        mock_user = Mock(spec=[])

        result = UserNode.first_owasp_contribution_at(mock_user)

        assert result is None

    def test_is_owasp_board_member_true(self):
        """Test is_owasp_board_member returns True when flag is set."""
        mock_profile = Mock()
        mock_profile.is_owasp_board_member = True

        mock_user = Mock()
        mock_user.owasp_profile = mock_profile

        result = UserNode.is_owasp_board_member(mock_user)

        assert result is True

    def test_is_owasp_board_member_without_profile(self):
        """Test is_owasp_board_member returns False when no profile."""
        mock_user = Mock(spec=[])

        result = UserNode.is_owasp_board_member(mock_user)

        assert result is False

    def test_is_former_owasp_staff_true(self):
        """Test is_former_owasp_staff returns True when flag is set."""
        mock_profile = Mock()
        mock_profile.is_former_owasp_staff = True

        mock_user = Mock()
        mock_user.owasp_profile = mock_profile

        result = UserNode.is_former_owasp_staff(mock_user)

        assert result is True

    def test_is_former_owasp_staff_without_profile(self):
        """Test is_former_owasp_staff returns False when no profile."""
        mock_user = Mock(spec=[])

        result = UserNode.is_former_owasp_staff(mock_user)

        assert result is False

    def test_is_gsoc_mentor_true(self):
        """Test is_gsoc_mentor returns True when flag is set."""
        mock_profile = Mock()
        mock_profile.is_gsoc_mentor = True

        mock_user = Mock()
        mock_user.owasp_profile = mock_profile

        result = UserNode.is_gsoc_mentor(mock_user)

        assert result is True

    def test_is_gsoc_mentor_without_profile(self):
        """Test is_gsoc_mentor returns False when no profile."""
        mock_user = Mock(spec=[])

        result = UserNode.is_gsoc_mentor(mock_user)

        assert result is False

    def test_linkedin_page_id_with_profile_and_value(self):
        """Test linkedin_page_id returns ID when profile exists with value."""
        mock_profile = Mock()
        mock_profile.linkedin_page_id = "john-doe-123"

        mock_user = Mock()
        mock_user.owasp_profile = mock_profile

        result = UserNode.linkedin_page_id(mock_user)

        assert result == "john-doe-123"

    def test_linkedin_page_id_with_profile_empty_value(self):
        """Test linkedin_page_id returns empty string when profile has empty value."""
        mock_profile = Mock()
        mock_profile.linkedin_page_id = ""

        mock_user = Mock()
        mock_user.owasp_profile = mock_profile

        result = UserNode.linkedin_page_id(mock_user)

        assert result == ""

    def test_linkedin_page_id_without_profile(self):
        """Test linkedin_page_id returns empty string when no profile."""
        mock_user = Mock(spec=[])

        result = UserNode.linkedin_page_id(mock_user)

        assert result == ""
