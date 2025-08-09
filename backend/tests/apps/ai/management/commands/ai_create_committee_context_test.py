"""Tests for the ai_create_committee_context Django management command."""

from unittest.mock import MagicMock, Mock, patch

import pytest
from django.core.management.base import BaseCommand

from apps.ai.management.commands.ai_create_committee_context import Command


@pytest.fixture
def command():
    """Return a command instance."""
    return Command()


@pytest.fixture
def mock_committee():
    """Return a mock Committee instance."""
    committee = Mock()
    committee.id = 1
    committee.key = "test-committee"
    return committee


class TestAiCreateCommitteeContextCommand:
    """Test suite for the ai_create_committee_context command."""

    def test_command_help_text(self, command):
        """Test that the command has the correct help text."""
        assert command.help == "Update context for OWASP committee data"

    def test_command_inheritance(self, command):
        """Test that the command inherits from BaseCommand."""
        assert isinstance(command, BaseCommand)

    def test_add_arguments(self, command):
        """Test that the command adds the correct arguments."""
        parser = MagicMock()
        command.add_arguments(parser)

        assert parser.add_argument.call_count == 3
        parser.add_argument.assert_any_call(
            "--committee-key",
            type=str,
            help="Process only the committee with this key",
        )
        parser.add_argument.assert_any_call(
            "--all",
            action="store_true",
            help="Process all the committees",
        )
        parser.add_argument.assert_any_call(
            "--batch-size",
            type=int,
            default=50,
            help="Number of committees to process in each batch",
        )

    @patch("apps.ai.management.commands.ai_create_committee_context.Committee.objects")
    def test_handle_no_committees_found(self, mock_committee_objects, command):
        """Test command when no committees are found."""
        command.stdout = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 0
        mock_committee_objects.filter.return_value = mock_queryset

        command.handle(committee_key=None, all=False, batch_size=50)

        command.stdout.write.assert_called_with("No committees found to process")

    @patch("apps.ai.management.commands.ai_create_committee_context.Committee.objects")
    def test_handle_with_committee_key(self, mock_committee_objects, command, mock_committee):
        """Test command with specific committee key."""
        command.stdout = MagicMock()
        command.style = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 1
        mock_queryset.__iter__ = lambda _self: iter([mock_committee])
        mock_queryset.__getitem__ = lambda _self, _key: [mock_committee]
        mock_committee_objects.filter.return_value = mock_queryset

        with patch.object(command, "process_context_batch", return_value=1):
            command.handle(committee_key="test-committee", all=False, batch_size=50)

        mock_committee_objects.filter.assert_called_with(key="test-committee")

    @patch("apps.ai.management.commands.ai_create_committee_context.Committee.objects")
    def test_handle_with_all_flag(self, mock_committee_objects, command, mock_committee):
        """Test command with --all flag."""
        command.stdout = MagicMock()
        command.style = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 1
        mock_queryset.__iter__ = lambda _self: iter([mock_committee])
        mock_queryset.__getitem__ = lambda _self, _key: [mock_committee]
        mock_committee_objects.all.return_value = mock_queryset

        with patch.object(command, "process_context_batch", return_value=1):
            command.handle(committee_key=None, all=True, batch_size=50)

        mock_committee_objects.all.assert_called_once()

    @patch("apps.ai.management.commands.ai_create_committee_context.Committee.objects")
    def test_handle_default_active_committees(
        self, mock_committee_objects, command, mock_committee
    ):
        """Test command defaults to active committees."""
        command.stdout = MagicMock()
        command.style = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 1
        mock_queryset.__iter__ = lambda _self: iter([mock_committee])
        mock_queryset.__getitem__ = lambda _self, _key: [mock_committee]
        mock_committee_objects.filter.return_value = mock_queryset

        with patch.object(command, "process_context_batch", return_value=1):
            command.handle(committee_key=None, all=False, batch_size=50)

        mock_committee_objects.filter.assert_called_with(is_active=True)
