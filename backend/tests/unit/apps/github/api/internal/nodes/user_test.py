"""Test cases for UserNode."""

import math
from datetime import UTC, datetime
from unittest.mock import Mock

from apps.github.api.internal.nodes.user import UserNode
from apps.nest.api.internal.nodes.badge import BadgeNode
from tests.unit.apps.common.graphql_node_base_test import GraphQLNodeBaseTest


class TestUserNode(GraphQLNodeBaseTest):
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
            "contribution_data",
            "contribution_score",
            "contributions_count",
            "created_at",
            "current_certificate",
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
            "tier",
            "updated_at",
            "url",
        }
        missing = expected_field_names - field_names
        assert not missing, f"Missing fields on UserNode: {sorted(missing)}"

    def test_created_at_field(self):
        """Test created_at field resolution."""
        mock_user = Mock()
        mock_user.idx_created_at = 1234567890.0

        field = self._get_field_by_name("created_at", UserNode)
        result = field.base_resolver.wrapped_func(None, mock_user)
        assert math.isclose(result, 1234567890.0)

    def test_issues_count_field(self):
        """Test issues_count field resolution."""
        mock_user = Mock()
        mock_user.idx_issues_count = 42

        field = self._get_field_by_name("issues_count", UserNode)
        result = field.base_resolver.wrapped_func(None, mock_user)
        assert result == 42

    def test_releases_count_field(self):
        """Test releases_count field resolution."""
        mock_user = Mock()
        mock_user.idx_releases_count = 15

        field = self._get_field_by_name("releases_count", UserNode)
        result = field.base_resolver.wrapped_func(None, mock_user)
        assert result == 15

    def test_updated_at_field(self):
        """Test updated_at field resolution."""
        mock_user = Mock()
        mock_user.idx_updated_at = 1234567890.0

        field = self._get_field_by_name("updated_at", UserNode)
        result = field.base_resolver.wrapped_func(None, mock_user)
        assert math.isclose(result, 1234567890.0)

    def test_url_field(self):
        """Test url field resolution."""
        mock_user = Mock()
        mock_user.url = "https://github.com/testuser"

        field = self._get_field_by_name("url", UserNode)
        result = field.base_resolver.wrapped_func(None, mock_user)
        assert result == "https://github.com/testuser"

    def test_badges_field_empty(self):
        """Test badges field resolution with no badges."""
        mock_user = Mock()
        mock_user.user_badges_list = []

        field = self._get_field_by_name("badges", UserNode)
        result = field.base_resolver.wrapped_func(None, mock_user)
        assert result == []

    def test_badges_field_single_badge(self):
        """Test badges field resolution with single badge."""
        mock_user = Mock()
        mock_badge = Mock(spec=BadgeNode)
        mock_user_badge = Mock()
        mock_user_badge.badge = mock_badge

        mock_user.user_badges_list = [mock_user_badge]
        field = self._get_field_by_name("badges", UserNode)
        result = field.base_resolver.wrapped_func(None, mock_user)
        assert result == [mock_badge]

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
        mock_user = Mock()
        mock_user.user_badges_list = [
            mock_user_badge_low,  # weight 10
            mock_user_badge_medium_a,  # weight 50, name "Medium Weight A"
            mock_user_badge_medium_b,  # weight 50, name "Medium Weight B"
            mock_user_badge_high,  # weight 100
        ]

        field = self._get_field_by_name("badges", UserNode)
        result = field.base_resolver.wrapped_func(None, mock_user)

        # Verify the badges are returned in the correct order
        expected_badges = [
            mock_badge_low_weight,
            mock_badge_medium_weight_a,
            mock_badge_medium_weight_b,
            mock_badge_high_weight,
        ]
        assert result == expected_badges

    def test_first_owasp_contribution_at_with_profile(self):
        """Test first_owasp_contribution_at returns ISO string when profile exists."""
        mock_profile = Mock()
        mock_profile.first_contribution_at = datetime(2025, 1, 15, tzinfo=UTC)

        mock_user = Mock()
        mock_user.owasp_profile = mock_profile

        field = self._get_field_by_name("first_owasp_contribution_at", UserNode)
        result = field.base_resolver.wrapped_func(None, mock_user)

        assert result == mock_profile.first_contribution_at.isoformat()

    def test_first_owasp_contribution_at_without_profile(self):
        """Test first_owasp_contribution_at returns None when no profile."""
        mock_user = Mock(spec=[])

        field = self._get_field_by_name("first_owasp_contribution_at", UserNode)
        result = field.base_resolver.wrapped_func(None, mock_user)

        assert result is None

    def test_is_owasp_board_member_true(self):
        """Test is_owasp_board_member returns True when flag is set."""
        mock_profile = Mock()
        mock_profile.is_owasp_board_member = True

        mock_user = Mock()
        mock_user.owasp_profile = mock_profile

        field = self._get_field_by_name("is_owasp_board_member", UserNode)
        result = field.base_resolver.wrapped_func(None, mock_user)

        assert result

    def test_is_owasp_board_member_without_profile(self):
        """Test is_owasp_board_member returns False when no profile."""
        mock_user = Mock(spec=[])

        field = self._get_field_by_name("is_owasp_board_member", UserNode)
        result = field.base_resolver.wrapped_func(None, mock_user)

        assert not result

    def test_is_former_owasp_staff_true(self):
        """Test is_former_owasp_staff returns True when flag is set."""
        mock_profile = Mock()
        mock_profile.is_former_owasp_staff = True

        mock_user = Mock()
        mock_user.owasp_profile = mock_profile

        field = self._get_field_by_name("is_former_owasp_staff", UserNode)
        result = field.base_resolver.wrapped_func(None, mock_user)

        assert result

    def test_is_former_owasp_staff_without_profile(self):
        """Test is_former_owasp_staff returns False when no profile."""
        mock_user = Mock(spec=[])

        field = self._get_field_by_name("is_former_owasp_staff", UserNode)
        result = field.base_resolver.wrapped_func(None, mock_user)

        assert not result

    def test_is_gsoc_mentor_true(self):
        """Test is_gsoc_mentor returns True when flag is set."""
        mock_profile = Mock()
        mock_profile.is_gsoc_mentor = True

        mock_user = Mock()
        mock_user.owasp_profile = mock_profile

        field = self._get_field_by_name("is_gsoc_mentor", UserNode)
        result = field.base_resolver.wrapped_func(None, mock_user)

        assert result

    def test_is_gsoc_mentor_without_profile(self):
        """Test is_gsoc_mentor returns False when no profile."""
        mock_user = Mock(spec=[])

        field = self._get_field_by_name("is_gsoc_mentor", UserNode)
        result = field.base_resolver.wrapped_func(None, mock_user)

        assert not result

    def test_linkedin_page_id_with_profile_and_value(self):
        """Test linkedin_page_id returns ID when profile exists with value."""
        mock_profile = Mock()
        mock_profile.linkedin_page_id = "john-doe-123"

        mock_user = Mock()
        mock_user.owasp_profile = mock_profile

        field = self._get_field_by_name("linkedin_page_id", UserNode)
        result = field.base_resolver.wrapped_func(None, mock_user)

        assert result == "john-doe-123"

    def test_linkedin_page_id_with_profile_empty_value(self):
        """Test linkedin_page_id returns empty string when profile has empty value."""
        mock_profile = Mock()
        mock_profile.linkedin_page_id = ""

        mock_user = Mock()
        mock_user.owasp_profile = mock_profile

        field = self._get_field_by_name("linkedin_page_id", UserNode)
        result = field.base_resolver.wrapped_func(None, mock_user)

        assert result == ""

    def test_linkedin_page_id_without_profile(self):
        """Test linkedin_page_id returns empty string when no profile."""
        mock_user = Mock(spec=[])

        field = self._get_field_by_name("linkedin_page_id", UserNode)
        result = field.base_resolver.wrapped_func(None, mock_user)

        assert result == ""

    def test_current_certificate_uses_prefetched_certificates(self):
        """Test current_certificate returns the first prefetched active certificate."""
        latest_certificate = Mock()
        older_certificate = Mock()
        mock_user = Mock()
        mock_user.user_certificates = [latest_certificate, older_certificate]

        field = self._get_field_by_name("current_certificate", UserNode)
        result = field.base_resolver.wrapped_func(None, mock_user)

        assert result is latest_certificate
        mock_user.certificates.filter.assert_not_called()

    def test_current_certificate_prefetched_empty(self):
        """Test current_certificate returns None when the prefetched list is empty."""
        mock_user = Mock()
        mock_user.user_certificates = []

        field = self._get_field_by_name("current_certificate", UserNode)
        result = field.base_resolver.wrapped_func(None, mock_user)

        assert result is None
        mock_user.certificates.filter.assert_not_called()

    def test_current_certificate_falls_back_to_query_without_prefetch(self):
        """Test current_certificate queries active certificates when not prefetched."""
        certificate = Mock()
        mock_user = Mock(spec=["certificates"])
        mock_queryset = mock_user.certificates.filter.return_value
        mock_queryset.order_by.return_value.first.return_value = certificate

        field = self._get_field_by_name("current_certificate", UserNode)
        result = field.base_resolver.wrapped_func(None, mock_user)

        assert result is certificate
        mock_user.certificates.filter.assert_called_once_with(is_revoked=False)
        mock_queryset.order_by.assert_called_once_with("-issued_at")
        mock_queryset.order_by.return_value.first.assert_called_once_with()

    def test_current_certificate_fallback_without_certificates(self):
        """Test current_certificate fallback returns None when the user has no certificate."""
        mock_user = Mock(spec=["certificates"])
        mock_queryset = mock_user.certificates.filter.return_value
        mock_queryset.order_by.return_value.first.return_value = None

        field = self._get_field_by_name("current_certificate", UserNode)
        result = field.base_resolver.wrapped_func(None, mock_user)

        assert result is None

    def test_contribution_score_without_score(self):
        """Test contribution_score returns None when the user has no score."""
        mock_user = Mock(spec=[])

        field = self._get_field_by_name("contribution_score", UserNode)
        result = field.base_resolver.wrapped_func(None, mock_user)

        assert result is None

    def test_contribution_score_with_none_score(self):
        """Test contribution_score returns None when the score relation is None."""
        mock_user = Mock()
        mock_user.contribution_score = None

        field = self._get_field_by_name("contribution_score", UserNode)
        result = field.base_resolver.wrapped_func(None, mock_user)

        assert result is None

    def test_contribution_score_with_score(self):
        """Test contribution_score returns the score value."""
        mock_user = Mock()
        mock_user.contribution_score.value = 275

        field = self._get_field_by_name("contribution_score", UserNode)
        result = field.base_resolver.wrapped_func(None, mock_user)

        assert result == 275

    def test_tier_without_score(self):
        """Test tier returns None when the user has no score."""
        mock_user = Mock(spec=[])

        field = self._get_field_by_name("tier", UserNode)
        result = field.base_resolver.wrapped_func(None, mock_user)

        assert result is None

    def test_tier_with_score(self):
        """Test tier returns the human-readable tier label."""
        mock_user = Mock()
        mock_user.contribution_score.get_tier_display.return_value = "Level 3"

        field = self._get_field_by_name("tier", UserNode)
        result = field.base_resolver.wrapped_func(None, mock_user)

        assert result == "Level 3"
        mock_user.contribution_score.get_tier_display.assert_called_once_with()
