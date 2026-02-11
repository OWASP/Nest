"""Tests for EntityChannel admin configuration."""

from unittest.mock import MagicMock, patch

import pytest
from django.contrib.admin.sites import AdminSite

from apps.owasp.admin.entity_channel import (
    EntityChannelAdmin,
    mark_as_reviewed,
)
from apps.owasp.models import EntityChannel


class TestMarkAsReviewedAction:
    """Tests for mark_as_reviewed admin action."""

    def test_mark_as_reviewed(self, mocker):
        """Test marking selected EntityChannels as reviewed."""
        mock_request = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.update.return_value = 3

        mock_messages = mocker.patch("apps.owasp.admin.entity_channel.messages")

        mark_as_reviewed(None, mock_request, mock_queryset)

        mock_queryset.update.assert_called_once_with(is_reviewed=True)
        mock_messages.success.assert_called_once()


class TestEntityChannelAdmin:
    """Tests for EntityChannelAdmin."""

    target_module = "apps.owasp.admin.entity_channel"

    @pytest.fixture
    def admin_instance(self):
        """Create admin instance."""
        site = AdminSite()
        return EntityChannelAdmin(EntityChannel, site)

    def test_channel_search_display_with_conversation(self, admin_instance, mocker):
        """Test channel_search_display returns channel name for conversations."""
        mock_conversation = mocker.patch(f"{self.target_module}.Conversation")
        mock_conv_instance = MagicMock()
        mock_conv_instance.name = "general"
        mock_conversation.objects.get.return_value = mock_conv_instance

        mock_channel_type = MagicMock()
        mock_channel_type.model = "conversation"

        obj = MagicMock()
        obj.channel_id = 123
        obj.channel_type = mock_channel_type

        result = admin_instance.channel_search_display(obj)

        assert result == "#general"

    def test_channel_search_display_conversation_not_found(self, admin_instance, mocker):
        """Test channel_search_display when conversation doesn't exist."""
        from apps.slack.models import Conversation

        mock_conversation = mocker.patch(f"{self.target_module}.Conversation")
        mock_conversation.DoesNotExist = Conversation.DoesNotExist
        mock_conversation.objects.get.side_effect = Conversation.DoesNotExist

        mock_channel_type = MagicMock()
        mock_channel_type.model = "conversation"

        obj = MagicMock()
        obj.channel_id = 999
        obj.channel_type = mock_channel_type

        result = admin_instance.channel_search_display(obj)

        assert "999" in result
        assert "not found" in result

    def test_channel_search_display_no_channel_id(self, admin_instance):
        """Test channel_search_display returns dash when no channel_id."""
        obj = MagicMock()
        obj.channel_id = None
        obj.channel_type = None

        result = admin_instance.channel_search_display(obj)

        assert result == "-"

    def test_channel_search_display_non_conversation_model(self, admin_instance):
        """Test channel_search_display for non-conversation model (branch 87->92)."""
        mock_channel_type = MagicMock()
        mock_channel_type.model = "other_model"

        obj = MagicMock()
        obj.channel_id = 123
        obj.channel_type = mock_channel_type

        result = admin_instance.channel_search_display(obj)

        assert result == "-"

    def test_get_form(self, admin_instance, mocker):
        """Test get_form adds conversation content type id."""
        mock_content_type = mocker.patch(f"{self.target_module}.ContentType")
        mock_ct_instance = MagicMock()
        mock_ct_instance.id = 42
        mock_content_type.objects.get_for_model.return_value = mock_ct_instance

        mock_request = MagicMock()

        with patch.object(EntityChannelAdmin.__bases__[0], "get_form") as mock_super_get_form:
            mock_form = MagicMock()
            mock_super_get_form.return_value = mock_form

            result = admin_instance.get_form(mock_request)

            assert result.conversation_content_type_id == 42
