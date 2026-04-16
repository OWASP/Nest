from unittest.mock import MagicMock, Mock, patch

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

    def test_str_method_huddle_thread(self):
        """Test __str__ with huddle_thread subtype."""
        message = Message(
            raw_data={"text": "Ignored", "subtype": "huddle_thread", "channel": "C123"}
        )
        assert str(message) == "C123 huddle"

    def test_cleaned_text_empty(self):
        """Test cleaned_text returns empty string when text is empty."""
        message = Message(raw_data={"text": ""})
        assert message.cleaned_text == ""

    def test_cleaned_text_removes_emojis(self):
        """Test cleaned_text removes emojis."""
        message = Message(raw_data={"text": "Hello 👋 World"})
        result = message.cleaned_text
        assert "👋" not in result
        assert "Hello" in result
        assert "World" in result

    def test_cleaned_text_removes_user_mentions(self):
        """Test cleaned_text removes user mentions."""
        message = Message(raw_data={"text": "Hey <@U12345678> check this"})
        result = message.cleaned_text
        assert "<@U12345678>" not in result
        assert "Hey" in result
        assert "check this" in result

    def test_cleaned_text_removes_links(self):
        """Test cleaned_text removes links."""
        message = Message(raw_data={"text": "Check <https://example.com|link>"})
        result = message.cleaned_text
        assert "https://example.com" not in result

    def test_cleaned_text_removes_emoji_aliases(self):
        """Test cleaned_text removes emoji aliases."""
        message = Message(raw_data={"text": "Great :smile: work"})
        result = message.cleaned_text
        assert ":smile:" not in result

    def test_cleaned_text_normalizes_whitespace(self):
        """Test cleaned_text normalizes multiple whitespaces."""
        message = Message(raw_data={"text": "Hello    World"})
        result = message.cleaned_text
        assert "    " not in result

    def test_subtype_property(self):
        """Test subtype property returns subtype from raw_data."""
        message = Message(raw_data={"text": "test", "subtype": "bot_message"})
        assert message.subtype == "bot_message"

    def test_subtype_property_none(self):
        """Test subtype property returns None when not present."""
        message = Message(raw_data={"text": "test"})
        assert message.subtype is None

    def test_text_property(self):
        """Test text property returns text from raw_data."""
        message = Message(raw_data={"text": "Hello world"})
        assert message.text == "Hello world"

    def test_text_property_default(self):
        """Test text property returns empty string when no text."""
        message = Message(raw_data={})
        assert message.text == ""

    def test_ts_property(self):
        """Test ts property returns timestamp from raw_data."""
        message = Message(raw_data={"ts": "1234567890.123456", "text": ""})
        assert message.ts == "1234567890.123456"

    def test_url_property(self):
        """Test url property returns correct Slack message URL."""
        mock_message = MagicMock(spec=Message)
        mock_message.conversation.workspace.name = "TestWorkspace"
        mock_message.conversation.slack_channel_id = "C12345"
        mock_message.slack_message_id = "1234567890.123456"
        result = Message.url.fget(mock_message)

        expected_url = "https://testworkspace.slack.com/archives/C12345/p1234567890123456"
        assert result == expected_url

    def test_latest_reply_property(self, mocker):
        """Test latest_reply property returns most recent reply."""
        mock_conversation = create_model_mock(Conversation)

        message = Message(raw_data={"text": "Parent"})
        message.conversation = mock_conversation

        mock_reply = create_model_mock(Message)
        mock_reply.raw_data = {"text": "Latest reply"}

        mock_filter = mocker.patch.object(Message.objects, "filter")
        mock_filter.return_value.order_by.return_value.first.return_value = mock_reply

        result = message.latest_reply

        assert result == mock_reply
        mock_filter.assert_called_once()
