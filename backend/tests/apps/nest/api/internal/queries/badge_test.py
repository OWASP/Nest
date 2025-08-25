from apps.nest.api.internal.nodes.badge import BadgeNode
from apps.nest.api.internal.queries.badge import BadgeQueries


class TestBadgeQueries:
    """Tests for BadgeQueries configuration."""

    def test_badges_field_exists(self):
        assert hasattr(BadgeQueries, "__strawberry_definition__")
        field_names = [f.name for f in BadgeQueries.__strawberry_definition__.fields]
        assert "badges" in field_names

        field = next(
            f for f in BadgeQueries.__strawberry_definition__.fields if f.name == "badges"
        )
        # badges returns list[BadgeNode]
        assert (
            getattr(field.type, "of_type", None) is BadgeNode
            or getattr(getattr(field.type, "of_type", None), "of_type", None) is BadgeNode
        )
