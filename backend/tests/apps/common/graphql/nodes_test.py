"""Test cases for BaseNode."""

from graphene_django import DjangoObjectType

from apps.common.graphql.nodes import BaseNode


class TestBaseNode:
    """Test cases for BaseNode class."""

    def test_base_node_inheritance(self):
        """Test if BaseNode inherits from DjangoObjectType."""
        assert issubclass(BaseNode, DjangoObjectType)

    def test_base_node_meta(self):
        """Test if BaseNode Meta is properly configured."""
        assert hasattr(BaseNode, "_meta")
        assert isinstance(BaseNode, DjangoObjectType.__class__)
