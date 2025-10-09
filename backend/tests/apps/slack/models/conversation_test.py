from datetime import UTC, datetime
from unittest.mock import Mock, patch

from apps.slack.models.conversation import Conversation
from apps.slack.models.workspace import Workspace


class TestConversationModel:
    def test_bulk_save(self):
        mock_conversations = [Mock(id=None), Mock(id=1)]
        with patch("apps.common.models.BulkSaveModel.bulk_save") as mock_bulk_save:
            Conversation.bulk_save(mock_conversations)
            mock_bulk_save.assert_called_once_with(Conversation, mock_conversations, fields=None)

    def test_update_data_new_conversation(self, mocker):
        # Setup conversation data from Slack API
        conversation_data = {
            "id": "C12345",
            "name": "general",
            "created": "1605000000",
            "is_private": False,
            "is_archived": False,
            "is_general": True,
            "topic": {"value": "General topic"},
            "purpose": {"value": "General purpose"},
            "creator": "U12345",
        }

        # Mock the DoesNotExist exception when getting conversation
        mocker.patch(
            "apps.slack.models.conversation.Conversation.objects.get",
            side_effect=Conversation.DoesNotExist,
        )

        # Mock the from_slack method
        mocker.patch.object(Conversation, "from_slack")

        # Mock the save method
        mocker.patch.object(Conversation, "save")

        # Call update_data
        result = Conversation.update_data(conversation_data, Workspace())

        # Assertions
        assert result is not None
        assert result.slack_channel_id == "C12345"
        assert result.from_slack.call_count == 1
        assert result.save.call_count == 1

    def test_update_data_existing_conversation(self, mocker):
        # Setup conversation data from Slack API
        conversation_data = {
            "id": "C12345",
            "name": "general",
            "created": "1605000000",
            "is_private": False,
            "is_archived": False,
            "is_general": True,
            "topic": {"value": "General topic"},
            "purpose": {"value": "General purpose"},
            "creator": "U12345",
        }

        # Create a mock conversation object
        mock_conversation = mocker.Mock(spec=Conversation)
        mock_conversation.slack_channel_id = "C12345"

        # Mock the objects.get to return the mock conversation
        mocker.patch(
            "apps.slack.models.conversation.Conversation.objects.get",
            return_value=mock_conversation,
        )

        # Call update_data
        result = Conversation.update_data(conversation_data, Workspace())

        # Assertions
        assert result is not None
        assert result.slack_channel_id == "C12345"
        assert result.from_slack.call_count == 1
        assert result.save.call_count == 1

    def test_update_data_no_save(self, mocker):
        # Setup conversation data
        conversation_data = {"id": "C12345", "name": "general"}

        # Mock Conversation.objects.get
        mocker.patch(
            "apps.slack.models.conversation.Conversation.objects.get",
            side_effect=Conversation.DoesNotExist,
        )

        # Mock the save method
        save_mock = mocker.patch.object(Conversation, "save")

        # Call update_data with save=False
        result = Conversation.update_data(conversation_data, Workspace(), save=False)

        # Assertions
        assert result is not None
        assert save_mock.call_count == 0

    def test_from_slack(self):
        # Create test data
        conversation_data = {
            "name": "general",
            "created": "1605000000",  # Unix timestamp
            "is_private": True,
            "is_archived": True,
            "is_general": True,
            "topic": {"value": "General topic"},
            "purpose": {"value": "General purpose"},
            "creator": "U12345",
        }

        # Create a conversation instance
        conversation = Conversation()

        # Call from_slack
        conversation.from_slack(conversation_data, Workspace())

        # Assertions
        assert conversation.name == "general"
        assert conversation.created_at == datetime.fromtimestamp(1605000000, tz=UTC)
        assert conversation.is_private
        assert conversation.is_archived
        assert conversation.is_general
        assert conversation.topic == "General topic"
        assert conversation.purpose == "General purpose"
        assert conversation.slack_creator_id == "U12345"

    def test_str_method(self):
        # Create a conversation with a name
        conversation = Conversation(
            name="test-channel", workspace=Workspace(name="test-workspace")
        )

        # Check __str__ returns the name
        assert str(conversation) == "test-workspace #test-channel"

    def test_add_to_context_first_message(self, mocker):
        """Test adding the first message to an empty conversation context."""
        conversation = Conversation(slack_channel_id="C12345")
        conversation.conversation_context = ""

        save_mock = mocker.patch.object(Conversation, "save")
        conversation.add_to_context("Hello, how are you?")

        assert conversation.conversation_context == "User: Hello, how are you?\n"
        save_mock.assert_called_once_with(update_fields=["conversation_context"])

    def test_add_to_context_with_bot_response(self, mocker):
        """Test adding a user message and bot response to context."""
        conversation = Conversation(slack_channel_id="C12345")
        conversation.conversation_context = "User: Hello\nBot: Hi there!\n"

        save_mock = mocker.patch.object(Conversation, "save")

        conversation.add_to_context(
            "What is OWASP?", "OWASP stands for Open Web Application Security Project."
        )

        expected_context = (
            "User: Hello\n"
            "Bot: Hi there!\n"
            "User: What is OWASP?\n"
            "Bot: OWASP stands for Open Web Application Security Project.\n"
        )
        assert conversation.conversation_context == expected_context
        save_mock.assert_called_once_with(update_fields=["conversation_context"])

    def test_add_to_context_empty_initial_context(self, mocker):
        """Test adding context when conversation_context is None."""
        conversation = Conversation(slack_channel_id="C12345")
        conversation.conversation_context = None

        save_mock = mocker.patch.object(Conversation, "save")

        conversation.add_to_context("First message", "First response")

        expected_context = "User: First message\nBot: First response\n"
        assert conversation.conversation_context == expected_context
        save_mock.assert_called_once_with(update_fields=["conversation_context"])

    def test_get_context_empty(self):
        """Test getting context when conversation_context is empty."""
        conversation = Conversation(slack_channel_id="C12345")
        conversation.conversation_context = ""

        result = conversation.get_context()

        assert result == ""

    def test_get_context_no_limit(self):
        """Test getting full context without limit."""
        conversation = Conversation(slack_channel_id="C12345")
        conversation.conversation_context = (
            "User: Message 1\n"
            "Bot: Response 1\n"
            "User: Message 2\n"
            "Bot: Response 2\n"
            "User: Message 3\n"
            "Bot: Response 3\n"
        )

        result = conversation.get_context()

        assert result == conversation.conversation_context

    def test_get_context_with_limit_below_threshold(self):
        """Test getting context with limit when total exchanges are below limit."""
        conversation = Conversation(slack_channel_id="C12345")
        conversation.conversation_context = (
            "User: Message 1\nBot: Response 1\nUser: Message 2\nBot: Response 2\n"
        )

        result = conversation.get_context(conversation_context_limit=3)

        assert result == conversation.conversation_context

    def test_get_context_with_limit_above_threshold(self):
        """Test getting context with limit when total exchanges exceed limit."""
        conversation = Conversation(slack_channel_id="C12345")
        conversation.conversation_context = (
            "User: Message 1\n"
            "Bot: Response 1\n"
            "User: Message 2\n"
            "Bot: Response 2\n"
            "User: Message 3\n"
            "Bot: Response 3\n"
            "User: Message 4\n"
            "Bot: Response 4\n"
        )

        result = conversation.get_context(conversation_context_limit=2)

        expected = "User: Message 3\nBot: Response 3\nUser: Message 4\nBot: Response 4"
        assert result == expected

    def test_get_context_none_context(self):
        """Test getting context when conversation_context is None."""
        conversation = Conversation(slack_channel_id="C12345")
        conversation.conversation_context = None

        result = conversation.get_context()

        assert result == ""

    def test_get_context_with_limit_exact_threshold(self):
        """Test getting context when exchanges exactly match the limit."""
        conversation = Conversation(slack_channel_id="C12345")
        conversation.conversation_context = (
            "User: Message 1\nBot: Response 1\nUser: Message 2\nBot: Response 2\n"
        )

        result = conversation.get_context(conversation_context_limit=2)

        assert result == conversation.conversation_context
