"""Tests for Badge GraphQL queries and nodes."""

from unittest.mock import MagicMock, patch

from apps.nest.api.internal.queries.badge import BadgeQueries
from apps.nest.models.badge import Badge


class TestBadgeQueries:
    """Test cases for BadgeQueries class."""

    def test_has_strawberry_definition(self):
        """BadgeQueries should be a valid Strawberry type with 'badges' field."""
        from strawberry import Schema

        schema = Schema(query=BadgeQueries)
        res = schema.execute_sync('{ __type(name:"BadgeQueries"){ fields { name } } }')
        assert res.errors is None
        field_names = [f["name"] for f in res.data["__type"]["fields"]]
        assert "badges" in field_names

    def test_badges_field_configuration(self):
        """'badges' field should return a list of BadgeNode."""
        from strawberry import Schema

        schema = Schema(query=BadgeQueries)
        res = schema.execute_sync(
            """
            {
                __type(name: "BadgeQueries") {
                    fields {
                        name type { kind ofType { kind ofType { kind ofType { name } } } }
                    }
                }
            }
            """
        )
        assert res.errors is None
        badges_field = next(f for f in res.data["__type"]["fields"] if f["name"] == "badges")
        assert badges_field["type"]["kind"] == "NON_NULL"
        assert badges_field["type"]["ofType"]["kind"] == "LIST"
        assert badges_field["type"]["ofType"]["ofType"]["kind"] == "NON_NULL"
        assert badges_field["type"]["ofType"]["ofType"]["ofType"]["name"] == "BadgeNode"

    @patch("apps.nest.api.internal.queries.badge.Badge.objects")
    def test_badges_resolution(self, mock_manager):
        """Resolver should return badges ordered by weight and name."""
        mock_badge = MagicMock(spec=Badge)
        mock_qs = MagicMock()
        mock_manager.all.return_value = mock_qs
        mock_qs.order_by.return_value = [mock_badge]

        result = BadgeQueries().badges()

        assert list(result) == [mock_badge]
        mock_manager.all.assert_called_once_with()
        mock_qs.order_by.assert_called_once_with("weight", "name")
