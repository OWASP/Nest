from unittest.mock import Mock, patch

from apps.owasp.api.internal.nodes.committee import CommitteeNode
from apps.owasp.api.internal.queries.committee import (
    SEARCH_COMMITTEES_LIMIT,
    CommitteeQuery,
)
from apps.owasp.models.committee import Committee


class TestCommitteeQuery:
    """Test cases for CommitteeQuery class."""

    def test_committee_query_has_strawberry_definition(self):
        """Test if CommitteeQuery is a valid Strawberry type."""
        assert hasattr(CommitteeQuery, "__strawberry_definition__")

        field_names = [field.name for field in CommitteeQuery.__strawberry_definition__.fields]
        assert "committee" in field_names
        assert "search_committees" in field_names

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


class TestSearchCommittees:
    """Test cases for search_committees query."""

    def test_search_committees_short_query(self):
        """Test search_committees returns empty for short queries."""
        query = CommitteeQuery()
        result = query.search_committees(query="ab")
        assert result == []

    def test_search_committees_long_query(self):
        """Test search_committees returns empty for queries exceeding max length."""
        query = CommitteeQuery()
        result = query.search_committees(query="a" * 101)
        assert result == []

    def test_search_committees_whitespace_query(self):
        """Test search_committees strips whitespace before checking length."""
        query = CommitteeQuery()
        result = query.search_committees(query="  ab  ")
        assert result == []

    def test_search_committees_valid_query(self):
        """Test search_committees returns matching committees."""
        mock_committees = [Mock(), Mock()]
        query = CommitteeQuery()
        with patch.object(Committee, "active_committees") as mock_active:
            mock_selected_qs = Mock()
            mock_active.select_related.return_value = mock_selected_qs
            mock_qs = Mock()
            mock_selected_qs.filter.return_value = mock_qs
            mock_ordered_qs = Mock()
            mock_qs.order_by.return_value = mock_ordered_qs
            mock_ordered_qs.__getitem__ = Mock(return_value=mock_committees)

            result = query.search_committees(query="test")

            mock_active.select_related.assert_called_once_with("owasp_repository")
            mock_selected_qs.filter.assert_called_once_with(name__icontains="test")
            mock_qs.order_by.assert_called_once_with("name")
            mock_ordered_qs.__getitem__.assert_called_once_with(
                slice(None, SEARCH_COMMITTEES_LIMIT)
            )
            assert result == mock_committees
