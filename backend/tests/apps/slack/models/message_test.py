from unittest.mock import Mock, patch

from apps.slack.models.conversation import Conversation
from apps.slack.models.member import Member
from apps.slack.models.message import Message


def create_model_mock(model_class):
    mock = Mock(spec=model_class)
    mock._state = Mock()
    mock.pk = 1
    return mock


class TestMessageModel:
    def test_bulk_save(self):
        mock_messages = [Mock(id=None), Mock(id=1)]
        with patch("apps.common.models.BulkSaveModel.bulk_save") as mock_bulk_save:
            Message.bulk_save(mock_messages)
            mock_bulk_save.assert_called_once_with(Message, mock_messages, fields=None)

    def test_update_data_new_message(self, mocker):
        mock_conversation = create_model_mock(Conversation)
        mock_author = create_model_mock(Member)

        message_data = {
            "ts": "123456.789",
            "text": "Test message",
        }

        mocker.patch(
            "apps.slack.models.message.Message.objects.get",
            side_effect=Message.DoesNotExist,
        )
        patched_message_save = mocker.patch("apps.slack.models.message.Message.save")

        with (
            patch.object(Message, "conversation", create=True),
            patch.object(Message, "author", create=True),
        ):
            result = Message.update_data(
                data=message_data, conversation=mock_conversation, author=mock_author, save=True
            )

            assert result is not None
            assert isinstance(result, Message)
            assert result.slack_message_id == "123456.789"
            assert result.conversation == mock_conversation
            assert result.author == mock_author
            patched_message_save.assert_called_once()

    def test_update_data_existing_message(self, mocker):
        mock_conversation = create_model_mock(Conversation)
        mock_author = create_model_mock(Member)

        message_data = {
            "ts": "123456.789",
            "text": "Updated message",
        }

        mock_message_instance = create_model_mock(Message)
        mock_message_instance.slack_message_id = "123456.789"

        mocker.patch(
            "apps.slack.models.message.Message.objects.get",
            return_value=mock_message_instance,
        )

        result = Message.update_data(
            data=message_data, conversation=mock_conversation, author=mock_author, save=True
        )

        assert result is mock_message_instance

        mock_message_instance.from_slack.assert_called_once_with(
            message_data,
            mock_conversation,
            mock_author,
            parent_message=None,
        )
        mock_message_instance.save.assert_called_once()

    def test_update_data_no_save(self, mocker):
        mock_conversation = create_model_mock(Conversation)
        mock_author = create_model_mock(Member)

        message_data = {
            "ts": "123456.789",
            "text": "Test message",
        }

        mocker.patch(
            "apps.slack.models.message.Message.objects.get",
            side_effect=Message.DoesNotExist,
        )

        patched_save_method = mocker.patch("apps.slack.models.message.Message.save")

        with (
            patch.object(Message, "conversation", create=True),
            patch.object(Message, "author", create=True),
        ):
            result = Message.update_data(
                data=message_data, conversation=mock_conversation, author=mock_author, save=False
            )

            assert result is not None
            assert isinstance(result, Message)
            assert result.slack_message_id == "123456.789"
            assert result.conversation == mock_conversation
            assert result.author == mock_author
            patched_save_method.assert_not_called()

    def test_update_data_with_thread_reply(self, mocker):
        mock_conversation = create_model_mock(Conversation)
        mock_author = create_model_mock(Member)
        mock_parent = create_model_mock(Message)

        message_data = {
            "ts": "123456.789",
            "text": "Reply message",
        }

        mocker.patch(
            "apps.slack.models.message.Message.objects.get",
            side_effect=Message.DoesNotExist,
        )
        patched_message_save = mocker.patch("apps.slack.models.message.Message.save")

        with (
            patch.object(Message, "conversation", create=True),
            patch.object(Message, "author", create=True),
            patch.object(Message, "parent_message", create=True),
        ):
            result = Message.update_data(
                data=message_data,
                conversation=mock_conversation,
                author=mock_author,
                parent_message=mock_parent,
                save=True,
            )

            assert result is not None
            assert isinstance(result, Message)
            assert result.slack_message_id == "123456.789"
            assert result.parent_message == mock_parent
            assert not result.has_replies
            patched_message_save.assert_called_once()

    def test_update_data_with_thread_parent(self, mocker):
        mock_conversation = create_model_mock(Conversation)
        mock_author = create_model_mock(Member)

        message_data = {
            "ts": "123456.789",
            "text": "Parent message",
            "reply_count": 2,
        }

        mocker.patch(
            "apps.slack.models.message.Message.objects.get",
            side_effect=Message.DoesNotExist,
        )
        patched_message_save = mocker.patch("apps.slack.models.message.Message.save")

        with (
            patch.object(Message, "conversation", create=True),
            patch.object(Message, "author", create=True),
        ):
            result = Message.update_data(
                data=message_data, conversation=mock_conversation, author=mock_author, save=True
            )

            assert result is not None
            assert isinstance(result, Message)
            assert result.slack_message_id == "123456.789"
            assert result.has_replies
            patched_message_save.assert_called_once()

    def test_str_method(self):
        message = Message(raw_data={"text": "Short message"})
        assert str(message) == "Short message"
