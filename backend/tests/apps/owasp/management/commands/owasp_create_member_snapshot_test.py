import io
from datetime import UTC, datetime
from unittest import mock

import pytest

from apps.owasp.management.commands.owasp_create_member_snapshot import Command


class TestOwaspCreateMemberSnapshotCommand:
    @pytest.fixture
    def command(self):
        return Command()

    def test_parse_date_valid(self, command):
        result = command.parse_date("2025-01-15", datetime(2025, 1, 1, tzinfo=UTC))

        assert result == datetime(2025, 1, 15, tzinfo=UTC)

    def test_parse_date_none_returns_default(self, command):
        default = datetime(2025, 2, 1, tzinfo=UTC)
        result = command.parse_date(None, default)

        assert result == default

    def test_parse_date_invalid_format(self, command):
        err = io.StringIO()
        command.stderr = err

        with pytest.raises(ValueError, match=r"time data .* does not match format"):
            command.parse_date("invalid-date", datetime.now(UTC))

        error_output = err.getvalue()
        assert "Invalid date format" in error_output

    def test_generate_heatmap_data(self, command):
        start_at = datetime(2025, 1, 1, tzinfo=UTC)
        end_at = datetime(2025, 10, 1, tzinfo=UTC)

        # Mock contributions with different dates
        mock_commit_1 = mock.Mock()
        mock_commit_1.created_at = datetime(2025, 1, 15, tzinfo=UTC)

        mock_commit_2 = mock.Mock()
        mock_commit_2.created_at = datetime(2025, 1, 15, tzinfo=UTC)

        mock_pr = mock.Mock()
        mock_pr.created_at = datetime(2025, 1, 16, tzinfo=UTC)

        mock_issue = mock.Mock()
        mock_issue.created_at = datetime(2025, 1, 15, tzinfo=UTC)

        # Call the actual method
        result = command.generate_heatmap_data(
            [mock_commit_1, mock_commit_2],
            [mock_pr],
            [mock_issue],
            start_at,
            end_at,
        )

        assert result == {"2025-01-15": 3, "2025-01-16": 1}

    def test_generate_heatmap_data_empty_contributions(self, command):
        start_at = datetime(2025, 1, 1, tzinfo=UTC)
        end_at = datetime(2025, 10, 1, tzinfo=UTC)

        result = command.generate_heatmap_data([], [], [], start_at, end_at)

        assert result == {}

    def test_generate_heatmap_data_single_date(self, command):
        start_at = datetime(2025, 1, 1, tzinfo=UTC)
        end_at = datetime(2025, 10, 1, tzinfo=UTC)

        mock_commit = mock.Mock()
        mock_commit.created_at = datetime(2025, 1, 10, tzinfo=UTC)

        mock_pr = mock.Mock()
        mock_pr.created_at = datetime(2025, 1, 10, tzinfo=UTC)

        mock_issue = mock.Mock()
        mock_issue.created_at = datetime(2025, 1, 10, tzinfo=UTC)

        result = command.generate_heatmap_data(
            [mock_commit], [mock_pr], [mock_issue], start_at, end_at
        )

        assert result == {"2025-01-10": 3}

    def test_generate_heatmap_data_filters_by_date_range(self, command):
        start_at = datetime(2025, 1, 1, tzinfo=UTC)
        end_at = datetime(2025, 10, 1, tzinfo=UTC)

        # Create contributions: one before, two within, one after range
        mock_commit_before = mock.Mock()
        mock_commit_before.created_at = datetime(2024, 12, 31, tzinfo=UTC)

        mock_commit_in_range = mock.Mock()
        mock_commit_in_range.created_at = datetime(2025, 1, 15, tzinfo=UTC)

        mock_pr_after = mock.Mock()
        mock_pr_after.created_at = datetime(2025, 10, 2, tzinfo=UTC)

        mock_issue_in_range = mock.Mock()
        mock_issue_in_range.created_at = datetime(2025, 5, 1, tzinfo=UTC)

        result = command.generate_heatmap_data(
            [mock_commit_before, mock_commit_in_range],
            [mock_pr_after],
            [mock_issue_in_range],
            start_at,
            end_at,
        )

        # Only dates within range should be included
        assert result == {"2025-01-15": 1, "2025-05-01": 1}
        assert "2024-12-31" not in result
        assert "2025-10-02" not in result

    def test_generate_entity_contributions_filters_by_date_range(self, command):
        start_at = datetime(2025, 1, 1, tzinfo=UTC)
        end_at = datetime(2025, 10, 1, tzinfo=UTC)

        # Mock user and entity setup
        mock_user = mock.Mock()
        mock_user.id = 1

        # Mock repository
        mock_repo = mock.Mock()
        mock_repo.id = 100

        # Create contributions: one before, two within, one after range
        mock_commit_before = mock.Mock()
        mock_commit_before.created_at = datetime(2024, 12, 31, tzinfo=UTC)
        mock_commit_before.repository_id = 100

        mock_commit_in_range = mock.Mock()
        mock_commit_in_range.created_at = datetime(2025, 1, 15, tzinfo=UTC)
        mock_commit_in_range.repository_id = 100

        mock_pr_after = mock.Mock()
        mock_pr_after.created_at = datetime(2025, 10, 2, tzinfo=UTC)
        mock_pr_after.repository_id = 100

        mock_issue_in_range = mock.Mock()
        mock_issue_in_range.created_at = datetime(2025, 5, 1, tzinfo=UTC)
        mock_issue_in_range.repository_id = 100

        # Create mock querysets with select_related
        # The method needs both .select_related() to work and direct iteration
        commit_list = [mock_commit_before, mock_commit_in_range]
        pr_list = [mock_pr_after]
        issue_list = [mock_issue_in_range]

        mock_commits = mock.Mock()
        mock_commits.select_related.return_value = iter(commit_list)
        mock_commits.__iter__ = lambda _: iter(commit_list)

        mock_prs = mock.Mock()
        mock_prs.select_related.return_value = iter(pr_list)
        mock_prs.__iter__ = lambda _: iter(pr_list)

        mock_issues = mock.Mock()
        mock_issues.select_related.return_value = iter(issue_list)
        mock_issues.__iter__ = lambda _: iter(issue_list)

        # Mock the database queries
        with (
            mock.patch(
                "apps.owasp.management.commands.owasp_create_member_snapshot.Project"
            ) as mock_project_model,
            mock.patch(
                "apps.owasp.management.commands.owasp_create_member_snapshot.ContentType"
            ) as mock_content_type,
            mock.patch(
                "apps.owasp.management.commands.owasp_create_member_snapshot.EntityMember"
            ) as mock_entity_member,
        ):
            # Setup mocks
            mock_content_type.objects.get_for_model.return_value = mock.Mock(id=1)
            mock_entity_member.objects.filter.return_value.values_list.return_value = [
                1,
                2,
            ]

            mock_project = mock.Mock()
            mock_project.nest_key = "test-project"
            mock_project.repositories.all.return_value = [mock_repo]

            mock_project_model.objects.filter.return_value.prefetch_related.return_value = [
                mock_project
            ]

            result = command.generate_entity_contributions(
                mock_user,
                mock_commits,
                mock_prs,
                mock_issues,
                "project",
                start_at,
                end_at,
            )

            # Only contributions within date range should be counted
            # 1 commit + 1 issue = 2 (PR is after end_at, commit_before is before start_at)
            assert result == {"test-project": 2}

    def test_generate_repository_contributions(self, command):
        start_at = datetime(2025, 1, 1, tzinfo=UTC)
        end_at = datetime(2025, 10, 1, tzinfo=UTC)

        # Mock repository and owner
        mock_owner = mock.Mock()
        mock_owner.login = "owasp"

        mock_repo = mock.Mock()
        mock_repo.name = "nest"
        mock_repo.owner = mock_owner

        # Create commits with dates
        mock_commit_1 = mock.Mock()
        mock_commit_1.created_at = datetime(2025, 1, 15, tzinfo=UTC)
        mock_commit_1.repository = mock_repo

        mock_commit_2 = mock.Mock()
        mock_commit_2.created_at = datetime(2025, 1, 16, tzinfo=UTC)
        mock_commit_2.repository = mock_repo

        mock_commit_3 = mock.Mock()
        mock_commit_3.created_at = datetime(2025, 1, 15, tzinfo=UTC)
        mock_commit_3.repository = mock_repo

        # One commit outside date range (should be excluded)
        mock_commit_out = mock.Mock()
        mock_commit_out.created_at = datetime(2024, 12, 31, tzinfo=UTC)
        mock_commit_out.repository = mock_repo

        result = command.generate_repository_contributions(
            [mock_commit_1, mock_commit_2, mock_commit_3, mock_commit_out],
            start_at,
            end_at,
        )

        assert result == {"owasp/nest": 3}

    def test_generate_repository_contributions_top_5(self, command):
        start_at = datetime(2025, 1, 1, tzinfo=UTC)
        end_at = datetime(2025, 10, 1, tzinfo=UTC)

        # Create 6 repos with different commit counts
        commits = []
        for i in range(1, 7):
            for _ in range(i):
                mock_owner = mock.Mock()
                mock_owner.login = "owasp"
                mock_repo = mock.Mock()
                mock_repo.name = f"repo{i}"
                mock_repo.owner = mock_owner

                mock_commit = mock.Mock()
                mock_commit.created_at = datetime(2025, 1, 15, tzinfo=UTC)
                mock_commit.repository = mock_repo
                commits.append(mock_commit)

        result = command.generate_repository_contributions(commits, start_at, end_at)

        # Should only return top 5
        assert len(result) == 5
        # Verify the counts are in descending order
        counts = list(result.values())
        assert counts == sorted(counts, reverse=True)

    def test_generate_communication_heatmap_data(self, command):
        start_at = datetime(2025, 1, 1, tzinfo=UTC)
        end_at = datetime(2025, 10, 1, tzinfo=UTC)

        # Mock public channel conversation
        mock_conversation = mock.Mock()
        mock_conversation.is_channel = True
        mock_conversation.is_private = False

        # Create messages
        mock_msg_1 = mock.Mock()
        mock_msg_1.created_at = datetime(2025, 1, 15, tzinfo=UTC)
        mock_msg_1.conversation = mock_conversation

        mock_msg_2 = mock.Mock()
        mock_msg_2.created_at = datetime(2025, 1, 15, tzinfo=UTC)
        mock_msg_2.conversation = mock_conversation

        mock_msg_3 = mock.Mock()
        mock_msg_3.created_at = datetime(2025, 1, 16, tzinfo=UTC)
        mock_msg_3.conversation = mock_conversation

        result = command.generate_communication_heatmap_data(
            [mock_msg_1, mock_msg_2, mock_msg_3],
            start_at,
            end_at,
        )

        assert result == {"2025-01-15": 2, "2025-01-16": 1}

    def test_generate_communication_heatmap_data_filters_private(self, command):
        start_at = datetime(2025, 1, 1, tzinfo=UTC)
        end_at = datetime(2025, 10, 1, tzinfo=UTC)

        # Mock private channel
        mock_private_conversation = mock.Mock()
        mock_private_conversation.is_channel = True
        mock_private_conversation.is_private = True

        # Mock public channel
        mock_public_conversation = mock.Mock()
        mock_public_conversation.is_channel = True
        mock_public_conversation.is_private = False

        # Create messages
        mock_msg_private = mock.Mock()
        mock_msg_private.created_at = datetime(2025, 1, 15, tzinfo=UTC)
        mock_msg_private.conversation = mock_private_conversation

        mock_msg_public = mock.Mock()
        mock_msg_public.created_at = datetime(2025, 1, 15, tzinfo=UTC)
        mock_msg_public.conversation = mock_public_conversation

        result = command.generate_communication_heatmap_data(
            [mock_msg_private, mock_msg_public],
            start_at,
            end_at,
        )

        # Only public channel message should be counted
        assert result == {"2025-01-15": 1}

    def test_generate_channel_communications(self, command):
        start_at = datetime(2025, 1, 1, tzinfo=UTC)
        end_at = datetime(2025, 10, 1, tzinfo=UTC)

        # Mock public channel
        mock_conversation = mock.Mock()
        mock_conversation.is_channel = True
        mock_conversation.is_private = False
        mock_conversation.name = "general"

        # Create messages
        mock_msg_1 = mock.Mock()
        mock_msg_1.created_at = datetime(2025, 1, 15, tzinfo=UTC)
        mock_msg_1.conversation = mock_conversation

        mock_msg_2 = mock.Mock()
        mock_msg_2.created_at = datetime(2025, 1, 16, tzinfo=UTC)
        mock_msg_2.conversation = mock_conversation

        result = command.generate_channel_communications(
            [mock_msg_1, mock_msg_2],
            start_at,
            end_at,
        )

        assert result == {"general": 2}

    def test_generate_channel_communications_top_5(self, command):
        start_at = datetime(2025, 1, 1, tzinfo=UTC)
        end_at = datetime(2025, 10, 1, tzinfo=UTC)

        # Create 6 channels with different message counts
        messages = []
        for i in range(1, 7):
            mock_conversation = mock.Mock()
            mock_conversation.is_channel = True
            mock_conversation.is_private = False
            mock_conversation.name = f"channel{i}"

            for _ in range(i):
                mock_msg = mock.Mock()
                mock_msg.created_at = datetime(2025, 1, 15, tzinfo=UTC)
                mock_msg.conversation = mock_conversation
                messages.append(mock_msg)

        result = command.generate_channel_communications(messages, start_at, end_at)

        # Should only return top 5
        assert len(result) == 5
        # Verify the counts are in descending order
        counts = list(result.values())
        assert counts == sorted(counts, reverse=True)

    def test_generate_communication_heatmap_data_filters_out_of_range(self, command):
        start_at = datetime(2025, 1, 1, tzinfo=UTC)
        end_at = datetime(2025, 10, 1, tzinfo=UTC)

        # Mock public channel
        mock_conversation = mock.Mock()
        mock_conversation.is_channel = True
        mock_conversation.is_private = False

        # Create messages outside range
        mock_msg_before = mock.Mock()
        mock_msg_before.created_at = datetime(2024, 12, 31, tzinfo=UTC)
        mock_msg_before.conversation = mock_conversation

        mock_msg_after = mock.Mock()
        mock_msg_after.created_at = datetime(2025, 10, 2, tzinfo=UTC)
        mock_msg_after.conversation = mock_conversation

        # Create message in range
        mock_msg_in_range = mock.Mock()
        mock_msg_in_range.created_at = datetime(2025, 1, 15, tzinfo=UTC)
        mock_msg_in_range.conversation = mock_conversation

        result = command.generate_communication_heatmap_data(
            [mock_msg_before, mock_msg_after, mock_msg_in_range],
            start_at,
            end_at,
        )

        # Only message in range should be counted
        assert result == {"2025-01-15": 1}
        assert "2024-12-31" not in result
        assert "2025-10-02" not in result

    def test_generate_channel_communications_filters_out_of_range(self, command):
        start_at = datetime(2025, 1, 1, tzinfo=UTC)
        end_at = datetime(2025, 10, 1, tzinfo=UTC)

        # Mock public channel
        mock_conversation = mock.Mock()
        mock_conversation.is_channel = True
        mock_conversation.is_private = False
        mock_conversation.name = "general"

        # Create messages outside range
        mock_msg_before = mock.Mock()
        mock_msg_before.created_at = datetime(2024, 12, 31, tzinfo=UTC)
        mock_msg_before.conversation = mock_conversation

        mock_msg_after = mock.Mock()
        mock_msg_after.created_at = datetime(2025, 10, 2, tzinfo=UTC)
        mock_msg_after.conversation = mock_conversation

        # Create message in range
        mock_msg_in_range = mock.Mock()
        mock_msg_in_range.created_at = datetime(2025, 1, 15, tzinfo=UTC)
        mock_msg_in_range.conversation = mock_conversation

        result = command.generate_channel_communications(
            [mock_msg_before, mock_msg_after, mock_msg_in_range],
            start_at,
            end_at,
        )

        # Only message in range should be counted
        assert result == {"general": 1}

    def test_generate_channel_communications_ignores_messages_without_channel_name(self, command):
        start_at = datetime(2025, 1, 1, tzinfo=UTC)
        end_at = datetime(2025, 10, 1, tzinfo=UTC)

        # Mock public channel without name
        mock_conversation = mock.Mock()
        mock_conversation.is_channel = True
        mock_conversation.is_private = False
        mock_conversation.name = ""

        # Create message
        mock_msg = mock.Mock()
        mock_msg.created_at = datetime(2025, 1, 15, tzinfo=UTC)
        mock_msg.conversation = mock_conversation

        result = command.generate_channel_communications([mock_msg], start_at, end_at)

        # Should not include channels without names
        assert result == {}

    def test_generate_repository_contributions_empty_commits(self, command):
        start_at = datetime(2025, 1, 1, tzinfo=UTC)
        end_at = datetime(2025, 10, 1, tzinfo=UTC)

        result = command.generate_repository_contributions([], start_at, end_at)

        assert result == {}
