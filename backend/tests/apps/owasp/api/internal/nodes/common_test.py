"""Tests for common GraphQL nodes."""

import math
from unittest.mock import Mock

from apps.owasp.api.internal.nodes.common import GenericEntityNode


class TestGenericEntityNode:
    def test_entity_leaders_resolver(self):
        """Test entity_leaders returns leaders from entity."""
        mock_leader1 = Mock()
        mock_leader2 = Mock()

        mock_entity = Mock()
        mock_entity.entity_leaders = [mock_leader1, mock_leader2]

        result = GenericEntityNode.entity_leaders(mock_entity)

        assert result == [mock_leader1, mock_leader2]

    def test_leaders_resolver(self):
        """Test leaders returns indexed leaders list."""
        mock_entity = Mock()
        mock_entity.idx_leaders = ["leader1", "leader2"]

        result = GenericEntityNode.leaders(mock_entity)

        assert result == ["leader1", "leader2"]

    def test_related_urls_resolver(self):
        """Test related_urls returns indexed URLs list."""
        mock_entity = Mock()
        mock_entity.idx_related_urls = ["https://example.com", "https://test.com"]

        result = GenericEntityNode.related_urls(mock_entity)

        assert result == ["https://example.com", "https://test.com"]

    def test_updated_at_resolver(self):
        """Test updated_at returns indexed timestamp."""
        mock_entity = Mock()
        mock_entity.idx_updated_at = 1234567890.0

        result = GenericEntityNode.updated_at(mock_entity)

        assert math.isclose(result, 1234567890.0)

    def test_url_resolver(self):
        """Test url returns indexed URL."""
        mock_entity = Mock()
        mock_entity.idx_url = "https://owasp.org/www-project-example"

        result = GenericEntityNode.url(mock_entity)

        assert result == "https://owasp.org/www-project-example"
