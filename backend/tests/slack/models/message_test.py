from datetime import UTC, datetime
from unittest.mock import Mock, patch

from apps.slack.models.conversation import Conversation
from apps.slack.models.message import Message

CONSTANT_2 = 2


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
            "reply_count": 0,
            "thread_timestamp": "123456.000",
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
        assert result.reply_count == 0
        assert result.thread_timestamp == "123456.000"
        assert result.timestamp == datetime.fromtimestamp(1605000000, tz=UTC)
        patched_message_save.assert_called_once()

    def test_update_data_existing_message(self, mocker):
        mock_conversation_instance = Mock(spec=Conversation)
        mock_conversation_instance._state = Mock()

        message_data = {
            "slack_message_id": "123456",
            "conversation": mock_conversation_instance,
            "text": "Updated message",
            "reply_count": 2,
            "thread_timestamp": "123456.000",
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
        assert result.reply_count == CONSTANT_2
        result.save.assert_called_once()

    def test_update_data_no_save(self, mocker):
        mock_conversation_instance = Mock(spec=Conversation)
        mock_conversation_instance._state = Mock()

        message_data = {
            "slack_message_id": "123456",
            "conversation": mock_conversation_instance,
            "text": "Test message",
            "reply_count": 0,
            "thread_timestamp": "123456.000",
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
        assert result.reply_count == 0
        assert result.thread_timestamp == "123456.000"
        assert result.timestamp == datetime.fromtimestamp(1605000000, tz=UTC)

        patched_save_method.assert_not_called()

    def test_is_thread_parent(self):
        message = Message(reply_count=1)
        assert message.is_thread_parent is True

        message = Message(reply_count=0)
        assert message.is_thread_parent is False

    def test_is_thread_reply(self):
        message = Message(thread_timestamp="123456.000", slack_message_id="123457.000")
        assert message.is_thread_reply is True

        message = Message(thread_timestamp="123456.000", slack_message_id="123456.000")
        assert message.is_thread_reply is False

        message = Message(thread_timestamp="")
        assert message.is_thread_reply is False

    def test_get_thread_messages(self, mocker):
        mock_conversation = Mock(spec=Conversation)
        mock_conversation._state = Mock()

        mock_parent = Mock(spec=Message)
        mock_parent._state = Mock()
        mock_parent.conversation = mock_conversation
        mock_parent.slack_message_id = "123456.000"
        mock_parent.thread_timestamp = "123456.000"

        mock_parent.get_thread_messages = Message.get_thread_messages.__get__(mock_parent, Message)

        mock_thread_messages_list = [
            Mock(spec=Message, _state=Mock()),
            Mock(spec=Message, _state=Mock()),
        ]

        filter_chain_mock = Mock()
        filter_chain_mock.order_by.return_value = mock_thread_messages_list

        patched_filter_method = mocker.patch(
            "apps.slack.models.message.Message.objects.filter",
            return_value=filter_chain_mock,
        )

        result = mock_parent.get_thread_messages()

        patched_filter_method.assert_called_once_with(
            conversation=mock_conversation,
            thread_timestamp="123456.000",
        )
        filter_chain_mock.order_by.assert_called_once()
        assert result == mock_thread_messages_list

    def test_str_method(self):
        message = Message(text="Short message")
        assert str(message) == "Short message"

        long_text = "This is a very long message that should be truncated for display purposes"
        message = Message(text=long_text)
        expected = "This is a very long message that should be truncat..."
        assert str(message) == expected
