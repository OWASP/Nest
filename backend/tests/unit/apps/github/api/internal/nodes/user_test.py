"""Test cases for UserNode."""

import math
from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock

import pytest

from apps.github.api.internal.dataloaders.user import (
    USER_BADGES_BY_USER_ID_LOADER,
    USER_ISSUES_COUNT_LOADER,
    USER_RELEASES_COUNT_LOADER,
)
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

        field = self._get_field_by_name("created_at", UserNode)
        result = field.base_resolver.wrapped_func(None, mock_user)
        assert math.isclose(result, 1234567890.0)

    @pytest.mark.asyncio
    async def test_issues_count_field(self):
        """Test issues_count field resolution."""
        mock_user = Mock(pk=1)
        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=42)
        mock_info = Mock()
        mock_info.context.github_dataloaders = {USER_ISSUES_COUNT_LOADER: mock_loader}

        field = self._get_field_by_name("issues_count", UserNode)
        result = await field.base_resolver.wrapped_func(None, mock_user, mock_info)
        assert result == 42

    @pytest.mark.asyncio
    async def test_releases_count_field(self):
        """Test releases_count field resolution."""
        mock_user = Mock(pk=1)
        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=15)
        mock_info = Mock()
        mock_info.context.github_dataloaders = {USER_RELEASES_COUNT_LOADER: mock_loader}

        field = self._get_field_by_name("releases_count", UserNode)
        result = await field.base_resolver.wrapped_func(None, mock_user, mock_info)
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

    @pytest.mark.asyncio
    async def test_badges_field_empty(self):
        """Test badges field resolution with no badges."""
        mock_user = Mock(pk=1)
        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=[])
        mock_info = Mock()
        mock_info.context.github_dataloaders = {USER_BADGES_BY_USER_ID_LOADER: mock_loader}

        field = self._get_field_by_name("badges", UserNode)
        result = await field.base_resolver.wrapped_func(None, mock_user, mock_info)
        assert result == []

    @pytest.mark.asyncio
    async def test_badges_field_single_badge(self):
        """Test badges field resolution with single badge."""
        mock_user = Mock(pk=1)
        mock_badge = Mock(spec=BadgeNode)
        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=[mock_badge])
        mock_info = Mock()
        mock_info.context.github_dataloaders = {USER_BADGES_BY_USER_ID_LOADER: mock_loader}

        field = self._get_field_by_name("badges", UserNode)
        result = await field.base_resolver.wrapped_func(None, mock_user, mock_info)
        assert result == [mock_badge]

    @pytest.mark.asyncio
    async def test_badges_field_sorted_by_weight_and_name(self):
        """Test badges field resolution with multiple badges sorted by weight and name."""
        mock_user = Mock(pk=1)

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

        expected_badges = [
            mock_badge_low_weight,
            mock_badge_medium_weight_a,
            mock_badge_medium_weight_b,
            mock_badge_high_weight,
        ]

        mock_loader = Mock()
        mock_loader.load = AsyncMock(return_value=expected_badges)
        mock_info = Mock()
        mock_info.context.github_dataloaders = {USER_BADGES_BY_USER_ID_LOADER: mock_loader}

        field = self._get_field_by_name("badges", UserNode)
        result = await field.base_resolver.wrapped_func(None, mock_user, mock_info)

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
