"""Tests for EntityChannel model."""

from unittest.mock import MagicMock, Mock, PropertyMock, patch

from apps.owasp.models.entity_channel import EntityChannel


class TestEntityChannelModel:
    """Tests for EntityChannel model."""

    def test_str_representation(self):
        """Test __str__ method returns correct format."""
        mock_conversation = MagicMock()
        mock_conversation.name = "test-channel"
        mock_conversation.__str__ = Mock(return_value="test-channel")

        channel = EntityChannel()
        channel.platform = "slack"

        mock_entity = Mock()
        mock_entity.__str__ = Mock(return_value="Test Entity")

        with (
            patch.object(
                type(channel), "channel", new_callable=PropertyMock, return_value=mock_conversation
            ),
            patch.object(
                type(channel), "entity", new_callable=PropertyMock, return_value=mock_entity
            ),
        ):
            result = str(channel)

        assert result == "Test Entity - test-channel (slack)"
