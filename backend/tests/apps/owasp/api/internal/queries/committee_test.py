from apps.owasp.api.internal.nodes.committee import CommitteeNode
from apps.owasp.api.internal.queries.committee import CommitteeQuery


class TestCommitteeQuery:
    """Test cases for CommitteeQuery class."""

    def test_committee_query_has_strawberry_definition(self):
        """Test if CommitteeQuery is a valid Strawberry type."""
        assert hasattr(CommitteeQuery, "__strawberry_definition__")

        field_names = [field.name for field in CommitteeQuery.__strawberry_definition__.fields]
        assert "committee" in field_names

    def test_committee_field_configuration(self):
        """Test if 'committee' field is configured properly."""
        committee_field = next(
            field
            for field in CommitteeQuery.__strawberry_definition__.fields
            if field.name == "committee"
        )

        assert committee_field.type.of_type is CommitteeNode

        arg_names = [arg.python_name for arg in committee_field.arguments]
        assert "key" in arg_names

        key_arg = next(arg for arg in committee_field.arguments if arg.python_name == "key")
        assert key_arg.type_annotation.annotation is str
