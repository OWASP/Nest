"""Tests for GitHub app UserAdmin and MemberProfileInline."""

from django.contrib.admin.sites import AdminSite

from apps.github.admin.user import MemberProfileInline, UserAdmin
from apps.github.models.user import User
from apps.owasp.models.member_profile import MemberProfile


class TestUserAdmin:
    """Test cases for UserAdmin."""

    def setup_method(self):
        """Set up test fixtures."""
        self.site = AdminSite()
        self.admin = UserAdmin(User, self.site)

    # --- configuration ---

    def test_list_display_contains_expected_fields(self):
        """Test list_display contains all required column fields."""
        assert "title" in self.admin.list_display
        assert "created_at" in self.admin.list_display
        assert "updated_at" in self.admin.list_display

    def test_search_fields_contains_login_and_name(self):
        """Test search_fields allows querying by login and name."""
        assert "login" in self.admin.search_fields
        assert "name" in self.admin.search_fields

    def test_inlines_contains_member_profile_inline(self):
        """Test the UserAdmin includes the MemberProfileInline."""
        assert MemberProfileInline in self.admin.inlines

    def test_inlines_count(self):
        """Test exactly one inline is registered."""
        assert len(self.admin.inlines) == 1


class TestMemberProfileInline:
    """Test cases for MemberProfileInline."""

    def test_inline_model_is_member_profile(self):
        """Test the inline is bound to the MemberProfile model."""
        assert MemberProfileInline.model == MemberProfile

    def test_inline_cannot_delete(self):
        """Test the inline does not allow deletion."""
        assert MemberProfileInline.can_delete is False

    def test_inline_verbose_name_plural(self):
        """Test the inline has a meaningful verbose_name_plural."""
        assert MemberProfileInline.verbose_name_plural == "OWASP Member Profile"

    def test_inline_fields_contains_slack_id(self):
        """Test inline fields include owasp_slack_id."""
        assert "owasp_slack_id" in MemberProfileInline.fields

    def test_inline_fields_contains_membership_flags(self):
        """Test inline fields include the three membership flag fields."""
        assert "is_owasp_board_member" in MemberProfileInline.fields
        assert "is_former_owasp_staff" in MemberProfileInline.fields
        assert "is_gsoc_mentor" in MemberProfileInline.fields

    def test_inline_fields_contains_contribution_date(self):
        """Test inline fields include first_contribution_at."""
        assert "first_contribution_at" in MemberProfileInline.fields

    def test_inline_readonly_fields_contains_contribution_date(self):
        """Test first_contribution_at is read-only in the inline."""
        assert "first_contribution_at" in MemberProfileInline.readonly_fields
