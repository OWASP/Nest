from unittest.mock import MagicMock

import pytest
from django.contrib import messages
from django.contrib.admin.sites import AdminSite

from apps.slack.admin.member import MemberAdmin
from apps.slack.models.member import Member


@pytest.fixture
def admin_instance():
    return MemberAdmin(model=Member, admin_site=AdminSite())


class TestMemberAdmin:
    def test_approve_suggested_users_success(self, admin_instance):
        request = MagicMock()
        mock_suggested_user = MagicMock()
        mock_member = MagicMock()

        mock_member.suggested_users.all.return_value.count.return_value = 1
        mock_member.suggested_users.all.return_value.first.return_value = mock_suggested_user

        admin_instance.message_user = MagicMock()
        queryset = [mock_member]

        admin_instance.approve_suggested_users(request, queryset)

        assert mock_member.user == mock_suggested_user
        mock_member.save.assert_called_once()
        admin_instance.message_user.assert_called_with(
            request, f" assigned user for {mock_member}.", messages.SUCCESS
        )

    def test_approve_suggested_users_multiple_error(self, admin_instance):
        request = MagicMock()
        mock_member = MagicMock()

        mock_member.suggested_users.all.return_value.count.return_value = 2

        admin_instance.message_user = MagicMock()
        queryset = [mock_member]

        admin_instance.approve_suggested_users(request, queryset)

        mock_member.save.assert_not_called()
        expected_message = (
            f"Error: Multiple suggested users found for {mock_member}. "
            f"Only one user can be assigned due to the one-to-one constraint."
        )

        admin_instance.message_user.assert_called_with(request, expected_message, messages.ERROR)

    def test_approve_suggested_users_none_warning(self, admin_instance):
        request = MagicMock()
        mock_member = MagicMock()

        mock_member.suggested_users.all.return_value.count.return_value = 0

        admin_instance.message_user = MagicMock()
        queryset = [mock_member]

        admin_instance.approve_suggested_users(request, queryset)

        mock_member.save.assert_not_called()
        admin_instance.message_user.assert_called_with(
            request, f"No suggested users found for {mock_member}.", messages.WARNING
        )
