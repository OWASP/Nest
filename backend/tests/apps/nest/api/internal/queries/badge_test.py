"""Tests for Badge GraphQL queries and nodes."""

from unittest.mock import MagicMock, patch

from apps.nest.api.internal.nodes.badge import BadgeNode
from apps.nest.api.internal.queries.badge import BadgeQueries
from apps.nest.models.badge import Badge


class TestBadgeQueries:
    """Test cases for BadgeQueries class."""

    def test_has_strawberry_definition(self):
        """BadgeQueries should be a valid Strawberry type with 'badges' field."""
        assert hasattr(BadgeQueries, "__strawberry_definition__")
        field_names = [f.name for f in BadgeQueries.__strawberry_definition__.fields]
        assert "badges" in field_names

    def test_badges_field_configuration(self):
        """'badges' field should return a list of BadgeNode."""
        field = next(
            f for f in BadgeQueries.__strawberry_definition__.fields if f.name == "badges"
        )
        assert field.type.of_type is BadgeNode or field.type is BadgeNode

    @patch("apps.nest.models.badge.Badge.objects.all")
    def test_badges_resolution(self, mock_all):
        """Resolver should return badges ordered by weight and name."""
        mock_badge = MagicMock(spec=Badge)
        mock_qs = MagicMock()
        mock_qs.order_by.return_value = [mock_badge]
        mock_all.return_value = mock_qs

        result = BadgeQueries().badges()

        assert result == [mock_badge]
        mock_all.assert_called_once()
        mock_qs.order_by.assert_called_once_with("weight", "name")
