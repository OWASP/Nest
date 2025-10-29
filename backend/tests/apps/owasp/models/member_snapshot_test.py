from datetime import UTC, datetime

from apps.github.models.user import User
from apps.owasp.models.member_snapshot import MemberSnapshot


class TestMemberSnapshotModel:
    def test_str_representation(self):
        user = User(login="testuser")
        snapshot = MemberSnapshot(
            github_user=user,
            start_at=datetime(2025, 1, 1, tzinfo=UTC),
            end_at=datetime(2025, 1, 31, tzinfo=UTC),
        )

        assert str(snapshot) == "testuser snapshot (2025-01-01 to 2025-01-31)"

    def test_meta_options(self):
        assert MemberSnapshot._meta.db_table == "owasp_member_snapshots"
        assert MemberSnapshot._meta.verbose_name_plural == "Member Snapshots"

    def test_unique_together_constraint(self):
        unique_together = MemberSnapshot._meta.unique_together
        assert ("github_user", "start_at", "end_at") in unique_together

    def test_has_indexes(self):
        indexes = MemberSnapshot._meta.indexes
        assert len(indexes) == 0

    def test_github_user_field(self):
        field = MemberSnapshot._meta.get_field("github_user")

        assert field.remote_field.on_delete.__name__ == "CASCADE"
        assert field.remote_field.related_name == "contribution_snapshots"

    def test_has_timestamp_fields(self):
        assert hasattr(MemberSnapshot, "nest_created_at")
        assert hasattr(MemberSnapshot, "nest_updated_at")

    def test_has_contribution_heatmap_data_field(self):
        field = MemberSnapshot._meta.get_field("contribution_heatmap_data")

        assert field.get_internal_type() == "JSONField"
        assert field.blank is True
        assert callable(field.default)

    def test_has_m2m_fields(self):
        assert hasattr(MemberSnapshot, "commits")
        assert hasattr(MemberSnapshot, "pull_requests")
        assert hasattr(MemberSnapshot, "issues")
        assert hasattr(MemberSnapshot, "messages")

    def test_has_count_properties(self):
        assert hasattr(MemberSnapshot, "commits_count")
        assert hasattr(MemberSnapshot, "pull_requests_count")
        assert hasattr(MemberSnapshot, "issues_count")
        assert hasattr(MemberSnapshot, "messages_count")
        assert hasattr(MemberSnapshot, "total_contributions")

    def test_total_contributions_excludes_messages(self):
        """Test that total_contributions only includes GitHub contributions."""
        user = User(login="testuser")
        snapshot = MemberSnapshot(
            github_user=user,
            start_at=datetime(2025, 1, 1, tzinfo=UTC),
            end_at=datetime(2025, 1, 31, tzinfo=UTC),
        )
        snapshot.id = 1

        # The property should only sum commits + PRs + issues (not messages)
        assert "messages_count" not in str(
            MemberSnapshot.total_contributions.fget.__code__.co_names
        )

    def test_m2m_field_configuration(self):
        commits_field = MemberSnapshot._meta.get_field("commits")
        assert commits_field.remote_field.related_name == "member_snapshots"
        assert commits_field.blank is True

        prs_field = MemberSnapshot._meta.get_field("pull_requests")
        assert prs_field.remote_field.related_name == "member_snapshots"
        assert prs_field.blank is True

        issues_field = MemberSnapshot._meta.get_field("issues")
        assert issues_field.remote_field.related_name == "member_snapshots"
        assert issues_field.blank is True

        messages_field = MemberSnapshot._meta.get_field("messages")
        assert messages_field.remote_field.related_name == "member_snapshots"
        assert messages_field.blank is True

    def test_has_communication_heatmap_data_field(self):
        field = MemberSnapshot._meta.get_field("communication_heatmap_data")

        assert field.get_internal_type() == "JSONField"
        assert field.blank is True
        assert callable(field.default)

    def test_has_channel_communications_field(self):
        field = MemberSnapshot._meta.get_field("channel_communications")

        assert field.get_internal_type() == "JSONField"
        assert field.blank is True
        assert callable(field.default)

    def test_has_chapter_contributions_field(self):
        field = MemberSnapshot._meta.get_field("chapter_contributions")

        assert field.get_internal_type() == "JSONField"
        assert field.blank is True
        assert callable(field.default)

    def test_has_project_contributions_field(self):
        field = MemberSnapshot._meta.get_field("project_contributions")

        assert field.get_internal_type() == "JSONField"
        assert field.blank is True
        assert callable(field.default)

    def test_has_repository_contributions_field(self):
        field = MemberSnapshot._meta.get_field("repository_contributions")

        assert field.get_internal_type() == "JSONField"
        assert field.blank is True
        assert callable(field.default)
