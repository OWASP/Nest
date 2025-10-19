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

        assert field.one_to_one is True
        assert field.remote_field.on_delete.__name__ == "CASCADE"
        assert field.remote_field.related_name == "owasp_profile"

    def test_owasp_slack_id_field(self):
        field = MemberProfile._meta.get_field("owasp_slack_id")

        assert field.max_length == 20
        assert field.blank is True
        assert field.default == ""

    def test_has_timestamp_fields(self):
        assert hasattr(MemberProfile, "nest_created_at")
        assert hasattr(MemberProfile, "nest_updated_at")
