"""Github app user model."""

from django.db import models

from apps.common.models import TimestampedModel
from apps.github.models.common import GenericUserModel, NodeModel
from apps.github.models.mixins.user import UserIndexMixin
from apps.github.models.organization import Organization


class User(NodeModel, GenericUserModel, TimestampedModel, UserIndexMixin):
    """User model."""

    class Meta:
        db_table = "github_users"
        verbose_name_plural = "Users"

    bio = models.TextField(verbose_name="Bio", max_length=1000, default="")
    is_hireable = models.BooleanField(verbose_name="Is hireable", default=False)
    twitter_username = models.CharField(verbose_name="Twitter username", max_length=50, default="")

    def __str__(self):
        """User human readable representation."""
        return f"{self.name or self.login}"

    @property
    def is_indexable(self):
        """Users to index."""
        return (
            self.login != "ghost" and self.login not in Organization.get_logins()
        )  # See https://github.com/ghost for more info.

    def from_github(self, gh_user):
        """Update instance based on GitHub user data."""
        super().from_github(gh_user)

        field_mapping = {
            "bio": "bio",
            "is_hireable": "hireable",
            "twitter_username": "twitter_username",
        }

        # Direct fields.
        for model_field, gh_field in field_mapping.items():
            value = getattr(gh_user, gh_field)
            if value is not None:
                setattr(self, model_field, value)

    @staticmethod
    def update_data(gh_user, save=True):
        """Update GitHub user data."""
        user_node_id = User.get_node_id(gh_user)
        try:
            user = User.objects.get(node_id=user_node_id)
        except User.DoesNotExist:
            user = User(node_id=user_node_id)

        user.from_github(gh_user)
        if save:
            user.save()

        return user
