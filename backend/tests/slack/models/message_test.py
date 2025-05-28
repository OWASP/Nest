from datetime import UTC, datetime
from unittest.mock import Mock, patch

from apps.slack.models.conversation import Conversation
from apps.slack.models.message import Message


class TestMessageModel:
    def test_bulk_save(self):
        mock_messages = [Mock(id=None), Mock(id=1)]
        with patch("apps.common.models.BulkSaveModel.bulk_save") as mock_bulk_save:
            Message.bulk_save(mock_messages)
            mock_bulk_save.assert_called_once_with(Message, mock_messages, fields=None)

    def test_update_data_new_message(self, mocker):
        mock_conversation_instance = Mock(spec=Conversation)
        mock_conversation_instance._state = Mock()

        message_data = {
            "slack_message_id": "123456",
            "conversation": mock_conversation_instance,
            "text": "Test message",
            "timestamp": "1605000000.000000",
        }

        mocker.patch(
            "apps.slack.models.message.Message.objects.get",
            side_effect=Message.DoesNotExist,
        )
        patched_message_save = mocker.patch("apps.slack.models.message.Message.save")

        result = Message.update_data(message_data)

        assert result is not None
        assert isinstance(result, Message)
        assert result.slack_message_id == "123456"
        assert result.text == "Test message"
        assert result.is_thread is False
        assert result.timestamp == datetime.fromtimestamp(1605000000, tz=UTC)
        patched_message_save.assert_called_once()

    def test_update_data_existing_message(self, mocker):
        mock_conversation_instance = Mock(spec=Conversation)
        mock_conversation_instance._state = Mock()

        message_data = {
            "slack_message_id": "123456",
            "conversation": mock_conversation_instance,
            "text": "Updated message",
            "timestamp": "1605000000.000000",
        }

        mock_message_instance = Mock(spec=Message)
        mock_message_instance._state = Mock()
        mock_message_instance.slack_message_id = "123456"

        mocker.patch(
            "apps.slack.models.message.Message.objects.get",
            return_value=mock_message_instance,
        )

        result = Message.update_data(message_data)

        assert result is mock_message_instance
        assert result.text == "Updated message"
        assert result.is_thread is False
        result.save.assert_called_once()

    def test_update_data_no_save(self, mocker):
        mock_conversation_instance = Mock(spec=Conversation)
        mock_conversation_instance._state = Mock()

        message_data = {
            "slack_message_id": "123456",
            "conversation": mock_conversation_instance,
            "text": "Test message",
            "timestamp": "1605000000.000000",
        }

        mocker.patch(
            "apps.slack.models.message.Message.objects.get",
            side_effect=Message.DoesNotExist,
        )

        patched_save_method = mocker.patch("apps.slack.models.message.Message.save")

        result = Message.update_data(message_data, save=False)

        # Assertions:
        assert result is not None
        assert isinstance(result, Message)

        assert result.slack_message_id == "123456"
        assert result.text == "Test message"
        assert result.conversation == mock_conversation_instance
        assert result.is_thread is False
        assert result.timestamp == datetime.fromtimestamp(1605000000, tz=UTC)

        patched_save_method.assert_not_called()

    def test_update_data_with_thread_messages(self, mocker):
        mock_conversation_instance = Mock(spec=Conversation)
        mock_conversation_instance._state = Mock()

        message_data = {
            "slack_message_id": "123456",
            "conversation": mock_conversation_instance,
            "text": "Parent message",
            "thread_messages": [{"text": "Reply 1"}, {"text": "Reply 2"}, {"text": ""}],
            "timestamp": "1605000000.000000",
        }

        mocker.patch(
            "apps.slack.models.message.Message.objects.get",
            side_effect=Message.DoesNotExist,
        )
        patched_message_save = mocker.patch("apps.slack.models.message.Message.save")

        result = Message.update_data(message_data)

        assert result is not None
        assert isinstance(result, Message)
        assert result.slack_message_id == "123456"
        assert result.text == "Parent message\n\nReply 1\n\nReply 2"
        assert result.is_thread is True
        assert result.timestamp == datetime.fromtimestamp(1605000000, tz=UTC)
        patched_message_save.assert_called_once()

    def test_update_data_with_is_thread_flag(self, mocker):
        mock_conversation_instance = Mock(spec=Conversation)
        mock_conversation_instance._state = Mock()

        message_data = {
            "slack_message_id": "123456",
            "conversation": mock_conversation_instance,
            "text": "Thread message",
            "is_thread": True,
            "timestamp": "1605000000.000000",
        }

        mocker.patch(
            "apps.slack.models.message.Message.objects.get",
            side_effect=Message.DoesNotExist,
        )
        patched_message_save = mocker.patch("apps.slack.models.message.Message.save")

        result = Message.update_data(message_data)

        assert result is not None
        assert isinstance(result, Message)
        assert result.slack_message_id == "123456"
        assert result.text == "Thread message"
        assert result.is_thread is True
        patched_message_save.assert_called_once()

    def test_str_method(self):
        message = Message(text="Short message")
        assert str(message) == "Short message"

        long_text = "This is a very long message that should be truncated for display purposes"
        message = Message(text=long_text)
        expected = "This is a very long message that should be truncat..."
        assert str(message) == expected
