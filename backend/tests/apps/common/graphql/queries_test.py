"""Test cases for BaseQuery."""

from graphene import ObjectType

from apps.common.graphql.queries import BaseQuery


class TestBaseQuery:
    """Test cases for BaseQuery class."""

    def test_base_query_inheritance(self):
        """Test if BaseQuery inherits from ObjectType."""
        assert issubclass(BaseQuery, ObjectType)
