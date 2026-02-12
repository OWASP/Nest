"""Tests for message posted event handler."""

from unittest.mock import Mock, patch

import pytest

from apps.slack.events.message_posted import MessagePosted

TEST_BOT_TOKEN = "xoxb-test-token"  # noqa: S105


class TestMessagePosted:
    """Test cases for MessagePosted event handler."""

    @pytest.fixture
    def workspace_mock(self):
        """Mock workspace object."""
        workspace = Mock()
        workspace.slack_workspace_id = "T123456"
        workspace.bot_token = TEST_BOT_TOKEN
        return workspace

    @pytest.fixture
    def conversation_mock(self):
        """Mock conversation object."""
        conversation = Mock()
        conversation.slack_channel_id = "C123456"
        conversation.is_nest_bot_assistant_enabled = True
        return conversation

    @pytest.fixture
    def member_mock(self):
        """Mock member object."""
        member = Mock()
        member.slack_user_id = "U123456"
        member.name = "Test User"
        return member

    @pytest.fixture
    def message_handler(self):
        """Create MessagePosted handler instance."""
        return MessagePosted()

    def test_init(self, message_handler):
        """Test MessagePosted initialization."""
        assert message_handler.event_type == "message"
        assert message_handler.question_detector is not None

    def test_handle_event_ignores_subtype_messages(self, message_handler):
        """Test that messages with subtype are ignored."""
        event = {
            "subtype": "channel_join",
            "channel": "C123456",
            "user": "U123456",
            "text": "What is OWASP?",
            "ts": "1234567890.123456",
        }
        client = Mock()

        message_handler.handle_event(event, client)

        client.chat_postMessage.assert_not_called()

    def test_handle_event_ignores_bot_messages(self, message_handler):
        """Test that bot messages are ignored."""
        event = {
            "bot_id": "B123456",
            "channel": "C123456",
            "user": "U123456",
            "text": "What is OWASP?",
            "ts": "1234567890.123456",
        }
        client = Mock()

        message_handler.handle_event(event, client)

        client.chat_postMessage.assert_not_called()

    def test_handle_event_ignores_thread_messages(self, message_handler):
        """Test that thread messages are ignored."""
        event = {
            "thread_ts": "1234567890.123455",
            "channel": "C123456",
            "user": "U123456",
            "text": "What is OWASP?",
            "ts": "1234567890.123456",
        }
        client = Mock()

        with patch("apps.slack.events.message_posted.Message") as mock_message:
            mock_message.DoesNotExist = Exception
            mock_message.objects.get.side_effect = Exception("Message not found")

            message_handler.handle_event(event, client)

        client.chat_postMessage.assert_not_called()

    def test_handle_event_conversation_not_found(self, message_handler):
        """Test handling when conversation is not found."""
        event = {
            "channel": "C999999",
            "user": "U123456",
            "text": "What is OWASP?",
            "ts": "1234567890.123456",
        }

        client = Mock()
        client.auth_test.return_value = {"user_id": "U987654"}

        with patch("apps.slack.events.message_posted.Conversation") as mock_conversation:
            from apps.slack.models.conversation import Conversation  # noqa: PLC0415

            mock_conversation.DoesNotExist = Conversation.DoesNotExist
            mock_conversation.objects.get.side_effect = Conversation.DoesNotExist

            with patch.object(
                message_handler.question_detector,
                "is_owasp_question",
                return_value=True,
            ):
                message_handler.handle_event(event, client)

            mock_conversation.objects.get.assert_called_once_with(
                slack_channel_id="C999999",
                is_nest_bot_assistant_enabled=True,
            )

    def test_handle_event_assistant_disabled(self, message_handler, conversation_mock):
        """Test handling when assistant is disabled for conversation."""
        conversation_mock.is_nest_bot_assistant_enabled = False

        event = {
            "channel": "C123456",
            "user": "U123456",
            "text": "What is OWASP?",
            "ts": "1234567890.123456",
        }

        client = Mock()
        client.auth_test.return_value = {"user_id": "U987654"}

        with patch("apps.slack.events.message_posted.Conversation") as mock_conversation:
            from apps.slack.models.conversation import Conversation  # noqa: PLC0415

            mock_conversation.DoesNotExist = Conversation.DoesNotExist
            mock_conversation.objects.get.side_effect = Conversation.DoesNotExist

            with patch.object(
                message_handler.question_detector,
                "is_owasp_question",
                return_value=True,
            ):
                message_handler.handle_event(event, client)

            mock_conversation.objects.get.assert_called_once_with(
                slack_channel_id="C123456",
                is_nest_bot_assistant_enabled=True,
            )

    @patch("apps.slack.events.message_posted.django_rq")
    @patch("apps.slack.events.message_posted.Conversation")
    @patch("apps.slack.events.message_posted.Member")
    def test_handle_event_not_owasp_question(
        self,
        mock_member,
        mock_conversation,
        mock_django_rq,
        message_handler,
        conversation_mock,
        member_mock,
    ):
        """Test handling when message is not an OWASP question."""
        mock_conversation.objects.get.return_value = conversation_mock
        mock_member.objects.get.return_value = member_mock

        event = {
            "channel": "C123456",
            "user": "U123456",
            "text": "Hello world",
            "ts": "1234567890.123456",
        }

        client = Mock()
        client.auth_test.return_value = {"user_id": "U987654"}

        with patch.object(
            message_handler.question_detector,
            "is_owasp_question",
            return_value=False,
        ):
            message_handler.handle_event(event, client)

        mock_django_rq.get_queue.assert_not_called()

    @patch("apps.slack.events.message_posted.django_rq")
    @patch("apps.slack.events.message_posted.Message")
    @patch("apps.slack.events.message_posted.Conversation")
    @patch("apps.slack.events.message_posted.Member")
    def test_handle_event_successful_owasp_question(
        self,
        mock_member,
        mock_conversation,
        mock_message_model,
        mock_django_rq,
        message_handler,
        conversation_mock,
        member_mock,
    ):
        """Test successful handling of OWASP question."""
        mock_conversation.objects.get.return_value = conversation_mock
        mock_member.objects.get.return_value = member_mock

        event = {
            "channel": "C123456",
            "user": "U123456",
            "text": "What is OWASP?",
            "ts": "1234567890.123456",
        }

        mock_message = Mock()
        mock_message.id = 1
        mock_message_model.update_data.return_value = mock_message

        mock_queue = Mock()
        mock_django_rq.get_queue.return_value = mock_queue

        client = Mock()
        client.auth_test.return_value = {"user_id": "U987654"}

        with patch.object(
            message_handler.question_detector,
            "is_owasp_question",
            return_value=True,
        ):
            message_handler.handle_event(event, client)

        mock_message_model.update_data.assert_called_once_with(
            data=event, conversation=conversation_mock, author=member_mock, save=True
        )
        mock_django_rq.get_queue.assert_called_once_with("ai")
        mock_queue.enqueue_in.assert_called_once()

    def test_handle_event_member_not_found(self, message_handler, conversation_mock):
        """Test handling when member is not found."""
        event = {
            "channel": "C123456",
            "user": "U999999",
            "text": "What is OWASP?",
            "ts": "1234567890.123456",
        }

        client = Mock()
        client.users_info.return_value = {"user": {"id": "U999999", "name": "Test User"}}

        # Create a proper workspace mock
        workspace_mock = Mock()
        conversation_mock.workspace = workspace_mock

        with (
            patch("apps.slack.events.message_posted.Conversation") as mock_conversation,
            patch("apps.slack.events.message_posted.Member") as mock_member,
            patch("apps.slack.events.message_posted.Message") as mock_message_model,
        ):
            mock_conversation.objects.get.return_value = conversation_mock

            from apps.slack.models.member import Member  # noqa: PLC0415

            mock_member.DoesNotExist = Member.DoesNotExist
            mock_member.objects.get.side_effect = Member.DoesNotExist
            mock_member.update_data.return_value = Mock()

            mock_message = Mock()
            mock_message.id = 1
            mock_message_model.update_data.return_value = mock_message

            with (
                patch.object(
                    message_handler.question_detector,
                    "is_owasp_question",
                    return_value=True,
                ),
                patch("apps.slack.events.message_posted.django_rq") as mock_django_rq,
            ):
                mock_queue = Mock()
                mock_django_rq.get_queue.return_value = mock_queue

                message_handler.handle_event(event, client)

                mock_django_rq.get_queue.assert_called_once()

    def test_handle_event_empty_text(self, message_handler):
        """Test handling event with empty text."""
        event = {"channel": "C123456", "user": "U123456", "ts": "1234567890.123456"}

        client = Mock()
        client.auth_test.return_value = {"user_id": "U987654"}

        with patch("apps.slack.events.message_posted.Conversation") as mock_conversation:
            from apps.slack.models.conversation import Conversation  # noqa: PLC0415

            mock_conversation.DoesNotExist = Conversation.DoesNotExist
            mock_conversation.objects.get.side_effect = Conversation.DoesNotExist

            with patch.object(
                message_handler.question_detector,
                "is_owasp_question",
                return_value=False,
            ):
                message_handler.handle_event(event, client)
