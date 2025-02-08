"""Test cases for UserQuery."""

from unittest.mock import Mock, patch

import pytest
from graphene import Field, NonNull, String
from apps.common.graphql.queries import BaseQuery
from apps.github.graphql.nodes.user import UserNode
from apps.github.graphql.queries.user import UserQuery
from apps.github.models.user import User


class TestUserQuery:
    """Test cases for UserQuery class."""

    @pytest.fixture
    def mock_info(self):
        """GraphQL info mock fixture."""
        return Mock()

    @pytest.fixture
    def mock_user(self):
        """User mock fixture."""
        return Mock(spec=User)

    def test_user_query_inheritance(self):
        """Test if UserQuery inherits from BaseQuery."""
        assert issubclass(UserQuery, BaseQuery)

    def test_resolve_user_existing(self, mock_user, mock_info):
        """Test resolving an existing user."""
        with patch("apps.github.models.user.User.objects.get") as mock_get:
            mock_get.return_value = mock_user

            result = UserQuery.resolve_user(
                None, mock_info, login="test-user"
            )

            assert result == mock_user
            mock_get.assert_called_once_with(login="test-user")

    def test_resolve_user_not_found(self, mock_info):
        """Test resolving a non-existent user."""
        with patch("apps.github.models.user.User.objects.get") as mock_get:
            mock_get.side_effect = User.DoesNotExist

            result = UserQuery.resolve_user(
                None, mock_info, login="non-existent"
            )

            assert result is None
            mock_get.assert_called_once_with(login="non-existent")

    def test_user_field_configuration(self):
        """Test if user field is properly configured."""
        user_field = UserQuery._meta.fields.get("user")
        
        assert isinstance(user_field, Field)
        assert user_field.type == UserNode
        assert "login" in user_field.args
        
        login_arg = user_field.args["login"]
        assert isinstance(login_arg.type, NonNull)
        assert login_arg.type.of_type == String