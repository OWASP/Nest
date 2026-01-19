"""Base Test Class for GraphQL Node Tests."""


class GraphQLNodeBaseTest:
    """Base Test Class for GraphQL Node Tests."""

    def _get_field_by_name(self, name, node_class):
        return next(
            (f for f in node_class.__strawberry_definition__.fields if f.name == name), None
        )
