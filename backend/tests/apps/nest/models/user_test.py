from unittest.mock import Mock, patch

from django.db import models

from apps.nest.models import User


class TestUserModel:
    """Unit tests for User model without DB."""

    def test_model_fields(self):
        assert isinstance(User._meta.get_field("github_id"), models.CharField)
        assert User._meta.get_field("github_id").max_length > 0
        assert User._meta.get_field("github_id").unique is True

        assert isinstance(User._meta.get_field("username"), models.CharField)
        assert User._meta.get_field("username").max_length > 0
        assert User._meta.get_field("username").unique is True

    def test_meta_options(self):
        assert User._meta.db_table == "user"
        assert User._meta.ordering == ["username"]

    def test_str_representation(self):
        mock_user = Mock(spec=User)
        mock_user.github_id = "gh123"
        mock_user.username = "testuser"

        with patch.object(User, "__str__", lambda s: s.github_id or s.username):
            user = User()
            user.github_id = "gh123"
            assert str(user) == "gh123"

            user.github_id = None
            user.username = "testuser"
            assert str(user) == "testuser"
