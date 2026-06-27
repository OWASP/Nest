"""Tests for BotInteraction model, reaction feedback handler, and message_auto_reply hook."""

from unittest.mock import Mock, patch

import pytest

from apps.slack.apps import SlackConfig
from apps.slack.events.reaction_added.bot_feedback import BotFeedback
from apps.slack.models import Conversation, Message
from apps.slack.models.bot_interaction import BotInteraction
from apps.slack.services.message_auto_reply import generate_ai_reply_if_unanswered

TEST_BOT_TOKEN = "xoxb-test-token"  # noqa: S105
REPLY_TS = "1234567890.999999"
CHANNEL_ID = "C123456"


class TestBotInteractionModel:
    """Unit tests for the BotInteraction model."""

    def test_str_no_reaction(self):
        """Return em-dash when no reaction recorded."""
        interaction = BotInteraction(
            channel_id="C123",
            user_id="U456",
            user_message="What is OWASP?",
            bot_response="OWASP is…",
            thumbs_up=None,
        )
        assert "—" in str(interaction)

    def test_str_thumbs_up(self):
        """Return 👍 for positive feedback."""
        interaction = BotInteraction(
            channel_id="C123",
            user_id="U456",
            user_message="What is OWASP?",
            bot_response="OWASP is…",
            thumbs_up=True,
        )
        assert "👍" in str(interaction)

    def test_str_thumbs_down(self):
        """Return 👎 for negative feedback."""
        interaction = BotInteraction(
            channel_id="C123",
            user_id="U456",
            user_message="What is OWASP?",
            bot_response="OWASP is…",
            thumbs_up=False,
        )
        assert "👎" in str(interaction)

    def test_str_truncates_long_message(self):
        """Truncate user_message to 50 chars in __str__."""
        long_message = "A" * 100
        interaction = BotInteraction(
            channel_id="C123",
            user_id="U456",
            user_message=long_message,
            bot_response="response",
            thumbs_up=None,
        )
        result = str(interaction)
        assert "A" * 50 in result

    def test_db_table_name(self):
        """Use correct db_table name."""
        assert BotInteraction._meta.db_table == "slack_bot_interactions"

    def test_thumbs_up_field_nullable(self):
        """Accept None for thumbs_up field."""
        field = BotInteraction._meta.get_field("thumbs_up")
        assert field.null is True
        assert field.blank is True

    def test_slack_reply_ts_default_blank(self):
        """Default slack_reply_ts to empty string."""
        interaction = BotInteraction(
            channel_id="C1", user_id="U1", user_message="msg", bot_response="resp"
        )
        assert interaction.slack_reply_ts == ""

    def test_tokens_used_default_zero(self):
        """Default tokens_used to 0."""
        interaction = BotInteraction(
            channel_id="C1", user_id="U1", user_message="msg", bot_response="resp"
        )
        assert interaction.tokens_used == 0

    def test_slack_reply_ts_has_db_index(self):
        """Index slack_reply_ts for fast reaction lookup."""
        field = BotInteraction._meta.get_field("slack_reply_ts")
        assert field.db_index is True


class TestBotFeedback:
    """Unit tests for the BotFeedback event handler."""

    @pytest.fixture
    def handler(self):
        """Create a BotFeedback instance."""
        return BotFeedback()

    @pytest.fixture
    def mock_interaction(self):
        """Create a mock BotInteraction instance."""
        interaction = Mock(spec=BotInteraction)
        interaction.pk = 1
        interaction.thumbs_up = None
        return interaction

    def _make_event(
        self, reaction="thumbsup", ts=REPLY_TS, item_type="message", channel=CHANNEL_ID
    ):
        return {
            "reaction": reaction,
            "item": {"type": item_type, "ts": ts, "channel": channel},
            "user": "U789",
        }

    @patch("apps.slack.events.reaction_added.bot_feedback.BotInteraction.objects.filter")
    def test_thumbs_up_sets_true(self, mock_filter, handler, mock_interaction):
        """Set thumbs_up=True on 👍 reaction."""
        mock_filter.return_value.order_by.return_value.first.return_value = mock_interaction

        handler.handle_event(self._make_event("thumbsup"), client=None)

        assert mock_interaction.thumbs_up is True
        mock_interaction.save.assert_called_once_with(
            update_fields=["thumbs_up", "nest_updated_at"]
        )

    @patch("apps.slack.events.reaction_added.bot_feedback.BotInteraction.objects.filter")
    def test_thumbs_down_sets_false(self, mock_filter, handler, mock_interaction):
        """Set thumbs_up=False on 👎 reaction."""
        mock_filter.return_value.order_by.return_value.first.return_value = mock_interaction

        handler.handle_event(self._make_event("thumbsdown"), client=None)

        assert mock_interaction.thumbs_up is False
        mock_interaction.save.assert_called_once_with(
            update_fields=["thumbs_up", "nest_updated_at"]
        )

    @patch("apps.slack.events.reaction_added.bot_feedback.BotInteraction.objects.filter")
    def test_unrelated_reaction_ignored(self, mock_filter, handler):
        """Ignore reactions other than 👍/👎."""
        handler.handle_event(self._make_event("heart"), client=None)
        mock_filter.assert_not_called()

    @patch("apps.slack.events.reaction_added.bot_feedback.BotInteraction.objects.filter")
    def test_non_message_item_type_ignored(self, mock_filter, handler):
        """Ignore reactions on non-message items."""
        handler.handle_event(self._make_event(item_type="file"), client=None)
        mock_filter.assert_not_called()

    @patch("apps.slack.events.reaction_added.bot_feedback.BotInteraction.objects.filter")
    def test_no_matching_interaction_ignored(self, mock_filter, handler):
        """Silently ignore reaction on a non-bot message."""
        mock_filter.return_value.order_by.return_value.first.return_value = None
        handler.handle_event(self._make_event("thumbsup"), client=None)

    @patch("apps.slack.events.reaction_added.bot_feedback.BotInteraction.objects.filter")
    def test_missing_ts_ignored(self, mock_filter, handler):
        """Ignore event with no ts on item."""
        event = {
            "reaction": "thumbsup",
            "item": {"type": "message", "channel": CHANNEL_ID},
            "user": "U1",
        }
        handler.handle_event(event, client=None)
        mock_filter.assert_not_called()

    @patch("apps.slack.events.reaction_added.bot_feedback.BotInteraction.objects.filter")
    def test_missing_channel_ignored(self, mock_filter, handler):
        """Ignore event with no channel on item."""
        event = {
            "reaction": "thumbsup",
            "item": {"type": "message", "ts": REPLY_TS},
            "user": "U1",
        }
        handler.handle_event(event, client=None)
        mock_filter.assert_not_called()

    def test_event_type(self, handler):
        """Register handler for reaction_added event type."""
        assert handler.event_type == "reaction_added"


class TestMessageAutoReplyLogging:
    """Tests for BotInteraction logging in generate_ai_reply_if_unanswered."""

    @pytest.fixture
    def mock_message(self):
        """Create a mock Message with conversation and raw_data."""
        conversation = Mock(spec=Conversation)
        conversation.slack_channel_id = CHANNEL_ID
        conversation.is_nest_bot_assistant_enabled = True
        message = Mock(spec=Message)
        message.id = 1
        message.slack_message_id = "1234567890.123456"
        message.text = "What is OWASP?"
        message.raw_data = {"user": "U789"}
        message.conversation = conversation
        return message

    @patch.object(SlackConfig, "app")
    @patch("apps.slack.services.message_auto_reply.BotInteraction.objects.create")
    @patch("apps.slack.services.message_auto_reply.Message.objects.get")
    @patch("apps.slack.services.message_auto_reply.process_ai_query")
    @patch("apps.slack.services.message_auto_reply.get_blocks")
    def test_bot_interaction_created_after_reply(
        self,
        mock_get_blocks,
        mock_process_ai_query,
        mock_message_get,
        mock_create,
        mock_app,
        mock_message,
    ):
        """Create BotInteraction row after successful chat_postMessage."""
        mock_message_get.return_value = mock_message
        mock_process_ai_query.return_value = "OWASP is a security community…"
        mock_get_blocks.return_value = [{"type": "section"}]
        mock_client = Mock()
        mock_app.client = mock_client
        mock_client.conversations_replies.return_value = {"messages": [{"reply_count": 0}]}
        mock_client.chat_postMessage.return_value = {"ts": REPLY_TS}

        generate_ai_reply_if_unanswered(mock_message.id)

        mock_create.assert_called_once_with(
            channel_id=CHANNEL_ID,
            user_id="U789",
            user_message=mock_message.text,
            bot_response="OWASP is a security community…",
            slack_reply_ts=REPLY_TS,
        )

    @patch.object(SlackConfig, "app")
    @patch("apps.slack.services.message_auto_reply.BotInteraction.objects.create")
    @patch("apps.slack.services.message_auto_reply.Message.objects.get")
    @patch("apps.slack.services.message_auto_reply.process_ai_query")
    def test_no_bot_interaction_when_no_ai_response(
        self, mock_process_ai_query, mock_message_get, mock_create, mock_app, mock_message
    ):
        """Skip BotInteraction creation when AI returns nothing."""
        mock_message_get.return_value = mock_message
        mock_process_ai_query.return_value = None
        mock_client = Mock()
        mock_app.client = mock_client
        mock_client.conversations_replies.return_value = {"messages": [{"reply_count": 0}]}

        generate_ai_reply_if_unanswered(mock_message.id)
        mock_create.assert_not_called()

    @patch.object(SlackConfig, "app")
    @patch("apps.slack.services.message_auto_reply.BotInteraction.objects.create")
    @patch("apps.slack.services.message_auto_reply.Message.objects.get")
    @patch("apps.slack.services.message_auto_reply.process_ai_query")
    def test_no_bot_interaction_when_already_replied(
        self, mock_process_ai_query, mock_message_get, mock_create, mock_app, mock_message
    ):
        """Skip BotInteraction creation when message already has human replies."""
        mock_message_get.return_value = mock_message
        mock_client = Mock()
        mock_app.client = mock_client
        mock_client.conversations_replies.return_value = {"messages": [{"reply_count": 2}]}

        generate_ai_reply_if_unanswered(mock_message.id)
        mock_process_ai_query.assert_not_called()
        mock_create.assert_not_called()

    @patch.object(SlackConfig, "app")
    @patch("apps.slack.services.message_auto_reply.BotInteraction.objects.create")
    @patch("apps.slack.services.message_auto_reply.Message.objects.get")
    @patch("apps.slack.services.message_auto_reply.process_ai_query")
    @patch("apps.slack.services.message_auto_reply.get_blocks")
    def test_bot_interaction_ts_fallback_when_response_missing_ts(
        self,
        mock_get_blocks,
        mock_process_ai_query,
        mock_message_get,
        mock_create,
        mock_app,
        mock_message,
    ):
        """Fall back to empty string for slack_reply_ts when response has no ts key."""
        mock_message_get.return_value = mock_message
        mock_process_ai_query.return_value = "OWASP answer"
        mock_get_blocks.return_value = [{"type": "section"}]
        mock_client = Mock()
        mock_app.client = mock_client
        mock_client.conversations_replies.return_value = {"messages": [{"reply_count": 0}]}
        mock_client.chat_postMessage.return_value = {"ok": True}  # no 'ts' key

        generate_ai_reply_if_unanswered(mock_message.id)
        _, kwargs = mock_create.call_args
        assert kwargs["slack_reply_ts"] == ""
