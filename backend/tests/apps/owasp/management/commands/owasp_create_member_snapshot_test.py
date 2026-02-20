import io
from argparse import ArgumentParser
from datetime import UTC, datetime
from unittest import mock

import pytest

from apps.owasp.management.commands.owasp_create_member_snapshot import Command


class TestOwaspCreateMemberSnapshotCommand:
    @pytest.fixture
    def command(self):
        return Command()

    def test_add_arguments(self, command):
        """Test add_arguments adds expected arguments."""
        parser = ArgumentParser()
        command.add_arguments(parser)
        args = parser.parse_args(["testuser"])
        assert args.username == "testuser"
        assert args.start_at is None
        assert args.end_at is None

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

        # All dates should be initialized
        assert "2025-01-15" in result
        assert result["2025-01-15"] == 3
        assert "2025-01-16" in result
        assert result["2025-01-16"] == 1
        # Check a date without contributions is 0
        assert result["2025-01-01"] == 0

    def test_generate_heatmap_data_empty_contributions(self, command):
        start_at = datetime(2025, 1, 1, tzinfo=UTC)
        end_at = datetime(2025, 1, 3, tzinfo=UTC)

        result = command.generate_heatmap_data([], [], [], start_at, end_at)

        # All dates should be initialized to 0
        assert result == {"2025-01-01": 0, "2025-01-02": 0, "2025-01-03": 0}

    def test_generate_heatmap_data_single_date(self, command):
        start_at = datetime(2025, 1, 1, tzinfo=UTC)
        end_at = datetime(2025, 1, 10, tzinfo=UTC)

        mock_commit = mock.Mock()
        mock_commit.created_at = datetime(2025, 1, 10, tzinfo=UTC)

        mock_pr = mock.Mock()
        mock_pr.created_at = datetime(2025, 1, 10, tzinfo=UTC)

        mock_issue = mock.Mock()
        mock_issue.created_at = datetime(2025, 1, 10, tzinfo=UTC)

        result = command.generate_heatmap_data(
            [mock_commit], [mock_pr], [mock_issue], start_at, end_at
        )

        # Should have all dates in range
        assert result["2025-01-10"] == 3
        assert result["2025-01-01"] == 0
        assert len(result) == 10  # 10 days from Jan 1 to Jan 10

    def test_generate_heatmap_data_filters_by_date_range(self, command):
        start_at = datetime(2025, 1, 1, tzinfo=UTC)
        end_at = datetime(2025, 1, 5, tzinfo=UTC)

        # Create contributions: one before, one within, one after range
        mock_commit_before = mock.Mock()
        mock_commit_before.created_at = datetime(2024, 12, 31, tzinfo=UTC)

        mock_commit_in_range = mock.Mock()
        mock_commit_in_range.created_at = datetime(2025, 1, 3, tzinfo=UTC)

        mock_pr_after = mock.Mock()
        mock_pr_after.created_at = datetime(2025, 1, 10, tzinfo=UTC)

        result = command.generate_heatmap_data(
            [mock_commit_before, mock_commit_in_range],
            [mock_pr_after],
            [],
            start_at,
            end_at,
        )

        # Should have all dates in range initialized
        assert result["2025-01-03"] == 1
        assert result["2025-01-01"] == 0
        assert result["2025-01-02"] == 0
        # Dates outside range should not be included
        assert "2024-12-31" not in result
        assert "2025-01-10" not in result

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

            # Mock the first filter call (for initializing all led entities)
            # and the second call (for building repo_to_entity mapping)
            mock_filter = mock.Mock()
            mock_filter.prefetch_related.return_value = [mock_project]
            # Make the filter mock iterable for the initialization loop
            mock_filter.__iter__ = lambda _: iter([mock_project])
            mock_project_model.objects.filter.return_value = mock_filter

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
        end_at = datetime(2025, 1, 16, tzinfo=UTC)

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

        # Should have all dates initialized
        assert result["2025-01-15"] == 2
        assert result["2025-01-16"] == 1
        assert result["2025-01-01"] == 0

    def test_generate_communication_heatmap_data_filters_private(self, command):
        start_at = datetime(2025, 1, 1, tzinfo=UTC)
        end_at = datetime(2025, 1, 15, tzinfo=UTC)

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

        # Only public channel message should be counted, but all dates initialized
        assert result["2025-01-15"] == 1
        assert result["2025-01-01"] == 0

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
        end_at = datetime(2025, 1, 15, tzinfo=UTC)

        # Mock public channel
        mock_conversation = mock.Mock()
        mock_conversation.is_channel = True
        mock_conversation.is_private = False

        # Create messages outside range
        mock_msg_before = mock.Mock()
        mock_msg_before.created_at = datetime(2024, 12, 31, tzinfo=UTC)
        mock_msg_before.conversation = mock_conversation

        mock_msg_after = mock.Mock()
        mock_msg_after.created_at = datetime(2025, 1, 20, tzinfo=UTC)
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

        # Only message in range should be counted, all dates initialized
        assert result["2025-01-15"] == 1
        assert result["2025-01-01"] == 0
        # Dates outside range should not be included
        assert "2024-12-31" not in result
        assert "2025-01-20" not in result

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

    def test_generate_heatmap_data_empty_issues(self, command):
        """Test generate_heatmap_data with issue outside date range."""
        start_at = datetime(2025, 1, 1, tzinfo=UTC)
        end_at = datetime(2025, 1, 3, tzinfo=UTC)

        mock_commit = mock.Mock()
        mock_commit.created_at = datetime(2025, 1, 1, tzinfo=UTC)

        mock_issue_out_of_range = mock.Mock()
        mock_issue_out_of_range.created_at = datetime(2025, 2, 1, tzinfo=UTC)

        result = command.generate_heatmap_data(
            [mock_commit], [], [mock_issue_out_of_range], start_at, end_at
        )

        assert result["2025-01-01"] == 1
        assert result["2025-01-02"] == 0

    def test_generate_entity_contributions_unmatched_repos(self, command):
        """Test entity_contributions where contributions' repos don't match led entities."""
        start_at = datetime(2025, 1, 1, tzinfo=UTC)
        end_at = datetime(2025, 10, 1, tzinfo=UTC)

        mock_user = mock.Mock()
        mock_user.id = 1

        mock_commit = mock.Mock()
        mock_commit.created_at = datetime(2025, 3, 1, tzinfo=UTC)
        mock_commit.repository_id = 999

        mock_pr = mock.Mock()
        mock_pr.created_at = datetime(2025, 3, 1, tzinfo=UTC)
        mock_pr.repository_id = 999

        mock_issue = mock.Mock()
        mock_issue.created_at = datetime(2025, 3, 1, tzinfo=UTC)
        mock_issue.repository_id = 999

        mock_commits = mock.Mock()
        mock_commits.select_related.return_value = [mock_commit]
        mock_commits.__iter__ = lambda _: iter([mock_commit])

        mock_prs = mock.Mock()
        mock_prs.select_related.return_value = [mock_pr]
        mock_prs.__iter__ = lambda _: iter([mock_pr])

        mock_issues = mock.Mock()
        mock_issues.select_related.return_value = [mock_issue]
        mock_issues.__iter__ = lambda _: iter([mock_issue])

        with (
            mock.patch(
                "apps.owasp.management.commands.owasp_create_member_snapshot.Chapter"
            ) as mock_chapter_model,
            mock.patch(
                "apps.owasp.management.commands.owasp_create_member_snapshot.ContentType"
            ) as mock_content_type,
            mock.patch(
                "apps.owasp.management.commands.owasp_create_member_snapshot.EntityMember"
            ) as mock_entity_member,
        ):
            mock_content_type.objects.get_for_model.return_value = mock.Mock(id=1)
            mock_entity_member.objects.filter.return_value.values_list.return_value = [1]

            mock_chapter = mock.Mock()
            mock_chapter.nest_key = "test-chapter"
            mock_chapter.owasp_repository_id = 100

            mock_filter = mock.Mock()
            mock_filter.select_related.return_value = [mock_chapter]
            mock_filter.__iter__ = lambda _: iter([mock_chapter])
            mock_chapter_model.objects.filter.return_value = mock_filter

            result = command.generate_entity_contributions(
                mock_user, mock_commits, mock_prs, mock_issues, "chapter", start_at, end_at
            )

        assert result == {"test-chapter": 0}


class TestHandleMethod:
    """Tests for the handle() method of owasp_create_member_snapshot command."""

    target_module = "apps.owasp.management.commands.owasp_create_member_snapshot"

    @pytest.fixture
    def command(self):
        cmd = Command()
        cmd.stdout = mock.MagicMock()
        cmd.stderr = mock.MagicMock()
        cmd.style = mock.MagicMock()
        cmd.style.ERROR = lambda x: x
        cmd.style.WARNING = lambda x: x
        cmd.style.SUCCESS = lambda x: x
        return cmd

    def test_handle_user_not_found(self, command, mocker):
        """Test handle when user is not found."""
        mock_user = mocker.patch(f"{self.target_module}.User")
        mock_user.DoesNotExist = Exception
        mock_user.objects.get.side_effect = mock_user.DoesNotExist

        command.handle(username="nonexistent", start_at=None, end_at=None)

        command.stderr.write.assert_called()

    def test_handle_creates_new_snapshot(self, command, mocker):
        """Test handle creates a new snapshot when none exists."""
        mock_user = mocker.patch(f"{self.target_module}.User")
        mock_user_instance = mock.MagicMock()
        mock_user.objects.get.return_value = mock_user_instance

        mock_snapshot_model = mocker.patch(f"{self.target_module}.MemberSnapshot")
        mock_snapshot_model.objects.filter.return_value.first.return_value = None

        mock_snapshot = mock.MagicMock()
        mock_snapshot.id = 1
        mock_snapshot.total_contributions = 0
        mock_snapshot.commits_count = 0
        mock_snapshot.pull_requests_count = 0
        mock_snapshot.issues_count = 0
        mock_snapshot.messages_count = 0
        mock_snapshot_model.objects.create.return_value = mock_snapshot

        mock_commit = mocker.patch(f"{self.target_module}.Commit")
        mock_commit.objects.filter.return_value.count.return_value = 0

        mock_pr = mocker.patch(f"{self.target_module}.PullRequest")
        mock_pr.objects.filter.return_value.count.return_value = 0

        mock_issue = mocker.patch(f"{self.target_module}.Issue")
        mock_issue.objects.filter.return_value.count.return_value = 0

        mock_profile = mocker.patch(f"{self.target_module}.MemberProfile")
        mock_profile.DoesNotExist = Exception
        mock_profile.objects.get.side_effect = mock_profile.DoesNotExist

        mocker.patch.object(command, "generate_heatmap_data", return_value={})
        mocker.patch.object(command, "generate_entity_contributions", return_value={})
        mocker.patch.object(command, "generate_repository_contributions", return_value={})
        mocker.patch.object(command, "generate_communication_heatmap_data", return_value={})

        command.handle(username="testuser", start_at=None, end_at=None)

        mock_snapshot_model.objects.create.assert_called_once()

    def test_handle_updates_existing_snapshot(self, command, mocker):
        """Test handle updates an existing snapshot."""
        mock_user = mocker.patch(f"{self.target_module}.User")
        mock_user_instance = mock.MagicMock()
        mock_user.objects.get.return_value = mock_user_instance

        mock_snapshot_model = mocker.patch(f"{self.target_module}.MemberSnapshot")
        mock_existing_snapshot = mock.MagicMock()
        mock_existing_snapshot.id = 99
        mock_existing_snapshot.total_contributions = 0
        mock_existing_snapshot.commits_count = 0
        mock_existing_snapshot.pull_requests_count = 0
        mock_existing_snapshot.issues_count = 0
        mock_existing_snapshot.messages_count = 0
        mock_snapshot_model.objects.filter.return_value.first.return_value = mock_existing_snapshot

        mock_commit = mocker.patch(f"{self.target_module}.Commit")
        mock_commit.objects.filter.return_value.count.return_value = 0

        mock_pr = mocker.patch(f"{self.target_module}.PullRequest")
        mock_pr.objects.filter.return_value.count.return_value = 0

        mock_issue = mocker.patch(f"{self.target_module}.Issue")
        mock_issue.objects.filter.return_value.count.return_value = 0

        mock_profile = mocker.patch(f"{self.target_module}.MemberProfile")
        mock_profile.DoesNotExist = Exception
        mock_profile.objects.get.side_effect = mock_profile.DoesNotExist

        mocker.patch.object(command, "generate_heatmap_data", return_value={})
        mocker.patch.object(command, "generate_entity_contributions", return_value={})
        mocker.patch.object(command, "generate_repository_contributions", return_value={})
        mocker.patch.object(command, "generate_communication_heatmap_data", return_value={})

        command.handle(username="testuser", start_at=None, end_at=None)

        mock_existing_snapshot.commits.clear.assert_called_once()
        mock_existing_snapshot.pull_requests.clear.assert_called_once()
        mock_existing_snapshot.issues.clear.assert_called_once()
        mock_existing_snapshot.messages.clear.assert_called_once()

    def test_handle_with_contributions(self, command, mocker):
        """Test handle with actual contributions linked."""
        mock_user = mocker.patch(f"{self.target_module}.User")
        mock_user_instance = mock.MagicMock()
        mock_user.objects.get.return_value = mock_user_instance

        mock_snapshot_model = mocker.patch(f"{self.target_module}.MemberSnapshot")
        mock_snapshot_model.objects.filter.return_value.first.return_value = None

        mock_snapshot = mock.MagicMock()
        mock_snapshot.id = 1
        mock_snapshot.total_contributions = 10
        mock_snapshot.commits_count = 5
        mock_snapshot.pull_requests_count = 3
        mock_snapshot.issues_count = 2
        mock_snapshot.messages_count = 0
        mock_snapshot_model.objects.create.return_value = mock_snapshot

        mock_commit = mocker.patch(f"{self.target_module}.Commit")
        mock_commit_qs = mock.MagicMock()
        mock_commit_qs.count.return_value = 5
        mock_commit_qs.__iter__ = lambda _: iter([])
        mock_commit.objects.filter.return_value = mock_commit_qs

        mock_pr = mocker.patch(f"{self.target_module}.PullRequest")
        mock_pr_qs = mock.MagicMock()
        mock_pr_qs.count.return_value = 3
        mock_pr_qs.__iter__ = lambda _: iter([])
        mock_pr.objects.filter.return_value = mock_pr_qs

        mock_issue = mocker.patch(f"{self.target_module}.Issue")
        mock_issue_qs = mock.MagicMock()
        mock_issue_qs.count.return_value = 2
        mock_issue_qs.__iter__ = lambda _: iter([])
        mock_issue.objects.filter.return_value = mock_issue_qs

        mock_profile = mocker.patch(f"{self.target_module}.MemberProfile")
        mock_profile.DoesNotExist = Exception
        mock_profile.objects.get.side_effect = mock_profile.DoesNotExist

        mocker.patch.object(command, "generate_heatmap_data", return_value={"2025-01-01": 1})
        mocker.patch.object(command, "generate_entity_contributions", return_value={"project": 1})
        mocker.patch.object(command, "generate_repository_contributions", return_value={"repo": 1})
        mocker.patch.object(command, "generate_communication_heatmap_data", return_value={})

        command.handle(username="testuser", start_at=None, end_at=None)

        mock_snapshot.commits.add.assert_called()
        mock_snapshot.pull_requests.add.assert_called()
        mock_snapshot.issues.add.assert_called()

    def test_handle_with_member_profile_no_slack_id(self, command, mocker):
        """Test handle when user has profile but no Slack ID."""
        mock_user = mocker.patch(f"{self.target_module}.User")
        mock_user_instance = mock.MagicMock()
        mock_user.objects.get.return_value = mock_user_instance

        mock_snapshot_model = mocker.patch(f"{self.target_module}.MemberSnapshot")
        mock_snapshot_model.objects.filter.return_value.first.return_value = None

        mock_snapshot = mock.MagicMock()
        mock_snapshot.id = 1
        mock_snapshot.total_contributions = 0
        mock_snapshot.commits_count = 0
        mock_snapshot.pull_requests_count = 0
        mock_snapshot.issues_count = 0
        mock_snapshot.messages_count = 0
        mock_snapshot_model.objects.create.return_value = mock_snapshot

        mock_commit = mocker.patch(f"{self.target_module}.Commit")
        mock_commit.objects.filter.return_value.count.return_value = 0

        mock_pr = mocker.patch(f"{self.target_module}.PullRequest")
        mock_pr.objects.filter.return_value.count.return_value = 0

        mock_issue = mocker.patch(f"{self.target_module}.Issue")
        mock_issue.objects.filter.return_value.count.return_value = 0

        mock_profile = mocker.patch(f"{self.target_module}.MemberProfile")
        mock_profile_instance = mock.MagicMock()
        mock_profile_instance.owasp_slack_id = None
        mock_profile.objects.get.return_value = mock_profile_instance

        mocker.patch.object(command, "generate_heatmap_data", return_value={})
        mocker.patch.object(command, "generate_entity_contributions", return_value={})
        mocker.patch.object(command, "generate_repository_contributions", return_value={})
        mocker.patch.object(command, "generate_communication_heatmap_data", return_value={})

        command.handle(username="testuser", start_at=None, end_at=None)

        stdout_calls = [str(call) for call in command.stdout.write.call_args_list]
        assert any("No Slack ID" in str(call) for call in stdout_calls)

    def test_handle_with_slack_messages(self, command, mocker):
        """Test handle when user has Slack messages."""
        mock_user = mocker.patch(f"{self.target_module}.User")
        mock_user_instance = mock.MagicMock()
        mock_user.objects.get.return_value = mock_user_instance

        mock_snapshot_model = mocker.patch(f"{self.target_module}.MemberSnapshot")
        mock_snapshot_model.objects.filter.return_value.first.return_value = None

        mock_snapshot = mock.MagicMock()
        mock_snapshot.id = 1
        mock_snapshot.total_contributions = 5
        mock_snapshot.commits_count = 5
        mock_snapshot.pull_requests_count = 0
        mock_snapshot.issues_count = 0
        mock_snapshot.messages_count = 10
        mock_snapshot_model.objects.create.return_value = mock_snapshot

        mock_commit = mocker.patch(f"{self.target_module}.Commit")
        mock_commit_qs = mock.MagicMock()
        mock_commit_qs.count.return_value = 5
        mock_commit_qs.__iter__ = lambda _: iter([])
        mock_commit.objects.filter.return_value = mock_commit_qs

        mock_pr = mocker.patch(f"{self.target_module}.PullRequest")
        mock_pr.objects.filter.return_value.count.return_value = 0

        mock_issue = mocker.patch(f"{self.target_module}.Issue")
        mock_issue.objects.filter.return_value.count.return_value = 0

        mock_profile = mocker.patch(f"{self.target_module}.MemberProfile")
        mock_profile_instance = mock.MagicMock()
        mock_profile_instance.owasp_slack_id = "U12345"
        mock_profile.objects.get.return_value = mock_profile_instance

        mock_message = mocker.patch(f"{self.target_module}.Message")
        mock_msg_qs = mock.MagicMock()
        mock_msg_qs.select_related.return_value = mock_msg_qs
        mock_msg_qs.count.return_value = 10
        mock_msg_qs.__iter__ = lambda _: iter([])
        mock_message.objects.filter.return_value = mock_msg_qs
        mock_message.objects.none.return_value = mock_msg_qs

        mocker.patch.object(command, "generate_heatmap_data", return_value={"2025-01-01": 1})
        mocker.patch.object(command, "generate_entity_contributions", return_value={})
        mocker.patch.object(command, "generate_repository_contributions", return_value={})
        mocker.patch.object(
            command, "generate_communication_heatmap_data", return_value={"2025-01-01": 5}
        )
        mocker.patch.object(
            command, "generate_channel_communications", return_value={"general": 5}
        )

        command.handle(username="testuser", start_at=None, end_at=None)
        mock_snapshot.messages.add.assert_called()

    def test_handle_with_custom_dates(self, command, mocker):
        """Test handle with custom start and end dates."""
        mock_user = mocker.patch(f"{self.target_module}.User")
        mock_user_instance = mock.MagicMock()
        mock_user.objects.get.return_value = mock_user_instance

        mock_snapshot_model = mocker.patch(f"{self.target_module}.MemberSnapshot")
        mock_snapshot_model.objects.filter.return_value.first.return_value = None

        mock_snapshot = mock.MagicMock()
        mock_snapshot.id = 1
        mock_snapshot.total_contributions = 0
        mock_snapshot.commits_count = 0
        mock_snapshot.pull_requests_count = 0
        mock_snapshot.issues_count = 0
        mock_snapshot.messages_count = 0
        mock_snapshot_model.objects.create.return_value = mock_snapshot

        mock_commit = mocker.patch(f"{self.target_module}.Commit")
        mock_commit.objects.filter.return_value.count.return_value = 0

        mock_pr = mocker.patch(f"{self.target_module}.PullRequest")
        mock_pr.objects.filter.return_value.count.return_value = 0

        mock_issue = mocker.patch(f"{self.target_module}.Issue")
        mock_issue.objects.filter.return_value.count.return_value = 0

        mock_profile = mocker.patch(f"{self.target_module}.MemberProfile")
        mock_profile.DoesNotExist = Exception
        mock_profile.objects.get.side_effect = mock_profile.DoesNotExist

        mocker.patch.object(command, "generate_heatmap_data", return_value={})
        mocker.patch.object(command, "generate_entity_contributions", return_value={})
        mocker.patch.object(command, "generate_repository_contributions", return_value={})
        mocker.patch.object(command, "generate_communication_heatmap_data", return_value={})

        command.handle(username="testuser", start_at="2024-06-01", end_at="2024-12-31")
        mock_snapshot_model.objects.create.assert_called_once()

    def test_handle_no_contributions_warning(self, command, mocker):
        """Test handle shows warning when no contributions found."""
        mock_user = mocker.patch(f"{self.target_module}.User")
        mock_user_instance = mock.MagicMock()
        mock_user.objects.get.return_value = mock_user_instance

        mock_snapshot_model = mocker.patch(f"{self.target_module}.MemberSnapshot")
        mock_snapshot_model.objects.filter.return_value.first.return_value = None

        mock_snapshot = mock.MagicMock()
        mock_snapshot.id = 1
        mock_snapshot.total_contributions = 0
        mock_snapshot.commits_count = 0
        mock_snapshot.pull_requests_count = 0
        mock_snapshot.issues_count = 0
        mock_snapshot.messages_count = 0
        mock_snapshot_model.objects.create.return_value = mock_snapshot

        mock_commit = mocker.patch(f"{self.target_module}.Commit")
        mock_commit.objects.filter.return_value.count.return_value = 0

        mock_pr = mocker.patch(f"{self.target_module}.PullRequest")
        mock_pr.objects.filter.return_value.count.return_value = 0

        mock_issue = mocker.patch(f"{self.target_module}.Issue")
        mock_issue.objects.filter.return_value.count.return_value = 0

        mock_profile = mocker.patch(f"{self.target_module}.MemberProfile")
        mock_profile.DoesNotExist = Exception
        mock_profile.objects.get.side_effect = mock_profile.DoesNotExist

        mocker.patch.object(command, "generate_heatmap_data", return_value={})
        mocker.patch.object(command, "generate_entity_contributions", return_value={})
        mocker.patch.object(command, "generate_repository_contributions", return_value={})
        mocker.patch.object(command, "generate_communication_heatmap_data", return_value={})

        command.handle(username="testuser", start_at=None, end_at=None)
        stdout_calls = [str(call) for call in command.stdout.write.call_args_list]
        assert any("no contributions" in str(call).lower() for call in stdout_calls)

    def test_handle_with_slack_zero_messages(self, command, mocker):
        """Test handle with valid Slack ID but zero messages."""
        mock_user = mocker.patch(f"{self.target_module}.User")
        mock_user_instance = mock.MagicMock()
        mock_user.objects.get.return_value = mock_user_instance

        mock_snapshot_model = mocker.patch(f"{self.target_module}.MemberSnapshot")
        mock_snapshot_model.objects.filter.return_value.first.return_value = None

        mock_snapshot = mock.MagicMock()
        mock_snapshot.id = 1
        mock_snapshot.total_contributions = 0
        mock_snapshot.commits_count = 0
        mock_snapshot.pull_requests_count = 0
        mock_snapshot.issues_count = 0
        mock_snapshot.messages_count = 0
        mock_snapshot_model.objects.create.return_value = mock_snapshot

        mock_commit = mocker.patch(f"{self.target_module}.Commit")
        mock_commit.objects.filter.return_value.count.return_value = 0

        mock_pr = mocker.patch(f"{self.target_module}.PullRequest")
        mock_pr.objects.filter.return_value.count.return_value = 0

        mock_issue = mocker.patch(f"{self.target_module}.Issue")
        mock_issue.objects.filter.return_value.count.return_value = 0

        mock_profile = mocker.patch(f"{self.target_module}.MemberProfile")
        mock_profile_instance = mock.MagicMock()
        mock_profile_instance.owasp_slack_id = "U12345"
        mock_profile.objects.get.return_value = mock_profile_instance

        mock_message = mocker.patch(f"{self.target_module}.Message")
        mock_msg_qs = mock.MagicMock()
        mock_msg_qs.select_related.return_value = mock_msg_qs
        mock_msg_qs.count.return_value = 0
        mock_message.objects.filter.return_value = mock_msg_qs
        mock_message.objects.none.return_value = mock_msg_qs

        mocker.patch.object(command, "generate_heatmap_data", return_value={})
        mocker.patch.object(command, "generate_entity_contributions", return_value={})
        mocker.patch.object(command, "generate_repository_contributions", return_value={})
        mocker.patch.object(command, "generate_communication_heatmap_data", return_value={})

        command.handle(username="testuser", start_at=None, end_at=None)

        mock_snapshot.messages.add.assert_not_called()


class TestGenerateEntityContributionsChapter:
    """Tests for chapter entity contributions."""

    def test_generate_entity_contributions_chapter(self):
        """Test chapter entity contributions."""
        command = Command()
        start_at = datetime(2025, 1, 1, tzinfo=UTC)
        end_at = datetime(2025, 10, 1, tzinfo=UTC)

        mock_user = mock.Mock()
        mock_user.id = 1

        mock_repo = mock.Mock()
        mock_repo.id = 100

        mock_commit = mock.Mock()
        mock_commit.created_at = datetime(2025, 1, 15, tzinfo=UTC)
        mock_commit.repository_id = 100

        mock_pr = mock.Mock()
        mock_pr.created_at = datetime(2025, 2, 1, tzinfo=UTC)
        mock_pr.repository_id = 100

        mock_issue = mock.Mock()
        mock_issue.created_at = datetime(2025, 3, 1, tzinfo=UTC)
        mock_issue.repository_id = 100

        commit_list = [mock_commit]
        pr_list = [mock_pr]
        issue_list = [mock_issue]

        mock_commits = mock.Mock()
        mock_commits.select_related.return_value = iter(commit_list)
        mock_commits.__iter__ = lambda _: iter(commit_list)

        mock_prs = mock.Mock()
        mock_prs.select_related.return_value = iter(pr_list)
        mock_prs.__iter__ = lambda _: iter(pr_list)

        mock_issues = mock.Mock()
        mock_issues.select_related.return_value = iter(issue_list)
        mock_issues.__iter__ = lambda _: iter(issue_list)

        target_module = "apps.owasp.management.commands.owasp_create_member_snapshot"

        with (
            mock.patch(f"{target_module}.Chapter") as mock_chapter_model,
            mock.patch(f"{target_module}.ContentType") as mock_content_type,
            mock.patch(f"{target_module}.EntityMember") as mock_entity_member,
        ):
            mock_content_type.objects.get_for_model.return_value = mock.Mock(id=2)
            mock_entity_member.objects.filter.return_value.values_list.return_value = [1]

            mock_chapter = mock.Mock()
            mock_chapter.nest_key = "test-chapter"
            mock_chapter.owasp_repository_id = 100

            mock_filter = mock.Mock()
            mock_filter.select_related.return_value = [mock_chapter]
            mock_filter.__iter__ = lambda _: iter([mock_chapter])
            mock_chapter_model.objects.filter.return_value = mock_filter

            result = command.generate_entity_contributions(
                mock_user,
                mock_commits,
                mock_prs,
                mock_issues,
                "chapter",
                start_at,
                end_at,
            )

            assert result == {"test-chapter": 3}

    def test_generate_entity_contributions_chapter_no_repository(self):
        """Test chapter with no repository."""
        command = Command()
        start_at = datetime(2025, 1, 1, tzinfo=UTC)
        end_at = datetime(2025, 10, 1, tzinfo=UTC)

        mock_user = mock.Mock()
        mock_user.id = 1

        mock_commits = mock.Mock()
        mock_commits.select_related.return_value = iter([])
        mock_commits.__iter__ = lambda _: iter([])

        mock_prs = mock.Mock()
        mock_prs.select_related.return_value = iter([])
        mock_prs.__iter__ = lambda _: iter([])

        mock_issues = mock.Mock()
        mock_issues.select_related.return_value = iter([])
        mock_issues.__iter__ = lambda _: iter([])

        target_module = "apps.owasp.management.commands.owasp_create_member_snapshot"

        with (
            mock.patch(f"{target_module}.Chapter") as mock_chapter_model,
            mock.patch(f"{target_module}.ContentType") as mock_content_type,
            mock.patch(f"{target_module}.EntityMember") as mock_entity_member,
        ):
            mock_content_type.objects.get_for_model.return_value = mock.Mock(id=2)
            mock_entity_member.objects.filter.return_value.values_list.return_value = [1]

            mock_chapter = mock.Mock()
            mock_chapter.nest_key = "test-chapter"
            mock_chapter.owasp_repository_id = None

            mock_filter = mock.Mock()
            mock_filter.select_related.return_value = [mock_chapter]
            mock_filter.__iter__ = lambda _: iter([mock_chapter])
            mock_chapter_model.objects.filter.return_value = mock_filter

            result = command.generate_entity_contributions(
                mock_user,
                mock_commits,
                mock_prs,
                mock_issues,
                "chapter",
                start_at,
                end_at,
            )
            assert result == {"test-chapter": 0}

    def test_generate_entity_contributions_pr_outside_date_range(self):
        """Test PR contribution with created_at = None or outside range."""
        command = Command()
        start_at = datetime(2025, 1, 1, tzinfo=UTC)
        end_at = datetime(2025, 10, 1, tzinfo=UTC)

        mock_user = mock.Mock()
        mock_user.id = 1

        mock_pr = mock.Mock()
        mock_pr.created_at = None
        mock_pr.repository_id = 100

        mock_commits = mock.Mock()
        mock_commits.select_related.return_value = iter([])
        mock_commits.__iter__ = lambda _: iter([])

        mock_prs = mock.Mock()
        mock_prs.select_related.return_value = iter([mock_pr])
        mock_prs.__iter__ = lambda _: iter([mock_pr])

        mock_issues = mock.Mock()
        mock_issues.select_related.return_value = iter([])
        mock_issues.__iter__ = lambda _: iter([])

        target_module = "apps.owasp.management.commands.owasp_create_member_snapshot"

        with (
            mock.patch(f"{target_module}.Chapter") as mock_chapter_model,
            mock.patch(f"{target_module}.ContentType") as mock_content_type,
            mock.patch(f"{target_module}.EntityMember") as mock_entity_member,
        ):
            mock_content_type.objects.get_for_model.return_value = mock.Mock(id=2)
            mock_entity_member.objects.filter.return_value.values_list.return_value = [1]

            mock_chapter = mock.Mock()
            mock_chapter.nest_key = "test-chapter"
            mock_chapter.owasp_repository_id = 100

            mock_filter = mock.Mock()
            mock_filter.select_related.return_value = [mock_chapter]
            mock_filter.__iter__ = lambda _: iter([mock_chapter])
            mock_chapter_model.objects.filter.return_value = mock_filter

            result = command.generate_entity_contributions(
                mock_user,
                mock_commits,
                mock_prs,
                mock_issues,
                "chapter",
                start_at,
                end_at,
            )
            assert result == {"test-chapter": 0}

    def test_generate_entity_contributions_issue_outside_date_range(self):
        """Test issue contribution with created_at = None or outside range."""
        command = Command()
        start_at = datetime(2025, 1, 1, tzinfo=UTC)
        end_at = datetime(2025, 10, 1, tzinfo=UTC)

        mock_user = mock.Mock()
        mock_user.id = 1

        mock_issue = mock.Mock()
        mock_issue.created_at = None
        mock_issue.repository_id = 100

        mock_commits = mock.Mock()
        mock_commits.select_related.return_value = iter([])
        mock_commits.__iter__ = lambda _: iter([])

        mock_prs = mock.Mock()
        mock_prs.select_related.return_value = iter([])
        mock_prs.__iter__ = lambda _: iter([])

        mock_issues = mock.Mock()
        mock_issues.select_related.return_value = iter([mock_issue])
        mock_issues.__iter__ = lambda _: iter([mock_issue])

        target_module = "apps.owasp.management.commands.owasp_create_member_snapshot"

        with (
            mock.patch(f"{target_module}.Chapter") as mock_chapter_model,
            mock.patch(f"{target_module}.ContentType") as mock_content_type,
            mock.patch(f"{target_module}.EntityMember") as mock_entity_member,
        ):
            mock_content_type.objects.get_for_model.return_value = mock.Mock(id=2)
            mock_entity_member.objects.filter.return_value.values_list.return_value = [1]

            mock_chapter = mock.Mock()
            mock_chapter.nest_key = "test-chapter"
            mock_chapter.owasp_repository_id = 100

            mock_filter = mock.Mock()
            mock_filter.select_related.return_value = [mock_chapter]
            mock_filter.__iter__ = lambda _: iter([mock_chapter])
            mock_chapter_model.objects.filter.return_value = mock_filter

            result = command.generate_entity_contributions(
                mock_user,
                mock_commits,
                mock_prs,
                mock_issues,
                "chapter",
                start_at,
                end_at,
            )
            assert result == {"test-chapter": 0}
