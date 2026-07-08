import pytest
from django.contrib.admin.sites import AdminSite

from apps.github.admin.user import MemberProfileInline, UserAdmin
from apps.github.models.user import User
from apps.owasp.models.member_profile import MemberProfile


@pytest.fixture
def user_admin_instance():
    return UserAdmin(model=User, admin_site=AdminSite())


class TestUserAdmin:
    def test_has_member_profile_inline(self, user_admin_instance):
        assert MemberProfileInline in user_admin_instance.inlines

    def test_list_display_contains_required_fields(self, user_admin_instance):
        admin_list_display = user_admin_instance.list_display

        assert "title" in admin_list_display
        assert "created_at" in admin_list_display
        assert "updated_at" in admin_list_display

    def test_search_fields_configured(self, user_admin_instance):
        search_fields = user_admin_instance.search_fields

        assert "login" in search_fields
        assert "name" in search_fields


class TestMemberProfileInline:
    def test_inline_model(self):
        assert MemberProfileInline.model == MemberProfile

    def test_inline_cannot_delete(self):
        assert not MemberProfileInline.can_delete

    def test_inline_fields(self):
        assert "owasp_slack_id" in MemberProfileInline.fields

    def test_inline_verbose_name(self):
        assert MemberProfileInline.verbose_name_plural == "OWASP Member Profile"
