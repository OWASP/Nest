import pytest
from django.core.exceptions import ValidationError

from apps.github.models.user import User
from apps.owasp.models.member_profile import MemberProfile


class TestMemberProfileModel:
    def test_str_representation(self):
        user = User(login="testuser")
        profile = MemberProfile(github_user=user)

        assert str(profile) == "OWASP member profile for testuser"

    def test_meta_options(self):
        assert MemberProfile._meta.db_table == "owasp_member_profiles"
        assert MemberProfile._meta.verbose_name_plural == "Member Profiles"

    def test_github_user_field(self):
        field = MemberProfile._meta.get_field("github_user")

        assert field.one_to_one
        assert field.remote_field.on_delete.__name__ == "CASCADE"
        assert field.remote_field.related_name == "owasp_profile"

    def test_owasp_slack_id_field(self):
        field = MemberProfile._meta.get_field("owasp_slack_id")

        assert field.max_length == 20
        assert field.blank
        assert field.default == ""

    def test_has_timestamp_fields(self):
        assert hasattr(MemberProfile, "nest_created_at")
        assert hasattr(MemberProfile, "nest_updated_at")

    def test_linkedin_page_id_field(self):
        field = MemberProfile._meta.get_field("linkedin_page_id")

        assert field.max_length == 100
        assert field.blank
        assert field.default == ""

    def test_linkedin_page_id_valid_values(self):
        user = User(login="testuser")
        profile = MemberProfile(github_user=user)

        # Test valid LinkedIn IDs
        valid_ids = [
            "john-doe",
            "john-doe-123",
            "johndoe",
            "john123",
            "a-b-c",
            "abc",  # minimum 3 characters
            "a" * 100,  # maximum 100 characters
        ]

        for linkedin_id in valid_ids:
            profile.linkedin_page_id = linkedin_id
            profile.full_clean(exclude=["github_user"])  # Should not raise ValidationError

    def test_linkedin_page_id_invalid_values(self):
        user = User(login="testuser")
        profile = MemberProfile(github_user=user)

        # Test invalid LinkedIn IDs
        invalid_ids = [
            "ab",  # too short (< 3 characters)
            "john doe",  # contains space
            "john_doe",  # contains underscore
            "john.doe",  # contains period
            "john@doe",  # contains @
            "john/doe",  # contains slash
            "a" * 101,  # too long (> 100 characters)
        ]

        for linkedin_id in invalid_ids:
            profile.linkedin_page_id = linkedin_id
            with pytest.raises(ValidationError):
                profile.full_clean(exclude=["github_user"])

    def test_linkedin_page_id_blank_allowed(self):
        user = User(login="testuser")
        profile = MemberProfile(github_user=user, linkedin_page_id="")

        # Should not raise ValidationError for blank value
        profile.full_clean(exclude=["github_user"])
