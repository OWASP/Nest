"""Tests for the github_enrich_issues command."""

from unittest import mock

import pytest

from apps.common.open_ai import OpenAi
from apps.github.management.commands.github_enrich_issues import Command
from apps.github.models.issue import Issue

builtins_print = "builtins.print"


class TestGitHubEnrichIssuesCommand:
    """Test suite for GitHub enrich issues command."""

    @pytest.fixture
    def command(self):
        """Return a command instance for testing."""
        return Command()

    @pytest.fixture
    def mock_issue(self):
        """Return a mock issue instance."""
        issue = mock.Mock(spec=Issue)
        issue.title = "Test Issue"
        return issue

    @pytest.mark.parametrize(
        (
            "offset",
            "issues_count",
            "force_update_hint",
            "force_update_summary",
            "update_hint",
            "update_summary",
        ),
        [
            (0, 3, False, False, True, True),
            (2, 5, True, False, True, True),
            (0, 6, False, True, False, True),
            (1, 8, True, True, True, False),
            (0, 3, False, False, False, False),
        ],
    )
    @mock.patch.object(OpenAi, "__init__", return_value=None)
    def test_handle(
        self,
        mock_openai_init,
        command,
        mock_issue,
        offset,
        issues_count,
        force_update_hint,
        force_update_summary,
        update_hint,
        update_summary,
    ):
        """Test the handle command with various parameters."""
        mock_issues_list = [mock_issue] * issues_count

        mock_filtered_issues = mock.MagicMock()
        mock_filtered_issues.__iter__.return_value = iter(mock_issues_list[offset:])
        mock_filtered_issues.count.return_value = len(mock_issues_list)
        mock_filtered_issues.__getitem__ = lambda _: []
        mock_filtered_issues.order_by.return_value = mock_filtered_issues

        mock_open_issues = mock.MagicMock()
        mock_open_issues.__iter__.return_value = iter(mock_issues_list[offset:])
        mock_open_issues.count.return_value = len(mock_issues_list)
        mock_open_issues.__getitem__ = (
            lambda _, idx: mock_issues_list[idx]
            if isinstance(idx, int)
            else mock_issues_list[idx.start : idx.stop]
        )
        mock_open_issues.order_by.return_value = mock_open_issues
        mock_open_issues.without_summary = mock_filtered_issues

        expected_update_fields = []
        if update_hint:
            expected_update_fields.append("hint")
        if update_summary:
            expected_update_fields.append("summary")

        with (
            mock.patch.object(Issue, "open_issues", mock_open_issues),
            mock.patch.object(Issue, "bulk_save") as mock_bulk_save,
            mock.patch.object(mock_issue, "generate_hint") as mock_generate_hint,
            mock.patch.object(mock_issue, "generate_summary") as mock_generate_summary,
            mock.patch(builtins_print),
        ):
            command.handle(
                offset=offset,
                force_update_hint=force_update_hint,
                force_update_summary=force_update_summary,
                update_hint=update_hint,
                update_summary=update_summary,
            )

            if issues_count - offset > 0:
                mock_bulk_save.assert_called_once()

                assert set(mock_bulk_save.call_args[1].get("fields", [])) == set(
                    expected_update_fields
                )

                mock_openai_init.assert_called_once()

                expected_generate_hint_calls = issues_count - offset if update_hint else 0
                assert mock_generate_hint.call_count == expected_generate_hint_calls

                expected_generate_summary_calls = issues_count - offset if update_summary else 0
                assert mock_generate_summary.call_count == expected_generate_summary_calls

    @mock.patch.object(OpenAi, "__init__", return_value=None)
    def test_handle_with_batch_processing(self, mock_openai_init, command, mock_issue):
        """Test the batch processing logic in the handle method."""
        batch_size = 1001
        mock_issues_list = [mock_issue] * batch_size

        mock_filtered_issues = mock.MagicMock()
        mock_filtered_issues.__iter__.return_value = iter(mock_issues_list)
        mock_filtered_issues.count.return_value = len(mock_issues_list)
        mock_filtered_issues.__getitem__ = lambda _: []
        mock_filtered_issues.order_by.return_value = mock_filtered_issues

        mock_open_issues = mock.MagicMock()
        mock_open_issues.__iter__.return_value = iter(mock_issues_list)
        mock_open_issues.count.return_value = len(mock_issues_list)
        mock_open_issues.__getitem__ = (
            lambda _, idx: mock_issues_list[idx]
            if isinstance(idx, int)
            else mock_issues_list[idx.start : idx.stop]
        )
        mock_open_issues.order_by.return_value = mock_open_issues
        mock_open_issues.without_summary = mock_filtered_issues

        with (
            mock.patch.object(Issue, "open_issues", mock_open_issues),
            mock.patch.object(Issue, "bulk_save") as mock_bulk_save,
            mock.patch.object(mock_issue, "generate_hint") as mock_generate_hint,
            mock.patch.object(mock_issue, "generate_summary") as mock_generate_summary,
            mock.patch(builtins_print),
        ):

            def side_effect():
                return mock.DEFAULT

            mock_bulk_save.side_effect = side_effect

            command.handle(
                offset=0,
                force_update_hint=False,
                force_update_summary=False,
                update_hint=True,
                update_summary=True,
            )
            call_count = 2
            assert mock_bulk_save.call_count == call_count

            assert mock_generate_hint.call_count == batch_size
            assert mock_generate_summary.call_count == batch_size

            calls = mock_bulk_save.call_args_list

            for call in calls:
                assert call[1].get("fields", []) == ["hint", "summary"]

    @mock.patch.object(OpenAi, "__init__", return_value=None)
    def test_handle_with_empty_issues_list(self, mock_openai_init, command):
        """Test handling when no issues are found."""
        mock_filtered_issues = mock.MagicMock()
        mock_filtered_issues.__iter__.return_value = iter([])
        mock_filtered_issues.count.return_value = 0
        mock_filtered_issues.__getitem__ = lambda _: []
        mock_filtered_issues.order_by.return_value = mock_filtered_issues

        mock_open_issues = mock.MagicMock()
        mock_open_issues.__iter__.return_value = iter([])
        mock_open_issues.count.return_value = 0
        mock_open_issues.__getitem__ = lambda _: []
        mock_open_issues.order_by.return_value = mock_open_issues
        mock_open_issues.without_summary = mock_filtered_issues

        with (
            mock.patch.object(Issue, "open_issues", mock_open_issues),
            mock.patch.object(Issue, "bulk_save") as mock_bulk_save,
            mock.patch(builtins_print),
        ):
            command.handle(
                offset=0,
                force_update_hint=False,
                force_update_summary=False,
                update_hint=True,
                update_summary=True,
            )

            mock_bulk_save.assert_called_once()
            issues_arg = mock_bulk_save.call_args[0][0]
            assert len(issues_arg) == 0

    @pytest.mark.parametrize(
        ("force_update_hint", "force_update_summary", "expected_query"),
        [
            (False, False, "without_summary"),
            (True, False, "all_issues"),
            (False, True, "all_issues"),
            (True, True, "all_issues"),
        ],
    )
    @mock.patch.object(OpenAi, "__init__", return_value=None)
    def test_handle_force_update_logic(
        self, mock_openai_init, command, force_update_hint, force_update_summary, expected_query
    ):
        """Test the force update logic affecting issue query selection."""
        mock_filtered_issues = mock.MagicMock()
        mock_filtered_issues.__iter__.return_value = iter([])
        mock_filtered_issues.count.return_value = 0
        mock_filtered_issues.order_by.return_value = mock_filtered_issues

        mock_open_issues = mock.MagicMock()
        mock_open_issues.__iter__.return_value = iter([])
        mock_open_issues.count.return_value = 0
        mock_open_issues.order_by.return_value = mock_open_issues
        mock_open_issues.without_summary = mock_filtered_issues

        with (
            mock.patch.object(Issue, "open_issues", mock_open_issues),
            mock.patch.object(Issue, "bulk_save"),
            mock.patch(builtins_print),
        ):
            command.handle(
                offset=0,
                force_update_hint=force_update_hint,
                force_update_summary=force_update_summary,
                update_hint=True,
                update_summary=True,
            )

            if expected_query == "without_summary":
                mock_filtered_issues.order_by.assert_called_once()
                assert mock_open_issues.order_by.call_count == 0
            else:
                mock_open_issues.order_by.assert_called_once()
                assert mock_filtered_issues.order_by.call_count == 0

    @mock.patch.object(OpenAi, "__init__", return_value=None)
    def test_handle_no_issues_found(self, mock_openai_init, command):
        mock_open_issues = mock.MagicMock()
        mock_open_issues.count.return_value = 0
        mock_open_issues.order_by.return_value = mock_open_issues
        mock_filtered_issues = mock.MagicMock()
        mock_filtered_issues.count.return_value = 0
        mock_filtered_issues.order_by.return_value = mock_filtered_issues
        mock_open_issues.without_summary = mock_filtered_issues

        with (
            mock.patch.object(Issue, "open_issues", mock_open_issues),
            mock.patch.object(Issue, "bulk_save") as mock_bulk_save,
            mock.patch(builtins_print) as mock_print,
        ):
            command.handle(
                offset=0,
                force_update_hint=False,
                force_update_summary=False,
                update_hint=True,
                update_summary=True,
            )
            mock_openai_init.assert_called_once()
            mock_bulk_save.assert_called_once()
            args, kwargs = mock_bulk_save.call_args
            assert len(args[0]) == 0
            assert kwargs.get("fields") == ["hint", "summary"]
            assert mock_print.call_count == 0
