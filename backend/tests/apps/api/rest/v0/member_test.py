from datetime import datetime
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest

from apps.api.rest.v0.member import MemberDetail, get_member, list_members


class TestMemberSchema:
    @pytest.mark.parametrize(
        "member_data",
        [
            {
                "avatar_url": "https://github.com/images/johndoe.png",
                "bio": "Developer advocate",
                "company": "GitHub",
                "created_at": "2024-12-30T00:00:00Z",
                "email": "john@example.com",
                "followers_count": 10,
                "following_count": 5,
                "location": "San Francisco",
                "login": "johndoe",
                "name": "John Doe",
                "public_repositories_count": 3,
                "title": "Senior Engineer",
                "twitter_username": "johndoe",
                "updated_at": "2024-12-30T00:00:00Z",
                "url": "https://github.com/johndoe",
            },
        ],
    )
    def test_user_schema(self, member_data):
        member = MemberDetail(**member_data)

        assert member.avatar_url == member_data["avatar_url"]
        assert member.bio == member_data["bio"]
        assert member.company == member_data["company"]
        assert member.created_at == datetime.fromisoformat(member_data["created_at"])
        assert member.followers_count == member_data["followers_count"]
        assert member.following_count == member_data["following_count"]
        assert member.location == member_data["location"]
        assert member.login == member_data["login"]
        assert member.name == member_data["name"]
        assert member.public_repositories_count == member_data["public_repositories_count"]
        assert member.title == member_data["title"]
        assert member.twitter_username == member_data["twitter_username"]
        assert member.updated_at == datetime.fromisoformat(member_data["updated_at"])
        assert member.url == member_data["url"]

        assert not hasattr(member, "email")


class TestListMembers:
    """Tests for list_members endpoint."""

    @patch("apps.api.rest.v0.member.UserModel")
    def test_list_members_no_ordering(self, mock_user_model):
        """Test listing members without ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_queryset = MagicMock()
        mock_user_model.objects.order_by.return_value = mock_queryset
        mock_filters.filter.return_value = mock_queryset

        result = list_members(mock_request, mock_filters, ordering=None)

        mock_user_model.objects.order_by.assert_called_with("-created_at")
        assert result == mock_queryset

    @patch("apps.api.rest.v0.member.UserModel")
    def test_list_members_with_ordering(self, mock_user_model):
        """Test listing members with custom ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_queryset = MagicMock()
        mock_user_model.objects.order_by.return_value = mock_queryset
        mock_filters.filter.return_value = mock_queryset

        result = list_members(mock_request, mock_filters, ordering="updated_at")

        mock_user_model.objects.order_by.assert_called_with("updated_at")
        assert result == mock_queryset


class TestGetMember:
    """Tests for get_member endpoint."""

    @patch("apps.api.rest.v0.member.UserModel")
    def test_get_member_success(self, mock_user_model):
        """Test getting a member when found."""
        mock_request = MagicMock()
        mock_member = MagicMock()
        mock_user_model.objects.filter.return_value.first.return_value = mock_member

        result = get_member(mock_request, "johndoe")

        mock_user_model.objects.filter.assert_called_with(login__iexact="johndoe")
        assert result == mock_member

    @patch("apps.api.rest.v0.member.UserModel")
    def test_get_member_not_found(self, mock_user_model):
        """Test getting a member when not found."""
        mock_request = MagicMock()
        mock_user_model.objects.filter.return_value.first.return_value = None

        result = get_member(mock_request, "nonexistent")

        assert result.status_code == HTTPStatus.NOT_FOUND
