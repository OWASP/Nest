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
    def test_backfill_objects_processes_all(self, mock_activity_event_class):
        """Test that backfill_objects calls update_data for every object."""
        mock_obj1 = MagicMock(repository=MagicMock())
        mock_obj2 = MagicMock(repository=MagicMock())

        mock_qs = MagicMock()
        mock_qs.count.return_value = 2
        mock_qs.__getitem__.return_value.iterator.return_value = iter([mock_obj1, mock_obj2])

        command = Command()
        command.stdout = MagicMock()
        command.backfill_objects(mock_qs, 0, "issues", str)

        mock_activity_event_class.update_data.assert_any_call(mock_obj1)
        mock_activity_event_class.update_data.assert_any_call(mock_obj2)
        assert mock_activity_event_class.update_data.call_count == 2

    @patch("apps.owasp.management.commands.owasp_backfill_activity_events.ActivityEvent")
    def test_backfill_objects_skips_without_repository(self, mock_activity_event_class):
        """Test that backfill_objects skips objects that have no repository."""
        mock_obj = MagicMock(repository=None)

        mock_qs = MagicMock()
        mock_qs.count.return_value = 1
        mock_qs.__getitem__.return_value.iterator.return_value = iter([mock_obj])

        command = Command()
        command.stdout = MagicMock()
        command.backfill_objects(mock_qs, 0, "issues", str)

        mock_activity_event_class.update_data.assert_not_called()

    @patch("apps.owasp.management.commands.owasp_backfill_activity_events.ActivityEvent")
    def test_backfill_objects_continues_on_error(self, mock_activity_event_class):
        """Test that backfill_objects continues when one object raises an exception."""
        mock_obj1 = MagicMock(repository=MagicMock())
        mock_obj2 = MagicMock(repository=MagicMock())

        mock_activity_event_class.update_data.side_effect = [Exception("DB error"), None]

        mock_qs = MagicMock()
        mock_qs.count.return_value = 2
        mock_qs.__getitem__.return_value.iterator.return_value = iter([mock_obj1, mock_obj2])

        command = Command()
        command.stdout = MagicMock()
        command.backfill_objects(mock_qs, 0, "issues", str)

        assert mock_activity_event_class.update_data.call_count == 2

    @patch("apps.owasp.management.commands.owasp_backfill_activity_events.ActivityEvent")
    def test_backfill_objects_respects_offset(self, mock_activity_event_class):
        """Test that backfill_objects slices the queryset with the given offset."""
        mock_qs = MagicMock()
        mock_qs.count.return_value = 5
        mock_qs.__getitem__.return_value.iterator.return_value = iter([])

        command = Command()
        command.stdout = MagicMock()
        command.backfill_objects(mock_qs, 3, "issues", str)

        mock_qs.__getitem__.assert_called_once_with(slice(3, None))

    @patch("apps.owasp.management.commands.owasp_backfill_activity_events.Issue")
    def test_backfill_issues_passes_correct_queryset(self, mock_issue_class, mocker):
        """Test that backfill_issues builds the right queryset and delegates."""
        mock_qs = MagicMock()
        mock_qs.__getitem__.return_value = mock_qs
        mock_issue_class.objects.select_related.return_value.order_by.return_value = mock_qs

        command = Command()
        command.stdout = MagicMock()
        mock_backfill_objects = mocker.patch.object(command, "backfill_objects")

        command.backfill_issues(offset=0)

        mock_issue_class.objects.select_related.assert_called_once_with("author", "repository")
        mock_issue_class.objects.select_related.return_value.order_by.assert_called_once_with(
            "created_at", "pk"
        )
        assert mock_backfill_objects.call_count == 1
        assert mock_backfill_objects.call_args[0][2] == "issues"

    @patch("apps.owasp.management.commands.owasp_backfill_activity_events.PullRequest")
    def test_backfill_pull_requests_passes_correct_queryset(self, mock_pr_class, mocker):
        """Test that backfill_pull_requests builds the right queryset and delegates."""
        mock_qs = MagicMock()
        mock_qs.__getitem__.return_value = mock_qs
        mock_pr_class.objects.select_related.return_value.order_by.return_value = mock_qs

        command = Command()
        command.stdout = MagicMock()
        mock_backfill_objects = mocker.patch.object(command, "backfill_objects")

        command.backfill_pull_requests(offset=0)

        mock_pr_class.objects.select_related.assert_called_once_with("author", "repository")
        mock_pr_class.objects.select_related.return_value.order_by.assert_called_once_with(
            "created_at", "pk"
        )
        assert mock_backfill_objects.call_count == 1
        assert mock_backfill_objects.call_args[0][2] == "pull requests"

    @patch("apps.owasp.management.commands.owasp_backfill_activity_events.Release")
    def test_backfill_releases_passes_correct_queryset(self, mock_release_class, mocker):
        """Test that backfill_releases builds the right queryset and delegates."""
        mock_qs = MagicMock()
        mock_qs.__getitem__.return_value = mock_qs
        mock_release_class.objects.select_related.return_value.order_by.return_value = mock_qs

        command = Command()
        command.stdout = MagicMock()
        mock_backfill_objects = mocker.patch.object(command, "backfill_objects")

        command.backfill_releases(offset=0)

        mock_release_class.objects.select_related.assert_called_once_with("author", "repository")
        mock_release_class.objects.select_related.return_value.order_by.assert_called_once_with(
            "created_at", "pk"
        )
        assert mock_backfill_objects.call_count == 1
        assert mock_backfill_objects.call_args[0][2] == "releases"

    @pytest.mark.parametrize(
        ("method_name", "model_patch_path"),
        [
            (
                "backfill_issues",
                "apps.owasp.management.commands.owasp_backfill_activity_events.Issue",
            ),
            (
                "backfill_pull_requests",
                "apps.owasp.management.commands.owasp_backfill_activity_events.PullRequest",
            ),
            (
                "backfill_releases",
                "apps.owasp.management.commands.owasp_backfill_activity_events.Release",
            ),
        ],
    )
    def test_backfill_wrapper_methods_pass_offset(self, method_name, model_patch_path, mocker):
        """Test that wrapper methods forward the offset argument to backfill_objects."""
        mock_model_class = mocker.patch(model_patch_path)
        mock_qs = MagicMock()
        mock_model_class.objects.select_related.return_value.order_by.return_value = mock_qs

        command = Command()
        command.stdout = MagicMock()
        mock_backfill_objects = mocker.patch.object(command, "backfill_objects")

        getattr(command, method_name)(offset=7)

        mock_backfill_objects.assert_called_once()
        assert mock_backfill_objects.call_args[0][1] == 7
