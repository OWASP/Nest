"""Tests for BotInteraction model, reaction feedback handler, and message_auto_reply hook."""

from unittest.mock import Mock, call, patch

import pytest

from apps.slack.apps import SlackConfig
from apps.slack.events.reaction_added.bot_feedback import BotFeedback
from apps.slack.models import Conversation, Message, Workspace
from apps.slack.models.bot_interaction import BotInteraction
from apps.slack.services.message_auto_reply import generate_ai_reply_if_unanswered

TEST_BOT_TOKEN = "xoxb-test-token"  # noqa: S105
REPLY_TS = "1234567890.999999"


# ---------------------------------------------------------------------------
# BotInteraction model
# ---------------------------------------------------------------------------


class TestBotInteractionModel:
    """Unit tests for the BotInteraction model."""

    def test_str_no_reaction(self):
        """__str__ shows em-dash when no reaction recorded."""
        interaction = BotInteraction(
            channel_id="C123",
            user_id="U456",
            user_message="What is OWASP?",
            bot_response="OWASP is…",
            thumbs_up=None,
        )
        assert "—" in str(interaction)

    def test_str_thumbs_up(self):
        """__str__ shows 👍 for positive feedback."""
        interaction = BotInteraction(
            channel_id="C123",
            user_id="U456",
            user_message="What is OWASP?",
            bot_response="OWASP is…",
            thumbs_up=True,
        )
        assert "👍" in str(interaction)

    def test_str_thumbs_down(self):
        """__str__ shows 👎 for negative feedback."""
        interaction = BotInteraction(
            channel_id="C123",
            user_id="U456",
            user_message="What is OWASP?",
            bot_response="OWASP is…",
            thumbs_up=False,
        )
        assert "👎" in str(interaction)

    def test_str_truncates_long_message(self):
        """__str__ truncates user_message to 50 chars."""
        long_message = "A" * 100
        interaction = BotInteraction(
            channel_id="C123",
            user_id="U456",
            user_message=long_message,
            bot_response="response",
            thumbs_up=None,
        )
        result = str(interaction)
        # repr of 50 chars + quotes should appear
        assert "A" * 50 in result

    def test_db_table_name(self):
        """Model uses correct db_table."""
        assert BotInteraction._meta.db_table == "slack_bot_interactions"

    def test_thumbs_up_field_nullable(self):
        """thumbs_up field accepts None."""
        field = BotInteraction._meta.get_field("thumbs_up")
        assert field.null is True
        assert field.blank is True

    def test_slack_reply_ts_default_blank(self):
        """slack_reply_ts defaults to empty string."""
        interaction = BotInteraction(
            channel_id="C1",
            user_id="U1",
            user_message="msg",
            bot_response="resp",
        )
        assert interaction.slack_reply_ts == ""

    def test_tokens_used_default_zero(self):
        """tokens_used defaults to 0."""
        interaction = BotInteraction(
            channel_id="C1",
            user_id="U1",
            user_message="msg",
            bot_response="resp",
        )
        assert interaction.tokens_used == 0


# ---------------------------------------------------------------------------
# BotFeedback reaction_added handler
# ---------------------------------------------------------------------------


class TestBotFeedback:
    """Unit tests for the BotFeedback event handler."""

    @pytest.fixture
    def handler(self):
        """Create a BotFeedback instance."""
        return BotFeedback()

    @pytest.fixture
    def mock_interaction(self):
        """Mock BotInteraction instance."""
        interaction = Mock(spec=BotInteraction)
        interaction.pk = 1
        interaction.thumbs_up = None
        return interaction

    def _make_event(self, reaction="thumbsup", ts=REPLY_TS, item_type="message"):
        return {
            "reaction": reaction,
            "item": {"type": item_type, "ts": ts},
            "user": "U789",
        }

    @patch("apps.slack.events.reaction_added.bot_feedback.BotInteraction.objects.get")
    def test_thumbs_up_sets_true(self, mock_get, handler, mock_interaction):
        """👍 reaction sets thumbs_up=True."""
        mock_get.return_value = mock_interaction

        handler.handle_event(self._make_event("thumbsup"), client=None)

        assert mock_interaction.thumbs_up is True
        mock_interaction.save.assert_called_once_with(
            update_fields=["thumbs_up", "nest_updated_at"]
        )

    @patch("apps.slack.events.reaction_added.bot_feedback.BotInteraction.objects.get")
    def test_thumbs_down_sets_false(self, mock_get, handler, mock_interaction):
        """👎 reaction sets thumbs_up=False."""
        mock_get.return_value = mock_interaction

        handler.handle_event(self._make_event("thumbsdown"), client=None)

        assert mock_interaction.thumbs_up is False
        mock_interaction.save.assert_called_once()

    @patch("apps.slack.events.reaction_added.bot_feedback.BotInteraction.objects.get")
    def test_unrelated_reaction_ignored(self, mock_get, handler):
        """Reactions other than 👍/👎 are silently ignored."""
        handler.handle_event(self._make_event("heart"), client=None)
        mock_get.assert_not_called()

    @patch("apps.slack.events.reaction_added.bot_feedback.BotInteraction.objects.get")
    def test_non_message_item_type_ignored(self, mock_get, handler):
        """Reactions on non-message items (e.g. files) are ignored."""
        handler.handle_event(self._make_event(item_type="file"), client=None)
        mock_get.assert_not_called()

    @patch("apps.slack.events.reaction_added.bot_feedback.BotInteraction.objects.get")
    def test_no_matching_interaction_ignored(self, mock_get, handler):
        """Reaction on a non-bot message is silently ignored."""
        mock_get.side_effect = BotInteraction.DoesNotExist()

        # Should not raise.
        handler.handle_event(self._make_event("thumbsup"), client=None)

    @patch("apps.slack.events.reaction_added.bot_feedback.BotInteraction.objects.get")
    def test_missing_ts_ignored(self, mock_get, handler):
        """Event with no ts on item is ignored."""
        event = {"reaction": "thumbsup", "item": {"type": "message"}, "user": "U1"}
        handler.handle_event(event, client=None)
        mock_get.assert_not_called()

    def test_event_type(self, handler):
        """Handler is registered for the correct event type."""
        assert handler.event_type == "reaction_added"


# ---------------------------------------------------------------------------
# message_auto_reply — BotInteraction logging hook
# ---------------------------------------------------------------------------


class TestMessageAutoReplyLogging:
    """Tests for the BotInteraction logging added to generate_ai_reply_if_unanswered."""

    @pytest.fixture
    def mock_workspace(self):
        workspace = Mock(spec=Workspace)
        workspace.slack_workspace_id = "T123456"
        workspace.bot_token = TEST_BOT_TOKEN
        return workspace

    @pytest.fixture
    def mock_conversation(self, mock_workspace):
        conversation = Mock(spec=Conversation)
        conversation.slack_channel_id = "C123456"
        conversation.workspace = mock_workspace
        conversation.is_nest_bot_assistant_enabled = True
        return conversation

    @pytest.fixture
    def mock_message(self, mock_conversation):
        message = Mock(spec=Message)
        message.id = 1
        message.slack_message_id = "1234567890.123456"
        message.text = "What is OWASP?"
        message.raw_data = {"user": "U789"}
        message.conversation = mock_conversation
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
        """BotInteraction row is created after a successful chat_postMessage."""
        mock_message_get.return_value = mock_message
        mock_process_ai_query.return_value = "OWASP is a security community…"
        mock_get_blocks.return_value = [{"type": "section"}]

        mock_client = Mock()
        mock_app.client = mock_client
        mock_client.conversations_replies.return_value = {"messages": [{"reply_count": 0}]}
        mock_client.chat_postMessage.return_value = {"ts": REPLY_TS}

        generate_ai_reply_if_unanswered(mock_message.id)

        mock_create.assert_called_once_with(
            channel_id=mock_message.conversation.slack_channel_id,
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
        self,
        mock_process_ai_query,
        mock_message_get,
        mock_create,
        mock_app,
        mock_message,
    ):
        """BotInteraction is NOT created when the AI returns nothing."""
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
        self,
        mock_process_ai_query,
        mock_message_get,
        mock_create,
        mock_app,
        mock_message,
    ):
        """BotInteraction is NOT created when message already has human replies."""
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
        """slack_reply_ts falls back to empty string if response has no ts."""
        mock_message_get.return_value = mock_message
        mock_process_ai_query.return_value = "OWASP answer"
        mock_get_blocks.return_value = [{"type": "section"}]
        mock_client = Mock()
        mock_app.client = mock_client
        mock_client.conversations_replies.return_value = {"messages": [{"reply_count": 0}]}
        mock_client.chat_postMessage.return_value = {}  # no 'ts' key

        generate_ai_reply_if_unanswered(mock_message.id)

        _, kwargs = mock_create.call_args
        assert kwargs["slack_reply_ts"] == ""