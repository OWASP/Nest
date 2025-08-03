from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from apps.slack.models.conversation import Conversation
from apps.slack.models.member import Member
from apps.slack.models.message import Message
from apps.slack.models.workspace import Workspace


class TestMessageModel:
    """Tests for the Message model."""

    def test_str_representation(self):
        message = Message(raw_data={"text": "This is the message text"})
        assert str(message) == "This is the message text"

        huddle_message = Message(raw_data={"subtype": "huddle_thread", "channel": "C123"})
        assert str(huddle_message) == "C123 huddle"

    def test_cleaned_text_property(self):
        message = Message()
        message.raw_data = {
            "text": "Hello <@U123> check this :smile: <https://example.com> and this :thumbs_up:"
        }
        expected_text = "Hello check this and this"
        assert message.cleaned_text == expected_text

        message.raw_data = {"text": "  Extra   whitespace  "}
        assert message.cleaned_text == "Extra whitespace"

    def test_url_property(self):
        workspace = Workspace(name="MyWorkspace")
        conversation = Conversation(workspace=workspace, slack_channel_id="C123")
        message = Message(conversation=conversation, slack_message_id="12345.67890")
        expected_url = "https://myworkspace.slack.com/archives/C123/p1234567890"
        assert message.url == expected_url

    def test_latest_reply_property(self):
        message = Message(conversation=Conversation())

        with patch.object(Message.objects, "filter") as mock_filter:
            _ = message.latest_reply

        mock_filter.assert_called_once_with(
            conversation=message.conversation, parent_message=message
        )
        mock_filter.return_value.order_by.assert_called_once_with("-created_at")
        mock_filter.return_value.order_by.return_value.first.assert_called_once()

    def test_from_slack_method(self):
        message = Message()
        conversation = Conversation()
        author = Member()
        parent = Message()

        slack_data = {
            "ts": "1672531200.000",  # 2023-01-01
            "reply_count": 5,
            "bot_id": "B123",
        }

        message.from_slack(slack_data, conversation, author, parent_message=parent)

        assert message.created_at == datetime(2023, 1, 1, tzinfo=UTC)
        assert message.has_replies is True
        assert message.is_bot is True
        assert message.raw_data == slack_data
        assert message.slack_message_id == "1672531200.000"
        assert message.author == author
        assert message.conversation == conversation
        assert message.parent_message == parent

    def test_update_data_creates_new_message(self):
        slack_data = {"ts": "12345.001"}
        conversation = Conversation()

        with (
            patch.object(Message, "save") as mock_save,
            patch.object(Message.objects, "get", side_effect=Message.DoesNotExist) as mock_get,
        ):
            message = Message.update_data(slack_data, conversation, save=True)

        mock_get.assert_called_once_with(slack_message_id="12345.001", conversation=conversation)
        mock_save.assert_called_once()
        assert isinstance(message, Message)
        assert message.slack_message_id == "12345.001"

    def test_update_data_updates_existing_message(self):
        slack_data = {"ts": "12345.001"}
        conversation = Conversation()
        mock_existing_message = MagicMock(spec=Message)

        with patch.object(Message.objects, "get", return_value=mock_existing_message) as mock_get:
            message = Message.update_data(slack_data, conversation, save=True)

        mock_get.assert_called_once()
        mock_existing_message.from_slack.assert_called_once()
        mock_existing_message.save.assert_called_once()
        assert message == mock_existing_message
