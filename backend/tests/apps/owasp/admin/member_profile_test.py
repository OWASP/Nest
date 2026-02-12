"""Tests for MemberProfile admin."""

from unittest import mock
from unittest.mock import MagicMock, Mock

from django.contrib.admin.sites import AdminSite

from apps.owasp.admin.member_profile import MemberProfileAdmin
from apps.owasp.models.member_profile import MemberProfile


class TestMemberProfileAdmin:
    def test_list_display(self):
        admin = MemberProfileAdmin(MemberProfile, AdminSite())

        expected_fields = (
            "github_user",
            "owasp_slack_id",
            "first_contribution_at",
            "is_owasp_board_member",
            "is_former_owasp_staff",
            "is_gsoc_mentor",
            "nest_created_at",
        )

        assert admin.list_display == expected_fields

    def test_list_filter(self):
        admin = MemberProfileAdmin(MemberProfile, AdminSite())

        expected_filters = (
            "is_owasp_board_member",
            "is_former_owasp_staff",
            "is_gsoc_mentor",
            "nest_created_at",
        )

        assert admin.list_filter == expected_filters

    def test_search_fields(self):
        admin = MemberProfileAdmin(MemberProfile, AdminSite())

        expected_search = (
            "github_user__login",
            "github_user__name",
            "owasp_slack_id",
        )

        assert admin.search_fields == expected_search

    def test_readonly_fields(self):
        admin = MemberProfileAdmin(MemberProfile, AdminSite())

        expected_readonly = (
            "nest_created_at",
            "nest_updated_at",
        )

        assert admin.readonly_fields == expected_readonly

    def test_autocomplete_fields(self):
        admin = MemberProfileAdmin(MemberProfile, AdminSite())

        expected_autocomplete = ("github_user",)

        assert admin.autocomplete_fields == expected_autocomplete

    def test_has_fieldsets(self):
        admin = MemberProfileAdmin(MemberProfile, AdminSite())

        assert admin.fieldsets is not None
        assert len(admin.fieldsets) == 4

        assert admin.fieldsets[0][0] == "User Information"
        assert admin.fieldsets[1][0] == "Contribution Information"
        assert admin.fieldsets[2][0] == "Membership Flags"
        assert admin.fieldsets[3][0] == "Timestamps"

    def test_get_queryset(self):
        """Test get_queryset applies select_related for github_user."""
        admin = MemberProfileAdmin(MemberProfile, AdminSite())

        mock_request = Mock()

        mock_queryset = MagicMock()
        mock_related_queryset = MagicMock()
        mock_queryset.select_related.return_value = mock_related_queryset

        with MagicMock() as mock_super:
            mock_super.return_value = mock_queryset
            admin.__class__.__bases__[0].get_queryset = mock_super

            admin_queryset = MagicMock()
            result_queryset = MagicMock()
            admin_queryset.select_related.return_value = result_queryset

            with mock.patch.object(
                admin.__class__.__bases__[0], "get_queryset", return_value=admin_queryset
            ):
                result = admin.get_queryset(mock_request)

                admin_queryset.select_related.assert_called_once_with("github_user")
                assert result == result_queryset
