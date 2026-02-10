from unittest.mock import Mock, patch

from apps.owasp.api.internal.nodes.committee import CommitteeNode
from apps.owasp.api.internal.queries.committee import CommitteeQuery
from apps.owasp.models.committee import Committee


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


class TestCommitteeResolution:
    """Test cases for committee resolution methods."""

    def test_committee_found(self):
        """Test if a committee is returned when found."""
        mock_committee = Mock(spec=Committee)

        with patch("apps.owasp.models.committee.Committee.objects.get") as mock_get:
            mock_get.return_value = mock_committee

            result = CommitteeQuery().committee(key="test-committee")

            assert result == mock_committee
            mock_get.assert_called_once_with(key="www-committee-test-committee")

    def test_committee_not_found(self):
        """Test if None is returned when the committee is not found."""
        with patch("apps.owasp.models.committee.Committee.objects.get") as mock_get:
            mock_get.side_effect = Committee.DoesNotExist

            result = CommitteeQuery().committee(key="non-existent")

            assert result is None
            mock_get.assert_called_once_with(key="www-committee-non-existent")
