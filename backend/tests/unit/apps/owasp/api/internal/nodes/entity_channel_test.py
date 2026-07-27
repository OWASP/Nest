"""Tests for EntityChannel GraphQL node resolvers."""

from unittest.mock import Mock

from apps.owasp.api.internal.nodes.entity_channel import EntityChannelNode


class TestEntityChannelNodeResolvers:
    def _get_resolver(self, field_name):
        """Get the resolver function for a field."""
        for field in EntityChannelNode.__strawberry_definition__.fields:
            if field.name == field_name:
                return field.base_resolver.wrapped_func if field.base_resolver else None
        return None

    def test_name_and_external_id_resolvers_return_values_from_channel(self):
        """Return channel name and external id when channel is present."""
        mock_channel = Mock(name="mock-conversation")
        mock_channel.name = "chapter-general"
        mock_channel.slack_channel_id = "C123ABC"

        mock_entity_channel = Mock()
        mock_entity_channel.channel = mock_channel

        name_resolver = self._get_resolver("name")
        external_id_resolver = self._get_resolver("external_id")

        assert name_resolver is not None
        assert external_id_resolver is not None
        assert name_resolver(None, mock_entity_channel) == "chapter-general"
        assert external_id_resolver(None, mock_entity_channel) == "C123ABC"

    def test_name_and_external_id_resolvers_return_none_when_channel_missing(self):
        """Return None when no linked channel exists."""
        mock_entity_channel = Mock()
        mock_entity_channel.channel = None

        name_resolver = self._get_resolver("name")
        external_id_resolver = self._get_resolver("external_id")

        assert name_resolver is not None
        assert external_id_resolver is not None
        assert name_resolver(None, mock_entity_channel) is None
        assert external_id_resolver(None, mock_entity_channel) is None
