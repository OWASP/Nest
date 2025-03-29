"""Github app user model."""

from django.db import models

from apps.common.models import TimestampedModel
from apps.github.constants import GITHUB_GHOST_USER_LOGIN, OWASP_FOUNDATION_LOGIN
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

    is_bot = models.BooleanField(verbose_name="Is bot", default=False)

    def __str__(self):
        """Return a human-readable representation of the user.

        Returns:
            str: The name or login of the user.
        """
        return f"{self.name or self.login}"

    @property
    def issues(self):
        """Get issues created by the user.

        Returns:
            QuerySet: A queryset of issues created by the user.
        """
        return self.created_issues.all()

    @property
    def releases(self):
        """Get releases created by the user.

        Returns:
            QuerySet: A queryset of releases created by the user.
        """
        return self.created_releases.all()

    def from_github(self, gh_user):
        """Update the user instance based on GitHub user data.

        Args:
            gh_user (github.NamedUser.NamedUser): The GitHub user object.
        """
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

        self.is_bot = gh_user.type == "Bot"

    @staticmethod
    def get_non_indexable_logins():
        """Get logins that should not be indexed.

        Returns:
            set: A set of non-indexable logins.
        """
        return {
            GITHUB_GHOST_USER_LOGIN,
            OWASP_FOUNDATION_LOGIN,
            *Organization.get_logins(),
        }

    @staticmethod
    def update_data(gh_user, save=True):
        """Update GitHub user data.

        Args:
            gh_user (github.NamedUser.NamedUser): The GitHub user object.
            save (bool, optional): Whether to save the instance. Defaults to True.

        Returns:
            User: The updated or created user instance.
        """
        user_node_id = User.get_node_id(gh_user)
        try:
            user = User.objects.get(node_id=user_node_id)
        except User.DoesNotExist:
            user = User(node_id=user_node_id)

        user.from_github(gh_user)
        if save:
            user.save()

        return user
