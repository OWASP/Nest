"""Unit tests for Nest app's custom User model."""

from unittest.mock import Mock, PropertyMock, patch

from django.db import models

from apps.github.models.user import User as GithubUser
from apps.nest.models import User


class TestUserModel:
    """Unit tests for User model without DB access."""

    def test_model_fields(self):
        """Test field types and constraints."""
        github_user_field = User._meta.get_field("github_user")
        assert isinstance(github_user_field, models.OneToOneField)

        assert github_user_field.remote_field.model == GithubUser
        assert github_user_field.null
        assert github_user_field.blank

        username_field = User._meta.get_field("username")
        assert isinstance(username_field, models.CharField)
        assert username_field.max_length > 0
        assert username_field.unique

    def test_meta_options(self):
        """Test Meta class options like db_table and ordering."""
        assert User._meta.db_table == "nest_users"
        assert User._meta.ordering == ["username"]
        assert User._meta.verbose_name_plural == "Users"

    def test_index_on_username(self):
        """Ensure 'username' field is indexed."""
        indexes = User._meta.indexes
        assert any(
            isinstance(index, models.Index) and index.fields == ["username"] for index in indexes
        )

    def test_str_representation(self):
        """Test __str__ returns the username."""
        user = User(username="testuser")
        assert str(user) == "testuser"

    def test_active_api_keys_property(self):
        """Test active_api_keys property returns filtered queryset."""
        user = User(username="testuser")

        mock_api_keys = Mock()
        mock_filter_result = Mock()
        mock_api_keys.filter.return_value = mock_filter_result

        with patch.object(type(user), "api_keys", new_callable=PropertyMock) as mock_prop:
            mock_prop.return_value = mock_api_keys

            result = user.active_api_keys

            assert mock_api_keys.filter.called
            call_kwargs = mock_api_keys.filter.call_args[1]
            assert "expires_at__gte" in call_kwargs
            assert call_kwargs["is_revoked"] is False
            assert result == mock_filter_result
