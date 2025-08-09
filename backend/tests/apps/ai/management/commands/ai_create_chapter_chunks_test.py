"""Tests for the ai_create_chapter_chunks Django management command."""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest
from django.core.management.base import BaseCommand

from apps.ai.management.commands.ai_create_chapter_chunks import Command


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


@pytest.fixture
def mock_context():
    """Return a mock Context instance."""
    context = Mock()
    context.id = 1
    return context


class TestAiCreateChapterChunksCommand:
    """Test suite for the ai_create_chapter_chunks command."""

    def test_command_help_text(self, command):
        """Test that the command has the correct help text."""
        assert command.help == "Create chunks for OWASP chapter data"

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

    @patch.dict(os.environ, {}, clear=True)
    def test_handle_missing_openai_key(self, command):
        """Test command fails when OpenAI API key is not set."""
        command.stdout = MagicMock()
        command.style = MagicMock()

        command.handle()

        command.stdout.write.assert_called_once()
        command.style.ERROR.assert_called_once_with(
            "DJANGO_OPEN_AI_SECRET_KEY environment variable not set"
        )

    @patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"})
    @patch("apps.ai.management.commands.ai_create_chapter_chunks.openai.OpenAI")
    @patch("apps.ai.management.commands.ai_create_chapter_chunks.Chapter.objects")
    def test_handle_no_chapters_found(self, mock_chapter_objects, mock_openai, command):
        """Test command when no chapters are found."""
        command.stdout = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 0
        mock_chapter_objects.filter.return_value = mock_queryset

        command.handle(chapter_key=None, all=False, batch_size=50)

        command.stdout.write.assert_called_with("No chapters found to process")

    @patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"})
    @patch("apps.ai.management.commands.ai_create_chapter_chunks.openai.OpenAI")
    @patch("apps.ai.management.commands.ai_create_chapter_chunks.Chapter.objects")
    def test_handle_with_chapter_key(
        self, mock_chapter_objects, mock_openai, command, mock_chapter
    ):
        """Test command with specific chapter key."""
        command.stdout = MagicMock()
        command.style = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 1
        mock_queryset.__iter__ = lambda _self: iter([mock_chapter])
        mock_queryset.__getitem__ = lambda _self, _key: [mock_chapter]
        mock_chapter_objects.filter.return_value = mock_queryset

        with patch.object(command, "process_chunks_batch", return_value=1):
            command.handle(chapter_key="test-chapter", all=False, batch_size=50)

        mock_chapter_objects.filter.assert_called_with(key="test-chapter")

    @patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"})
    @patch("apps.ai.management.commands.ai_create_chapter_chunks.openai.OpenAI")
    @patch("apps.ai.management.commands.ai_create_chapter_chunks.Chapter.objects")
    def test_handle_with_all_flag(self, mock_chapter_objects, mock_openai, command, mock_chapter):
        """Test command with --all flag."""
        command.stdout = MagicMock()
        command.style = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 1
        mock_queryset.__iter__ = lambda _self: iter([mock_chapter])
        mock_queryset.__getitem__ = lambda _self, _key: [mock_chapter]
        mock_chapter_objects.all.return_value = mock_queryset

        with patch.object(command, "process_chunks_batch", return_value=1):
            command.handle(chapter_key=None, all=True, batch_size=50)

        mock_chapter_objects.all.assert_called_once()

    @patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"})
    @patch("apps.ai.management.commands.ai_create_chapter_chunks.openai.OpenAI")
    @patch("apps.ai.management.commands.ai_create_chapter_chunks.Chapter.objects")
    def test_handle_default_active_chapters(
        self, mock_chapter_objects, mock_openai, command, mock_chapter
    ):
        """Test command defaults to active chapters."""
        command.stdout = MagicMock()
        command.style = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 1
        mock_queryset.__iter__ = lambda _self: iter([mock_chapter])
        mock_queryset.__getitem__ = lambda _self, _key: [mock_chapter]
        mock_chapter_objects.filter.return_value = mock_queryset

        with patch.object(command, "process_chunks_batch", return_value=1):
            command.handle(chapter_key=None, all=False, batch_size=50)

        mock_chapter_objects.filter.assert_called_with(is_active=True)

    @patch("apps.ai.management.commands.ai_create_chapter_chunks.ContentType.objects")
    @patch("apps.ai.management.commands.ai_create_chapter_chunks.Context.objects")
    @patch("apps.ai.management.commands.ai_create_chapter_chunks.extract_chapter_content")
    @patch("apps.ai.management.commands.ai_create_chapter_chunks.Chunk.split_text")
    @patch("apps.ai.management.commands.ai_create_chapter_chunks.create_chunks_and_embeddings")
    @patch("apps.ai.management.commands.ai_create_chapter_chunks.Chunk.bulk_save")
    def test_process_chunks_batch_success(
        self,
        mock_bulk_save,
        mock_create_chunks,
        mock_split_text,
        mock_extract,
        mock_context_objects,
        mock_content_type,
        command,
        mock_chapter,
        mock_context,
    ):
        """Test successful batch processing of chunks."""
        command.stdout = MagicMock()
        command.openai_client = MagicMock()

        # Setup mocks
        mock_content_type.get_for_model.return_value = MagicMock()
        mock_context_objects.filter.return_value.first.return_value = mock_context
        mock_extract.return_value = ("prose content", "metadata content")
        mock_split_text.return_value = ["chunk1", "chunk2"]
        mock_chunks = [Mock(), Mock()]
        mock_create_chunks.return_value = mock_chunks

        result = command.process_chunks_batch([mock_chapter])

        assert result == 1
        mock_extract.assert_called_once_with(mock_chapter)
        mock_split_text.assert_called_once_with("prose content")
        mock_create_chunks.assert_called_once()
        mock_bulk_save.assert_called_once_with(mock_chunks)

    @patch("apps.ai.management.commands.ai_create_chapter_chunks.ContentType.objects")
    @patch("apps.ai.management.commands.ai_create_chapter_chunks.Context.objects")
    def test_process_chunks_batch_no_context(
        self,
        mock_context_objects,
        mock_content_type,
        command,
        mock_chapter,
    ):
        """Test batch processing when no context is found."""
        command.stdout = MagicMock()
        command.style = MagicMock()

        # Setup mocks
        mock_content_type.get_for_model.return_value = MagicMock()
        mock_context_objects.filter.return_value.first.return_value = None

        result = command.process_chunks_batch([mock_chapter])

        assert result == 0
        command.style.WARNING.assert_called_once()

    @patch("apps.ai.management.commands.ai_create_chapter_chunks.ContentType.objects")
    @patch("apps.ai.management.commands.ai_create_chapter_chunks.Context.objects")
    @patch("apps.ai.management.commands.ai_create_chapter_chunks.extract_chapter_content")
    def test_process_chunks_batch_no_content(
        self,
        mock_extract,
        mock_context_objects,
        mock_content_type,
        command,
        mock_chapter,
        mock_context,
    ):
        """Test batch processing when no content is extracted."""
        command.stdout = MagicMock()

        # Setup mocks
        mock_content_type.get_for_model.return_value = MagicMock()
        mock_context_objects.filter.return_value.first.return_value = mock_context
        mock_extract.return_value = ("", "")

        result = command.process_chunks_batch([mock_chapter])

        assert result == 0
        command.stdout.write.assert_any_call(f"No content to chunk for chapter {mock_chapter.key}")
