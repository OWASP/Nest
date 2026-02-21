from datetime import UTC, datetime
from unittest.mock import Mock, PropertyMock, patch

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

    def test_latest_message_property(self, mocker):
        """Test latest_message property returns the most recent message."""
        conversation = Conversation()
        mock_message = mocker.Mock()
        mock_queryset = mocker.Mock()
        mock_queryset.order_by.return_value.first.return_value = mock_message

        mocker.patch.object(
            Conversation, "messages", new_callable=PropertyMock, return_value=mock_queryset
        )

        result = conversation.latest_message

        mock_queryset.order_by.assert_called_once_with("-created_at")
        assert result == mock_message
