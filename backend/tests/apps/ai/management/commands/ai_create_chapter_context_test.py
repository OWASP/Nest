"""Tests for the ai_create_chapter_context Django management command."""

from unittest.mock import MagicMock, Mock, patch

import pytest
from django.core.management.base import BaseCommand

from apps.ai.management.commands.ai_create_chapter_context import Command


@pytest.fixture
def command():
    """Return a command instance."""
    return Command()


@pytest.fixture
def mock_chapter():
    """Return a mock Chapter instance."""
    chapter = Mock()
    chapter.id = 1
    chapter.key = "test-chapter"
    return chapter


class TestAiCreateChapterContextCommand:
    """Test suite for the ai_create_chapter_context command."""

    def test_command_help_text(self, command):
        """Test that the command has the correct help text."""
        assert command.help == "Update context for OWASP chapter data"

    def test_command_inheritance(self, command):
        """Test that the command inherits from BaseCommand."""
        assert isinstance(command, BaseCommand)

    def test_add_arguments(self, command):
        """Test that the command adds the correct arguments."""
        parser = MagicMock()
        command.add_arguments(parser)

        assert parser.add_argument.call_count == 3
        parser.add_argument.assert_any_call(
            "--chapter-key",
            type=str,
            help="Process only the chapter with this key",
        )
        parser.add_argument.assert_any_call(
            "--all",
            action="store_true",
            help="Process all the chapters",
        )
        parser.add_argument.assert_any_call(
            "--batch-size",
            type=int,
            default=50,
            help="Number of chapters to process in each batch",
        )

    @patch("apps.ai.management.commands.ai_create_chapter_context.Chapter.objects")
    def test_handle_no_chapters_found(self, mock_chapter_objects, command):
        """Test command when no chapters are found."""
        command.stdout = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 0
        mock_chapter_objects.filter.return_value = mock_queryset

        command.handle(chapter_key=None, all=False, batch_size=50)

        command.stdout.write.assert_called_with("No chapters found to process")

    @patch("apps.ai.management.commands.ai_create_chapter_context.Chapter.objects")
    def test_handle_with_chapter_key(self, mock_chapter_objects, command, mock_chapter):
        """Test command with specific chapter key."""
        command.stdout = MagicMock()
        command.style = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 1
        mock_queryset.__iter__ = lambda _self: iter([mock_chapter])
        mock_queryset.__getitem__ = lambda _self, _key: [mock_chapter]
        mock_chapter_objects.filter.return_value = mock_queryset

        with patch.object(command, "process_context_batch", return_value=1):
            command.handle(chapter_key="test-chapter", all=False, batch_size=50)

        mock_chapter_objects.filter.assert_called_with(key="test-chapter")

    @patch("apps.ai.management.commands.ai_create_chapter_context.Chapter.objects")
    def test_handle_with_all_flag(self, mock_chapter_objects, command, mock_chapter):
        """Test command with --all flag."""
        command.stdout = MagicMock()
        command.style = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 1
        mock_queryset.__iter__ = lambda _self: iter([mock_chapter])
        mock_queryset.__getitem__ = lambda _self, _key: [mock_chapter]
        mock_chapter_objects.all.return_value = mock_queryset

        with patch.object(command, "process_context_batch", return_value=1):
            command.handle(chapter_key=None, all=True, batch_size=50)

        mock_chapter_objects.all.assert_called_once()

    @patch("apps.ai.management.commands.ai_create_chapter_context.Chapter.objects")
    def test_handle_default_active_chapters(self, mock_chapter_objects, command, mock_chapter):
        """Test command defaults to active chapters."""
        command.stdout = MagicMock()
        command.style = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 1
        mock_queryset.__iter__ = lambda _self: iter([mock_chapter])
        mock_queryset.__getitem__ = lambda _self, _key: [mock_chapter]
        mock_chapter_objects.filter.return_value = mock_queryset

        with patch.object(command, "process_context_batch", return_value=1):
            command.handle(chapter_key=None, all=False, batch_size=50)

        mock_chapter_objects.filter.assert_called_with(is_active=True)

    @patch("apps.ai.management.commands.ai_create_chapter_context.extract_chapter_content")
    @patch("apps.ai.management.commands.ai_create_chapter_context.create_context")
    def test_process_context_batch_success(
        self,
        mock_create_context,
        mock_extract,
        command,
        mock_chapter,
    ):
        """Test successful batch processing of contexts."""
        command.stdout = MagicMock()

        # Setup mocks
        mock_extract.return_value = ("prose content", "metadata content")
        mock_create_context.return_value = True

        result = command.process_context_batch([mock_chapter])

        assert result == 1
        mock_extract.assert_called_once_with(mock_chapter)
        mock_create_context.assert_called_once_with(
            content="metadata content\n\nprose content",
            content_object=mock_chapter,
            source="owasp_chapter",
        )

    @patch("apps.ai.management.commands.ai_create_chapter_context.extract_chapter_content")
    @patch("apps.ai.management.commands.ai_create_chapter_context.create_context")
    def test_process_context_batch_no_metadata(
        self,
        mock_create_context,
        mock_extract,
        command,
        mock_chapter,
    ):
        """Test batch processing without metadata content."""
        command.stdout = MagicMock()

        # Setup mocks
        mock_extract.return_value = ("prose content", "")
        mock_create_context.return_value = True

        result = command.process_context_batch([mock_chapter])

        assert result == 1
        mock_extract.assert_called_once_with(mock_chapter)
        mock_create_context.assert_called_once_with(
            content="prose content",
            content_object=mock_chapter,
            source="owasp_chapter",
        )

    @patch("apps.ai.management.commands.ai_create_chapter_context.extract_chapter_content")
    def test_process_context_batch_no_content(
        self,
        mock_extract,
        command,
        mock_chapter,
    ):
        """Test batch processing when no content is extracted."""
        command.stdout = MagicMock()

        # Setup mocks
        mock_extract.return_value = ("", "")

        result = command.process_context_batch([mock_chapter])

        assert result == 0
        command.stdout.write.assert_any_call(f"No content for chapter {mock_chapter.key}")

    @patch("apps.ai.management.commands.ai_create_chapter_context.extract_chapter_content")
    @patch("apps.ai.management.commands.ai_create_chapter_context.create_context")
    def test_process_context_batch_create_context_fails(
        self,
        mock_create_context,
        mock_extract,
        command,
        mock_chapter,
    ):
        """Test batch processing when create_context fails."""
        command.stdout = MagicMock()
        command.style = MagicMock()

        # Setup mocks
        mock_extract.return_value = ("prose content", "metadata content")
        mock_create_context.return_value = False

        result = command.process_context_batch([mock_chapter])

        assert result == 0
        command.style.ERROR.assert_called_once()
