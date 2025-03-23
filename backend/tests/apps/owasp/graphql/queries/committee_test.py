from unittest.mock import Mock, patch

import pytest
from graphene import Field, NonNull, String

from apps.common.graphql.queries import BaseQuery
from apps.owasp.graphql.nodes.committee import CommitteeNode
from apps.owasp.graphql.queries.committee import CommitteeQuery
from apps.owasp.models.committee import Committee


class TestCommitteeQuery:
    """Test cases for CommitteeQuery class."""

    def test_committee_query_inheritance(self):
        """Test if CommitteeQuery inherits from BaseQuery."""
        assert issubclass(CommitteeQuery, BaseQuery)

    def test_committee_field_configuration(self):
        """Test if committee field is properly configured."""
        committee_field = CommitteeQuery._meta.fields.get("committee")
        assert isinstance(committee_field, Field)
        assert committee_field.type == CommitteeNode

        assert "key" in committee_field.args
        key_arg = committee_field.args["key"]
        assert isinstance(key_arg.type, NonNull)
        assert key_arg.type.of_type == String


class TestCommitteeResolution:
    """Test cases for committee resolution."""

    @pytest.fixture()
    def mock_committee(self):
        """Committee mock fixture."""
        return Mock(spec=Committee)

    @pytest.fixture()
    def mock_info(self):
        """GraphQL info mock fixture."""
        return Mock()

    def test_resolve_committee_existing(self, mock_committee, mock_info):
        """Test resolving an existing committee."""
        with patch("apps.owasp.models.committee.Committee.objects.get") as mock_get:
            mock_get.return_value = mock_committee

            result = CommitteeQuery.resolve_committee(None, mock_info, key="test-committee")

            assert result == mock_committee
            mock_get.assert_called_once_with(key="www-committee-test-committee")

    def test_resolve_committee_not_found(self, mock_info):
        """Test resolving a non-existent committee."""
        with patch("apps.owasp.models.committee.Committee.objects.get") as mock_get:
            mock_get.side_effect = Committee.DoesNotExist

            result = CommitteeQuery.resolve_committee(None, mock_info, key="non-existent")

            assert result is None
            mock_get.assert_called_once_with(key="www-committee-non-existent")
