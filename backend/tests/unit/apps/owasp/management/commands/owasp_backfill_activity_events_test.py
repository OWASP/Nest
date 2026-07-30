"""Tests for the owasp_backfill_activity_events Django management command."""

from unittest.mock import MagicMock, patch

import pytest

from django.core.management.base import BaseCommand

from apps.owasp.management.commands.owasp_backfill_activity_events import Command


class TestOwaspBackfillActivityEventsCommand:
    def test_command_help_text(self):
        """Test that the command has the correct help text."""
        command = Command()
        assert command.help == (
            "Backfill ActivityEvent records for existing pull requests, issues, and releases."
        )

    def test_command_inheritance(self):
        """Test that the command inherits from BaseCommand."""
        assert issubclass(Command, BaseCommand)

    @pytest.mark.parametrize(
        ("argument_name", "expected_properties"),
        [
            (
                "--offset",
                {
                    "default": 0,
                    "required": False,
                    "type": int,
                    "help": "Number of records to skip before starting backfill.",
                },
            ),
            (
                "--model",
                {
                    "default": "all",
                    "required": False,
                    "choices": ["all", "issue", "pull_request", "release"],
                    "help": "Which model type to backfill. Defaults to 'all'.",
                },
            ),
        ],
    )
    def test_add_arguments(self, argument_name, expected_properties):
        """Test that the command adds the correct arguments."""
        mock_parser = MagicMock()
        command = Command()
        command.add_arguments(mock_parser)
        mock_parser.add_argument.assert_any_call(argument_name, **expected_properties)

    @pytest.mark.parametrize(
        "model_option",
        ["all", "issue", "pull_request", "release"],
    )
    def test_handle_calls_correct_backfill_methods(self, mocker, model_option):
        """Test that handle() delegates to the correct backfill methods based on --model."""
        command = Command()
        command.stdout = MagicMock()

        mock_backfill_issues = mocker.patch.object(command, "backfill_issues")
        mock_backfill_pull_requests = mocker.patch.object(command, "backfill_pull_requests")
        mock_backfill_releases = mocker.patch.object(command, "backfill_releases")

        command.handle(offset=0, model=model_option)

        if model_option in ("all", "issue"):
            mock_backfill_issues.assert_called_once_with(0)
        else:
            mock_backfill_issues.assert_not_called()

        if model_option in ("all", "pull_request"):
            mock_backfill_pull_requests.assert_called_once_with(0)
        else:
            mock_backfill_pull_requests.assert_not_called()

        if model_option in ("all", "release"):
            mock_backfill_releases.assert_called_once_with(0)
        else:
            mock_backfill_releases.assert_not_called()

    @patch("apps.owasp.management.commands.owasp_backfill_activity_events.ActivityEvent")
    @patch("apps.owasp.management.commands.owasp_backfill_activity_events.Issue")
    def test_backfill_issues_processes_all(self, mock_issue_class, mock_activity_event_class):
        """Test that backfill_issues processes each issue and calls update_data."""
        mock_issue1 = MagicMock(id=1, number=1, title="Issue 1")
        mock_issue1.repository = MagicMock()
        mock_issue2 = MagicMock(id=2, number=2, title="Issue 2")
        mock_issue2.repository = MagicMock()

        mock_qs = MagicMock()
        mock_qs.count.return_value = 2
        mock_qs.__getitem__.return_value = [mock_issue1, mock_issue2]
        mock_issue_class.objects.select_related.return_value.order_by.return_value = mock_qs

        command = Command()
        command.stdout = MagicMock()
        command.backfill_issues(offset=0)

        mock_activity_event_class.update_data.assert_any_call(mock_issue1)
        mock_activity_event_class.update_data.assert_any_call(mock_issue2)
        assert mock_activity_event_class.update_data.call_count == 2

    @patch("apps.owasp.management.commands.owasp_backfill_activity_events.ActivityEvent")
    @patch("apps.owasp.management.commands.owasp_backfill_activity_events.Issue")
    def test_backfill_issues_skips_without_repository(
        self, mock_issue_class, mock_activity_event_class
    ):
        """Test that backfill_issues skips issues that have no repository."""
        mock_issue = MagicMock(id=1, number=1, title="Issue No Repo")
        mock_issue.repository = None

        mock_qs = MagicMock()
        mock_qs.count.return_value = 1
        mock_qs.__getitem__.return_value = [mock_issue]
        mock_issue_class.objects.select_related.return_value.order_by.return_value = mock_qs

        command = Command()
        command.stdout = MagicMock()
        command.backfill_issues(offset=0)

        mock_activity_event_class.update_data.assert_not_called()

    @patch("apps.owasp.management.commands.owasp_backfill_activity_events.ActivityEvent")
    @patch("apps.owasp.management.commands.owasp_backfill_activity_events.Issue")
    def test_backfill_issues_continues_on_error(
        self, mock_issue_class, mock_activity_event_class
    ):
        """Test that backfill_issues continues processing when one issue raises an exception."""
        mock_issue1 = MagicMock(id=1, number=1, title="Issue 1")
        mock_issue1.repository = MagicMock()
        mock_issue2 = MagicMock(id=2, number=2, title="Issue 2")
        mock_issue2.repository = MagicMock()

        mock_activity_event_class.update_data.side_effect = [Exception("DB error"), None]

        mock_qs = MagicMock()
        mock_qs.count.return_value = 2
        mock_qs.__getitem__.return_value = [mock_issue1, mock_issue2]
        mock_issue_class.objects.select_related.return_value.order_by.return_value = mock_qs

        command = Command()
        command.stdout = MagicMock()
        command.backfill_issues(offset=0)

        assert mock_activity_event_class.update_data.call_count == 2

    @patch("apps.owasp.management.commands.owasp_backfill_activity_events.ActivityEvent")
    @patch("apps.owasp.management.commands.owasp_backfill_activity_events.PullRequest")
    def test_backfill_pull_requests_processes_all(
        self, mock_pr_class, mock_activity_event_class
    ):
        """Test that backfill_pull_requests processes each PR and calls update_data."""
        mock_pr1 = MagicMock(id=1, number=1, title="PR 1")
        mock_pr1.repository = MagicMock()
        mock_pr2 = MagicMock(id=2, number=2, title="PR 2")
        mock_pr2.repository = MagicMock()

        mock_qs = MagicMock()
        mock_qs.count.return_value = 2
        mock_qs.__getitem__.return_value = [mock_pr1, mock_pr2]
        mock_pr_class.objects.select_related.return_value.order_by.return_value = mock_qs

        command = Command()
        command.stdout = MagicMock()
        command.backfill_pull_requests(offset=0)

        mock_activity_event_class.update_data.assert_any_call(mock_pr1)
        mock_activity_event_class.update_data.assert_any_call(mock_pr2)
        assert mock_activity_event_class.update_data.call_count == 2

    @patch("apps.owasp.management.commands.owasp_backfill_activity_events.ActivityEvent")
    @patch("apps.owasp.management.commands.owasp_backfill_activity_events.PullRequest")
    def test_backfill_pull_requests_skips_without_repository(
        self, mock_pr_class, mock_activity_event_class
    ):
        """Test that backfill_pull_requests skips PRs that have no repository."""
        mock_pr = MagicMock(id=1, number=1, title="PR No Repo")
        mock_pr.repository = None

        mock_qs = MagicMock()
        mock_qs.count.return_value = 1
        mock_qs.__getitem__.return_value = [mock_pr]
        mock_pr_class.objects.select_related.return_value.order_by.return_value = mock_qs

        command = Command()
        command.stdout = MagicMock()
        command.backfill_pull_requests(offset=0)

        mock_activity_event_class.update_data.assert_not_called()

    @patch("apps.owasp.management.commands.owasp_backfill_activity_events.ActivityEvent")
    @patch("apps.owasp.management.commands.owasp_backfill_activity_events.Release")
    def test_backfill_releases_processes_all(self, mock_release_class, mock_activity_event_class):
        """Test that backfill_releases processes each release and calls update_data."""
        mock_release1 = MagicMock(id=1, tag_name="v1.0.0", name="Release 1.0.0")
        mock_release1.repository = MagicMock()
        mock_release2 = MagicMock(id=2, tag_name="v2.0.0", name="Release 2.0.0")
        mock_release2.repository = MagicMock()

        mock_qs = MagicMock()
        mock_qs.count.return_value = 2
        mock_qs.__getitem__.return_value = [mock_release1, mock_release2]
        mock_release_class.objects.select_related.return_value.order_by.return_value = mock_qs

        command = Command()
        command.stdout = MagicMock()
        command.backfill_releases(offset=0)

        mock_activity_event_class.update_data.assert_any_call(mock_release1)
        mock_activity_event_class.update_data.assert_any_call(mock_release2)
        assert mock_activity_event_class.update_data.call_count == 2

    @patch("apps.owasp.management.commands.owasp_backfill_activity_events.ActivityEvent")
    @patch("apps.owasp.management.commands.owasp_backfill_activity_events.Release")
    def test_backfill_releases_skips_without_repository(
        self, mock_release_class, mock_activity_event_class
    ):
        """Test that backfill_releases skips releases that have no repository."""
        mock_release = MagicMock(id=1, tag_name="v1.0.0", name="Release 1.0.0")
        mock_release.repository = None

        mock_qs = MagicMock()
        mock_qs.count.return_value = 1
        mock_qs.__getitem__.return_value = [mock_release]
        mock_release_class.objects.select_related.return_value.order_by.return_value = mock_qs

        command = Command()
        command.stdout = MagicMock()
        command.backfill_releases(offset=0)

        mock_activity_event_class.update_data.assert_not_called()

    @patch("apps.owasp.management.commands.owasp_backfill_activity_events.ActivityEvent")
    @patch("apps.owasp.management.commands.owasp_backfill_activity_events.Issue")
    def test_backfill_issues_respects_offset(self, mock_issue_class, mock_activity_event_class):
        """Test that backfill_issues respects the offset argument."""
        mock_issue1 = MagicMock(id=3, number=3, title="Issue 3")
        mock_issue1.repository = MagicMock()

        mock_qs = MagicMock()
        mock_qs.count.return_value = 3
        mock_qs.__getitem__.return_value = [mock_issue1]
        mock_issue_class.objects.select_related.return_value.order_by.return_value = mock_qs

        command = Command()
        command.stdout = MagicMock()
        command.backfill_issues(offset=2)

        mock_qs.__getitem__.assert_called_once_with(slice(2, None))
        mock_activity_event_class.update_data.assert_called_once_with(mock_issue1)
