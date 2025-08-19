from apps.nest.api.internal.nodes.badge import BadgeNode


class TestBadgeNode:
    """Tests for BadgeNode configuration."""

    def test_badge_node_definition(self):
        assert BadgeNode.__strawberry_definition__.name == "BadgeNode"

        fields = {f.name: f for f in BadgeNode.__strawberry_definition__.fields}
        # _id from relay + selected fields
        assert set(fields.keys()) >= {
            "_id", "id", "name", "description", "weight", "css_class"}
