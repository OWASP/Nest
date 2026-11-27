from datetime import UTC, datetime
from unittest.mock import Mock, PropertyMock, patch

import pytest
from django.utils import timezone

from apps.slack.models.conversation import METADATA_MAX_AGE, Conversation
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
        assert conversation.slack_metadata_synced_at is not None

    def test_str_method(self):
        """Test string representation for channels, DMs, and group chats."""
        workspace = Workspace(name="test-workspace")
        channel = Conversation(name="test-channel", workspace=workspace)
        dm = Conversation(
            is_im=True,
            name="",
            slack_channel_id="D123",
            workspace=workspace,
        )
        group_chat = Conversation(
            is_mpim=True,
            name="",
            slack_channel_id="G123",
            workspace=workspace,
        )
        unnamed = Conversation(name="", slack_channel_id="C123", workspace=workspace)

        assert str(channel) == "test-workspace #test-channel"
        assert str(dm) == "test-workspace DM (D123)"
        assert str(group_chat) == "test-workspace group chat (G123)"
        assert str(unnamed) == "test-workspace C123"

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

    def test_get_by_channel_id(self, mocker):
        """Lookup filters by channel id and workspace."""
        conversation = Mock()
        workspace = Workspace(slack_workspace_id="T1")
        manager = mocker.patch("apps.slack.models.conversation.Conversation.objects")
        manager.filter.return_value.first.return_value = conversation

        assert Conversation.get_by_channel_id("C123", workspace) is conversation
        manager.filter.assert_called_once_with(slack_channel_id="C123", workspace=workspace)

    def test_source_label_and_content_origin(self):
        """Test Reported From labels for IM, MPIM, named channels, and authors."""
        dm = Conversation(is_im=True, is_mpim=False, is_private=False)
        assert dm.source_label == "direct message"
        assert dm.content_origin() == "direct message"
        assert dm.content_origin("U1") == "direct message by <@U1>"
        assert dm.is_public_channel is False

        group = Conversation(is_im=False, is_mpim=True, is_private=False)
        assert group.source_label == "group chat"
        assert group.is_public_channel is False

        named = Conversation(
            is_channel=True,
            is_im=False,
            is_mpim=False,
            is_private=False,
            name="general",
            slack_channel_id="C123",
        )
        assert named.source_label == "#general"
        assert named.content_origin("U2") == "#general by <@U2>"
        assert named.is_public_channel is True

        unnamed = Conversation(
            is_im=False,
            is_mpim=False,
            is_private=False,
            name="",
            slack_channel_id="C123",
        )
        assert unnamed.source_label == "<#C123>"
        assert unnamed.is_public_channel is False

        group = Conversation(
            is_channel=False,
            is_group=True,
            is_im=False,
            is_mpim=False,
            is_private=False,
            name="",
            slack_channel_id="G123",
        )
        assert group.is_public_channel is False

        private = Conversation(
            is_channel=True,
            is_im=False,
            is_mpim=False,
            is_private=True,
            name="secret",
            slack_channel_id="C1",
        )
        assert private.is_public_channel is False

    def test_has_fresh_metadata(self):
        """Test freshness requires a recent slack_metadata_synced_at."""
        fresh = Conversation(slack_metadata_synced_at=timezone.now())
        stub = Conversation(slack_metadata_synced_at=None)
        stale = Conversation(
            slack_metadata_synced_at=timezone.now() - METADATA_MAX_AGE,
        )

        assert fresh.has_fresh_metadata is True
        assert fresh.has_slack_metadata is True
        assert stub.has_fresh_metadata is False
        assert stub.has_slack_metadata is False
        assert stale.has_fresh_metadata is False
        assert stale.has_slack_metadata is True

    def test_mark_direct_message_metadata(self, mocker):
        """Test D-prefixed ids are classified as non-private IMs without Slack API data."""
        conversation = Conversation(slack_channel_id="D123")
        save = mocker.patch.object(conversation, "save")

        assert conversation.mark_direct_message_metadata() is True
        assert conversation.is_im is True
        assert conversation.is_private is False
        assert conversation.is_channel is False
        assert conversation.is_group is False
        assert conversation.is_mpim is False
        assert conversation.slack_metadata_synced_at is not None
        save.assert_called_once()
        assert conversation.mark_direct_message_metadata() is True

        channel = Conversation(slack_channel_id="C123")
        assert channel.mark_direct_message_metadata() is False
        assert channel.slack_metadata_synced_at is None

    def test_get_or_create_returns_existing(self, mocker):
        """Test existing conversations are reused for content reporting."""
        workspace = Workspace(pk=1, slack_workspace_id="T1")
        conversation = Mock(workspace_id=1, workspace=workspace)
        manager = mocker.patch("apps.slack.models.conversation.Conversation.objects")
        manager.get_or_create.return_value = (conversation, False)

        assert Conversation.get_or_create(workspace, "C123") is conversation
        manager.get_or_create.assert_called_once()
        _, kwargs = manager.get_or_create.call_args
        assert kwargs["slack_channel_id"] == "C123"
        assert kwargs["defaults"]["workspace"] is workspace
        assert kwargs["defaults"]["is_channel"] is True

    def test_get_or_create_creates_im_for_d_channel(self, mocker):
        """Test a missing D... channel creates a minimal IM conversation row."""
        conversation = Mock()
        workspace = Workspace(pk=1, slack_workspace_id="T1")
        manager = mocker.patch("apps.slack.models.conversation.Conversation.objects")
        manager.get_or_create.return_value = (conversation, True)
        info = mocker.patch("apps.slack.models.conversation.logger.info")

        assert Conversation.get_or_create(workspace, "D999") is conversation
        _, kwargs = manager.get_or_create.call_args
        assert kwargs["defaults"]["is_im"] is True
        assert kwargs["defaults"]["is_channel"] is False
        assert kwargs["defaults"]["is_mpim"] is False
        info.assert_called_once()

    def test_get_or_create_creates_group_for_g_channel(self, mocker):
        """Test a missing G... channel creates a minimal group conversation row."""
        conversation = Mock()
        workspace = Workspace(pk=1, slack_workspace_id="T1")
        manager = mocker.patch("apps.slack.models.conversation.Conversation.objects")
        manager.get_or_create.return_value = (conversation, True)
        mocker.patch("apps.slack.models.conversation.logger.info")

        assert Conversation.get_or_create(workspace, "G999") is conversation
        _, kwargs = manager.get_or_create.call_args
        assert kwargs["defaults"]["is_group"] is True
        assert kwargs["defaults"]["is_mpim"] is False
        assert kwargs["defaults"]["is_channel"] is False
        assert "is_private" not in kwargs["defaults"]

    def test_get_or_create_rejects_workspace_mismatch(self, mocker):
        """Test existing conversations for another workspace are rejected."""
        other_workspace = Workspace(pk=2, slack_workspace_id="T2")
        conversation = Mock(workspace_id=2, workspace=other_workspace)
        workspace = Workspace(pk=1, slack_workspace_id="T1")
        manager = mocker.patch("apps.slack.models.conversation.Conversation.objects")
        manager.get_or_create.return_value = (conversation, False)

        with pytest.raises(ValueError, match="different Slack workspace"):
            Conversation.get_or_create(workspace, "C123")
