from datetime import UTC, datetime
from unittest.mock import MagicMock, PropertyMock, patch

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
        assert field.blank
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

        assert "messages_count" not in str(
            MemberSnapshot.total_contributions.fget.__code__.co_names
        )

    def test_m2m_field_configuration(self):
        commits_field = MemberSnapshot._meta.get_field("commits")
        assert commits_field.remote_field.related_name == "member_snapshots"
        assert commits_field.blank

        prs_field = MemberSnapshot._meta.get_field("pull_requests")
        assert prs_field.remote_field.related_name == "member_snapshots"
        assert prs_field.blank

        issues_field = MemberSnapshot._meta.get_field("issues")
        assert issues_field.remote_field.related_name == "member_snapshots"
        assert issues_field.blank

        messages_field = MemberSnapshot._meta.get_field("messages")
        assert messages_field.remote_field.related_name == "member_snapshots"
        assert messages_field.blank

    def test_has_communication_heatmap_data_field(self):
        field = MemberSnapshot._meta.get_field("communication_heatmap_data")

        assert field.get_internal_type() == "JSONField"
        assert field.blank
        assert callable(field.default)

    def test_has_channel_communications_field(self):
        field = MemberSnapshot._meta.get_field("channel_communications")

        assert field.get_internal_type() == "JSONField"
        assert field.blank
        assert callable(field.default)

    def test_has_chapter_contributions_field(self):
        field = MemberSnapshot._meta.get_field("chapter_contributions")

        assert field.get_internal_type() == "JSONField"
        assert field.blank
        assert callable(field.default)

    def test_has_project_contributions_field(self):
        field = MemberSnapshot._meta.get_field("project_contributions")

        assert field.get_internal_type() == "JSONField"
        assert field.blank
        assert callable(field.default)

    def test_has_repository_contributions_field(self):
        field = MemberSnapshot._meta.get_field("repository_contributions")

        assert field.get_internal_type() == "JSONField"
        assert field.blank
        assert callable(field.default)

    def test_commits_count_property(self):
        """Test commits_count property returns correct count."""
        user = User(login="testuser")
        snapshot = MemberSnapshot(
            github_user=user,
            start_at=datetime(2025, 1, 1, tzinfo=UTC),
            end_at=datetime(2025, 1, 31, tzinfo=UTC),
        )
        snapshot.id = 1

        with patch.object(
            type(snapshot), "commits_count", new_callable=PropertyMock, return_value=10
        ):
            assert snapshot.commits_count == 10

    def test_pull_requests_count_property(self):
        """Test pull_requests_count property returns correct count."""
        user = User(login="testuser")
        snapshot = MemberSnapshot(
            github_user=user,
            start_at=datetime(2025, 1, 1, tzinfo=UTC),
            end_at=datetime(2025, 1, 31, tzinfo=UTC),
        )
        snapshot.id = 1

        with patch.object(
            type(snapshot), "pull_requests_count", new_callable=PropertyMock, return_value=5
        ):
            assert snapshot.pull_requests_count == 5

    def test_issues_count_property(self):
        """Test issues_count property returns correct count."""
        user = User(login="testuser")
        snapshot = MemberSnapshot(
            github_user=user,
            start_at=datetime(2025, 1, 1, tzinfo=UTC),
            end_at=datetime(2025, 1, 31, tzinfo=UTC),
        )
        snapshot.id = 1

        with patch.object(
            type(snapshot), "issues_count", new_callable=PropertyMock, return_value=3
        ):
            assert snapshot.issues_count == 3

    def test_messages_count_property(self):
        """Test messages_count property returns correct count."""
        user = User(login="testuser")
        snapshot = MemberSnapshot(
            github_user=user,
            start_at=datetime(2025, 1, 1, tzinfo=UTC),
            end_at=datetime(2025, 1, 31, tzinfo=UTC),
        )
        snapshot.id = 1

        with patch.object(
            type(snapshot), "messages_count", new_callable=PropertyMock, return_value=20
        ):
            assert snapshot.messages_count == 20

    def test_total_contributions_property(self):
        """Test total_contributions property calculates correctly."""
        user = User(login="testuser")
        snapshot = MemberSnapshot(
            github_user=user,
            start_at=datetime(2025, 1, 1, tzinfo=UTC),
            end_at=datetime(2025, 1, 31, tzinfo=UTC),
        )
        snapshot.id = 1

        with (
            patch.object(
                type(snapshot), "commits_count", new_callable=PropertyMock, return_value=10
            ),
            patch.object(
                type(snapshot), "pull_requests_count", new_callable=PropertyMock, return_value=5
            ),
            patch.object(
                type(snapshot), "issues_count", new_callable=PropertyMock, return_value=3
            ),
        ):
            assert snapshot.total_contributions == 18

    def test_commits_count_executes_m2m_count(self):
        """Test commits_count actually calls self.commits.count()."""
        user = User(login="testuser")
        snapshot = MemberSnapshot(
            github_user=user,
            start_at=datetime(2025, 1, 1, tzinfo=UTC),
            end_at=datetime(2025, 1, 31, tzinfo=UTC),
        )
        snapshot.id = 1

        mock_manager = MagicMock()
        mock_manager.count.return_value = 7
        with patch.object(
            type(snapshot), "commits", new_callable=PropertyMock, return_value=mock_manager
        ):
            result = snapshot.commits_count
        assert result == 7
        mock_manager.count.assert_called_once()

    def test_pull_requests_count_executes_m2m_count(self):
        """Test pull_requests_count actually calls self.pull_requests.count()."""
        user = User(login="testuser")
        snapshot = MemberSnapshot(
            github_user=user,
            start_at=datetime(2025, 1, 1, tzinfo=UTC),
            end_at=datetime(2025, 1, 31, tzinfo=UTC),
        )
        snapshot.id = 1

        mock_manager = MagicMock()
        mock_manager.count.return_value = 4
        with patch.object(
            type(snapshot),
            "pull_requests",
            new_callable=PropertyMock,
            return_value=mock_manager,
        ):
            result = snapshot.pull_requests_count
        assert result == 4
        mock_manager.count.assert_called_once()

    def test_issues_count_executes_m2m_count(self):
        """Test issues_count actually calls self.issues.count()."""
        user = User(login="testuser")
        snapshot = MemberSnapshot(
            github_user=user,
            start_at=datetime(2025, 1, 1, tzinfo=UTC),
            end_at=datetime(2025, 1, 31, tzinfo=UTC),
        )
        snapshot.id = 1

        mock_manager = MagicMock()
        mock_manager.count.return_value = 2
        with patch.object(
            type(snapshot), "issues", new_callable=PropertyMock, return_value=mock_manager
        ):
            result = snapshot.issues_count
        assert result == 2
        mock_manager.count.assert_called_once()

    def test_messages_count_executes_m2m_count(self):
        """Test messages_count actually calls self.messages.count()."""
        user = User(login="testuser")
        snapshot = MemberSnapshot(
            github_user=user,
            start_at=datetime(2025, 1, 1, tzinfo=UTC),
            end_at=datetime(2025, 1, 31, tzinfo=UTC),
        )
        snapshot.id = 1

        mock_manager = MagicMock()
        mock_manager.count.return_value = 15
        with patch.object(
            type(snapshot), "messages", new_callable=PropertyMock, return_value=mock_manager
        ):
            result = snapshot.messages_count
        assert result == 15
        mock_manager.count.assert_called_once()
