from unittest.mock import MagicMock, Mock, patch

from slack_sdk.errors import SlackApiError, SlackClientError, SlackRequestError

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

    def test_get_author_id(self):
        """Test author id extraction from Slack message payloads."""
        assert Message.get_author_id({"user": "U123"}) == "U123"
        assert Message.get_author_id({"user": ""}) is None
        assert Message.get_author_id({"user": 7}) is None
        assert Message.get_author_id({}) is None

    def test_compact_ts_to_message_ts(self):
        """Test permalink compact timestamps convert to message ts."""
        assert Message.compact_ts_to_message_ts("1700000000123456") == "1700000000.123456"
        assert Message.compact_ts_to_message_ts("123") == ""

    def test_find_in_api_list(self):
        """Test message lookup within a Slack API messages list."""
        messages = [{"ts": "1.0", "text": "a"}, {"ts": "2.0", "text": "b"}]
        assert Message.find_in_api_list(messages, "2.0") == {"ts": "2.0", "text": "b"}
        assert Message.find_in_api_list(messages, "3.0") is None

    def test_unwrap_slack_link(self):
        """Test Slack mrkdwn link unwrapping."""
        assert (
            Message.unwrap_slack_link("<https://example.com/path|label>")
            == "https://example.com/path"
        )
        assert Message.unwrap_slack_link("https://example.com") == "https://example.com"
        assert (
            Message.unwrap_slack_link("<https://example.com/path|label with spaces> trailing")
            == "https://example.com/path"
        )
        assert (
            Message.unwrap_slack_link("https://example.com/path trailing")
            == "https://example.com/path"
        )

    def test_parse_permalink_rejects_invalid_thread_ts(self):
        """Test invalid thread_ts query values are dropped."""
        assert Message.parse_permalink(
            "https://owasp.slack.com/archives/C123/p1700000000123456?thread_ts=bad"
        ) == ("C123", "1700000000.123456", None)

    def test_get_raw_data_by_channel_and_ts(self, mocker):
        """Test stored raw_data is returned when present."""
        existing = Mock(raw_data={"ts": "1.0", "text": "hi"})
        manager = mocker.patch("apps.slack.models.message.Message.objects")
        manager.filter.return_value.only.return_value.first.return_value = existing

        assert Message.get_raw_data_by_channel_and_ts("C1", "1.0") == {
            "ts": "1.0",
            "text": "hi",
        }

    def test_get_raw_data_by_channel_and_ts_missing(self, mocker):
        """Test missing or empty stored raw_data returns None."""
        manager = mocker.patch("apps.slack.models.message.Message.objects")
        manager.filter.return_value.only.return_value.first.return_value = Mock(raw_data={})

        assert Message.get_raw_data_by_channel_and_ts("C1", "1.0") is None

    def test_load_payload_prefers_database(self, mocker):
        """Test load_payload returns Nest storage before calling Slack."""
        mocker.patch(
            "apps.slack.models.message.Message.get_raw_data_by_channel_and_ts",
            return_value={"ts": "1.0"},
        )
        fetch = mocker.patch("apps.slack.models.message.Message.fetch_payload")

        assert Message.load_payload(Mock(), "C1", "1.0") == {"ts": "1.0"}
        fetch.assert_not_called()

    def test_load_payload_falls_back_to_fetch(self, mocker):
        """Test load_payload fetches from Slack when Nest has no row."""
        mocker.patch(
            "apps.slack.models.message.Message.get_raw_data_by_channel_and_ts",
            return_value=None,
        )
        fetch = mocker.patch(
            "apps.slack.models.message.Message.fetch_payload",
            return_value={"ts": "1.0", "text": "from slack"},
        )
        client = Mock()

        assert Message.load_payload(client, "C1", "1.0", "0.9") == {
            "ts": "1.0",
            "text": "from slack",
        }
        fetch.assert_called_once_with(client, "C1", "1.0", "0.9")

    def test_fetch_payload_from_history(self):
        """Test fetch_payload returns a channel history match."""
        client = Mock()
        client.conversations_history.return_value = {
            "messages": [{"ts": "1.0", "text": "hi"}],
        }

        assert Message.fetch_payload(client, "C1", "1.0") == {"ts": "1.0", "text": "hi"}
        client.conversations_replies.assert_not_called()

    def test_fetch_payload_visibility_error(self):
        """Test fetch_payload returns None for not-visible channels."""
        client = Mock()
        client.conversations_history.side_effect = SlackApiError(
            message="missing",
            response={"ok": False, "error": "not_in_channel"},
        )

        assert Message.fetch_payload(client, "C1", "1.0") is None

    def test_fetch_payload_other_api_error(self):
        """Test fetch_payload returns None for unexpected Slack API errors."""
        client = Mock()
        client.conversations_history.side_effect = SlackApiError(
            message="fail",
            response={"ok": False, "error": "fatal_error"},
        )

        assert Message.fetch_payload(client, "C1", "1.0") is None

    def test_fetch_payload_request_error(self):
        """Test fetch_payload returns None on Slack transport failures."""
        client = Mock()
        client.conversations_history.side_effect = SlackRequestError("timeout")

        assert Message.fetch_payload(client, "C1", "1.0") is None

    def test_fetch_permalink_success(self):
        """Test fetch_permalink returns the Slack permalink."""
        client = Mock()
        client.chat_getPermalink.return_value = {"permalink": "https://example.slack.com/p"}

        assert Message.fetch_permalink(client, "C1", "1.0") == "https://example.slack.com/p"

    def test_fetch_payload_uses_targeted_thread_lookup(self):
        """Test fetch_payload loads a reply via oldest/latest on conversations.replies."""
        client = Mock()
        client.conversations_replies.return_value = {
            "messages": [{"ts": "1.1", "text": "reply"}],
        }

        assert Message.fetch_payload(client, "C1", "1.1", "1.0") == {
            "ts": "1.1",
            "text": "reply",
        }
        client.conversations_replies.assert_called_once_with(
            channel="C1",
            ts="1.0",
            latest="1.1",
            oldest="1.1",
            inclusive=True,
            limit=1,
        )
        client.conversations_history.assert_not_called()

    def test_fetch_payload_thread_miss_falls_back_to_history(self):
        """Test fetch_payload tries history when the targeted replies call misses."""
        client = Mock()
        client.conversations_replies.return_value = {"messages": []}
        client.conversations_history.return_value = {
            "messages": [{"ts": "1.1", "text": "channel message"}],
        }

        assert Message.fetch_payload(client, "C1", "1.1", "1.0") == {
            "ts": "1.1",
            "text": "channel message",
        }
        client.conversations_replies.assert_called_once()
        client.conversations_history.assert_called_once()

    def test_fetch_payload_returns_none_when_missing(self):
        """Test fetch_payload returns None when Slack has no matching message."""
        client = Mock()
        client.conversations_history.return_value = {"messages": []}

        assert Message.fetch_payload(client, "C1", "1.0") is None

    def test_fetch_payload_returns_none_when_thread_and_history_miss(self):
        """Test fetch_payload returns None without broad thread pagination."""
        client = Mock()
        client.conversations_replies.return_value = {"messages": []}
        client.conversations_history.return_value = {"messages": []}

        assert Message.fetch_payload(client, "C1", "1.1", "1.0") is None
        client.conversations_replies.assert_called_once()
        client.conversations_history.assert_called_once()

    def test_fetch_permalink_client_error(self):
        """Test fetch_permalink returns empty string on Slack client failures."""
        client = Mock()
        client.chat_getPermalink.side_effect = SlackClientError("boom")

        assert Message.fetch_permalink(client, "C1", "1.0") == ""

    def test_parse_permalink_rejects_empty_compact_ts(self):
        """Test too-short compact timestamps are rejected."""
        assert Message.parse_permalink("https://owasp.slack.com/archives/C123/p123") is None

    def test_parse_permalink_rejects_empty_input(self):
        """Test empty permalink input returns None."""
        assert Message.parse_permalink("") is None
        assert Message.parse_permalink("   ") is None

    def test_unwrap_slack_link_without_label(self):
        """Test Slack links without labels unwrap to the URL."""
        assert (
            Message.unwrap_slack_link("<https://example.com/path>") == "https://example.com/path"
        )
