"""Tests for the slack_create_chunks management command."""

import os
from io import StringIO
from unittest.mock import Mock, patch

import pytest
from django.core.management import call_command

from apps.ai.management.commands.slack_create_chunks import Command
from apps.ai.models.chunk import Chunk
from apps.slack.models.message import Message


class TestSlackCreateChunksCommand:
    """Test cases for the slack_create_chunks management command."""

    @pytest.fixture
    def command(self):
        """Create a Command instance for testing."""
        return Command()

    @pytest.fixture
    def mock_message(self):
        """Create a mock message."""
        message = Mock(spec=Message)
        message.slack_message_id = "1234567890.123456"
        message.raw_data = {"text": "This is a test message content for chunking"}
        return message

    @pytest.fixture
    def mock_message_with_subtype(self):
        """Create a mock message with join/leave subtype."""
        message = Mock(spec=Message)
        message.slack_message_id = "1234567890.123457"
        message.raw_data = {"text": "User joined channel", "subtype": "channel_join"}
        return message

    @pytest.fixture
    def mock_message_empty_text(self):
        """Create a mock message with empty text."""
        message = Mock(spec=Message)
        message.slack_message_id = "1234567890.123458"
        message.raw_data = {"text": ""}
        return message

    @pytest.fixture
    def mock_openai_embedding_response(self):
        """Create a mock OpenAI embedding response."""
        mock_data = [
            Mock(embedding=[0.1, 0.2, 0.3, 0.4, 0.5]),
            Mock(embedding=[0.6, 0.7, 0.8, 0.9, 1.0]),
        ]
        mock_response = Mock()
        mock_response.data = mock_data
        return mock_response

    @pytest.fixture(autouse=True)
    def mock_env_var(self):
        """Mock the environment variable for OpenAI API key."""
        with patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-api-key"}):
            yield

    def test_handle_no_openai_api_key(self, command):
        """Test handle method when OpenAI API key is not set."""
        with patch.dict(os.environ, {}, clear=True):
            stdout = StringIO()
            command.stdout = stdout

            command.handle()

            output = stdout.getvalue()
            assert "DJANGO_OPEN_AI_SECRET_KEY environment variable not set" in output

    @patch("builtins.print")
    @patch("apps.slack.models.message.Message.objects")
    @patch("openai.OpenAI")
    def test_handle_success(
        self, mock_openai_client, mock_message_objects, mock_print, command, mock_message
    ):
        """Test successful execution of handle method."""
        mock_message_objects.count.return_value = 1
        mock_message_objects.all.return_value.__getitem__.return_value = [mock_message]

        mock_client_instance = Mock()
        mock_openai_client.return_value = mock_client_instance

        mock_embedding_response = Mock()
        mock_embedding_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
        mock_client_instance.embeddings.create.return_value = mock_embedding_response

        stdout = StringIO()
        command.stdout = stdout

        with (
            patch.object(Chunk, "bulk_save") as mock_bulk_save,
            patch.object(Chunk, "update_data", return_value=Mock()) as mock_update_data,
        ):
            command.handle()

            mock_print.assert_called_with("Found 1 messages to process")
            output = stdout.getvalue()
            assert "Completed processing all 1 messages" in output
            mock_bulk_save.assert_called()
            mock_update_data.assert_called()

    def test_create_chunks_from_message_with_join_subtype(
        self, command, mock_message_with_subtype
    ):
        """Test create_chunks_from_message with channel_join subtype."""
        result = command.create_chunks_from_message(mock_message_with_subtype, "User joined")

        assert result == []

    def test_create_chunks_from_message_with_leave_subtype(self, command):
        """Test create_chunks_from_message with channel_leave subtype."""
        message = Mock(spec=Message)
        message.slack_message_id = "1234567890.123459"
        message.raw_data = {"text": "User left channel", "subtype": "channel_leave"}

        result = command.create_chunks_from_message(message, "User left")

        assert result == []

    def test_create_chunks_from_message_empty_chunks(self, command, mock_message_empty_text):
        """Test create_chunks_from_message when no chunks are created."""
        stdout = StringIO()
        command.stdout = stdout

        with patch.object(command, "split_message_text", return_value=[]):
            result = command.create_chunks_from_message(mock_message_empty_text, "")

            assert result == []
            output = stdout.getvalue()
            assert "No chunks created for message 1234567890.123458 - text too short" in output

    def test_create_chunks_from_message_success(
        self, command, mock_message, mock_openai_embedding_response
    ):
        """Test successful chunk creation from message."""
        mock_client = Mock()
        mock_client.embeddings.create.return_value = mock_openai_embedding_response
        command.openai_client = mock_client

        mock_chunk = Mock(spec=Chunk)

        with (
            patch.object(command, "split_message_text", return_value=["chunk1", "chunk2"]),
            patch.object(Chunk, "update_data", return_value=mock_chunk) as mock_update_data,
        ):
            result = command.create_chunks_from_message(mock_message, "test message")

            assert len(result) == 2
            assert all(chunk == mock_chunk for chunk in result)
            assert mock_update_data.call_count == 2
            mock_client.embeddings.create.assert_called_once_with(
                model="text-embedding-3-small", input=["chunk1", "chunk2"]
            )

            for call in mock_update_data.call_args_list:
                assert call.kwargs.get("save") is False

    @patch("langchain.text_splitter.RecursiveCharacterTextSplitter")
    def test_split_message_text(self, mock_splitter_class, command):
        """Test message text splitting functionality."""
        mock_splitter = Mock()
        mock_splitter.split_text.return_value = ["chunk1", "chunk2", "chunk3"]
        mock_splitter_class.return_value = mock_splitter

        long_text = "This is a long message that should be split into multiple chunks. " * 10

        result = command.split_message_text(long_text)

        mock_splitter_class.assert_called_once_with(
            chunk_size=300,
            chunk_overlap=40,
            length_function=len,
            separators=["\n\n", "\n", " ", ""],
        )
        mock_splitter.split_text.assert_called_once_with(long_text)
        assert result == ["chunk1", "chunk2", "chunk3"]

    @patch("langchain.text_splitter.RecursiveCharacterTextSplitter")
    def test_split_message_text_short(self, mock_splitter_class, command):
        """Test message text splitting with short text."""
        mock_splitter = Mock()
        mock_splitter.split_text.return_value = ["Short message"]
        mock_splitter_class.return_value = mock_splitter

        short_text = "Short message"

        result = command.split_message_text(short_text)

        assert result == ["Short message"]
        mock_splitter.split_text.assert_called_once_with(short_text)

    @patch("langchain.text_splitter.RecursiveCharacterTextSplitter")
    def test_split_message_text_empty(self, mock_splitter_class, command):
        """Test message text splitting with empty text."""
        mock_splitter = Mock()
        mock_splitter.split_text.return_value = []
        mock_splitter_class.return_value = mock_splitter

        result = command.split_message_text("")

        assert result == []

    @pytest.mark.parametrize(
        ("input_text", "expected_patterns"),
        [
            ("Hello world", "Hello world"),
            ("Hello <@U123456> world", "Hello  world"),
            ("Check this link <https://example.com>", "Check this link "),
            ("This is :smile: awesome :thumbsup:", "This is  awesome "),
            ("Multiple   spaces", "Multiple spaces"),
            ("", ""),
            ("  spaces around  ", "spaces around"),
        ],
    )
    def test_clean_message_text(self, command, input_text, expected_patterns):
        """Test message text cleaning functionality."""
        result = command.clean_message_text(input_text)

        assert result == expected_patterns

    def test_clean_message_text_with_emojis(self, command):
        """Test message text cleaning with emoji characters."""
        text_with_emojis = "Hello 😀😃😄 world 🌍🌎🌏"

        result = command.clean_message_text(text_with_emojis)

        assert "😀" not in result
        assert "😃" not in result
        assert "🌍" not in result
        assert "Hello" in result
        assert "world" in result

    def test_clean_message_text_complex_patterns(self, command):
        """Test message text cleaning with complex patterns."""
        complex_text = (
            "Hey <@U123456>! Check out <https://example.com/path?param=value> :rocket: Amazing!"
        )

        result = command.clean_message_text(complex_text)

        assert "<@U123456>" not in result
        assert "<https://example.com/path?param=value>" not in result
        assert ":rocket:" not in result
        assert "Hey" in result
        assert "Amazing" in result

    @patch("builtins.print")
    @patch("apps.slack.models.message.Message.objects")
    @patch("openai.OpenAI")
    def test_handle_batch_processing(
        self, mock_openai_client, mock_message_objects, mock_print, command
    ):
        """Test that messages are processed in batches."""
        mock_message_objects.count.return_value = 2500

        mock_messages_batch1 = [Mock(spec=Message) for _ in range(1000)]
        mock_messages_batch2 = [Mock(spec=Message) for _ in range(1000)]
        mock_messages_batch3 = [Mock(spec=Message) for _ in range(500)]

        def mock_getitem(slice_obj):
            start = slice_obj.start or 0
            stop = slice_obj.stop or 2500
            if start == 0 and stop == 1000:
                return mock_messages_batch1
            if start == 1000 and stop == 2000:
                return mock_messages_batch2
            if start == 2000 and stop == 2500:
                return mock_messages_batch3
            return []

        mock_message_objects.all.return_value.__getitem__ = mock_getitem

        for i, message in enumerate(
            mock_messages_batch1 + mock_messages_batch2 + mock_messages_batch3
        ):
            message.slack_message_id = f"msg_{i}"
            message.raw_data = {"text": f"Message {i}"}

        mock_client_instance = Mock()
        mock_openai_client.return_value = mock_client_instance

        mock_embedding_response = Mock()
        mock_embedding_response.data = []
        mock_client_instance.embeddings.create.return_value = mock_embedding_response

        stdout = StringIO()
        command.stdout = stdout

        with (
            patch.object(Chunk, "bulk_save") as mock_bulk_save,
            patch.object(command, "create_chunks_from_message", return_value=[]),
        ):
            command.handle()

            mock_print.assert_called_with("Found 2500 messages to process")
            output = stdout.getvalue()
            assert "Completed processing all 2500 messages" in output

            assert mock_bulk_save.call_count == 0

    @patch("django.core.management.call_command")
    def test_call_command_integration(self, mock_call_command):
        """Test that the command can be called via call_command."""
        call_command("slack_create_chunks")

        mock_call_command.assert_called_once_with("slack_create_chunks")

    def test_command_help_text(self, command):
        """Test that the command has appropriate help text."""
        assert command.help == "Create chunks for Slack messages"

    @patch("builtins.print")
    @patch("apps.slack.models.message.Message.objects")
    @patch("openai.OpenAI")
    def test_handle_with_no_messages(
        self, mock_openai_client, mock_message_objects, mock_print, command
    ):
        """Test handle method when there are no messages."""
        mock_message_objects.count.return_value = 0

        stdout = StringIO()
        command.stdout = stdout

        command.handle()

        mock_print.assert_called_with("Found 0 messages to process")
        output = stdout.getvalue()
        assert "Completed processing all 0 messages" in output

    def test_create_chunks_from_message_with_none_subtype(self, command, mock_message):
        """Test create_chunks_from_message with None subtype."""
        mock_message.raw_data = {"text": "Regular message"}

        mock_client = Mock()
        mock_embedding_response = Mock()
        mock_embedding_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
        mock_client.embeddings.create.return_value = mock_embedding_response
        command.openai_client = mock_client

        mock_chunk = Mock(spec=Chunk)

        with (
            patch.object(command, "split_message_text", return_value=["chunk1"]),
            patch.object(Chunk, "update_data", return_value=mock_chunk) as mock_update_data,
        ):
            result = command.create_chunks_from_message(mock_message, "Regular message")

            assert len(result) == 1
            assert result[0] == mock_chunk

            mock_update_data.assert_called_once()
            assert mock_update_data.call_args.kwargs.get("save") is False
