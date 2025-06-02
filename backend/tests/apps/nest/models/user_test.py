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
        assert User._meta.db_table == "nest_users"
        assert User._meta.ordering == ["username"]

    def test_str_representation(self):
        user = User()
        user.github_id = "gh123"
        user.username = "testuser"
        assert str(user) == "testuser"

        user.github_id = None
        assert str(user) == "testuser"
