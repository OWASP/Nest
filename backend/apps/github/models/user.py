"""Github app user model."""

from __future__ import annotations

from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.common.utils import get_absolute_url
from apps.github.constants import (
    GITHUB_ACTIONS_USER_LOGIN,
    GITHUB_GHOST_USER_LOGIN,
    OWASP_FOUNDATION_LOGIN,
)
from apps.github.models.common import GenericUserModel, NodeModel
from apps.github.models.mixins.user import UserIndexMixin
from apps.github.models.organization import Organization


class User(NodeModel, GenericUserModel, TimestampedModel, UserIndexMixin):
    """User model."""

    class Meta:
        db_table = "github_users"
        indexes = [
            models.Index(fields=["-created_at"], name="github_user_created_at_desc"),
            models.Index(fields=["-updated_at"], name="github_user_updated_at_desc"),
        ]
        verbose_name_plural = "Users"

    bio = models.TextField(verbose_name="Bio", max_length=1000, default="")
    is_hireable = models.BooleanField(verbose_name="Is hireable", default=False)
    twitter_username = models.CharField(
        verbose_name="Twitter username", max_length=50, default="", blank=True
    )

    is_bot = models.BooleanField(verbose_name="Is bot", default=False)

    is_owasp_staff = models.BooleanField(
        default=False,
        verbose_name="OWASP Staff",
        help_text="Indicates if the user is an OWASP staff member.",
    )

    contributions_count = models.PositiveIntegerField(
        verbose_name="Contributions count", default=0
    )

    def __str__(self) -> str:
        """Return a human-readable representation of the user.

        Returns
            str: The name or login of the user.

        """
        return self.title

    @property
    def issues(self):
        """Get issues created by the user.

        Returns:
            QuerySet: A queryset of issues created by the user.

        """
        return self.created_issues.all()

    @property
    def nest_url(self) -> str:
        """Get Nest URL for user."""
        return get_absolute_url(f"/members/{self.nest_key}")

    @property
    def releases(self):
        """Get releases created by the user.

        Returns
            QuerySet: A queryset of releases created by the user.

        """
        return self.created_releases.all()

    def from_github(self, gh_user) -> None:
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
            value = getattr(gh_user, gh_field, None)
            if value is not None:
                setattr(self, model_field, value)

        self.is_bot = gh_user.type == "Bot"

    def get_absolute_url(self):
        """Get absolute URL for the user."""
        return f"/members/{self.nest_key}"

    @staticmethod
    def bulk_save(users, fields=None) -> None:
        """Bulk save users."""
        BulkSaveModel.bulk_save(User, users, fields=fields)

    @staticmethod
    def get_non_indexable_logins() -> set:
        """Get logins that should not be indexed.

        Returns
            set: A set of non-indexable logins.

        """
        return {
            GITHUB_ACTIONS_USER_LOGIN,
            GITHUB_GHOST_USER_LOGIN,
            OWASP_FOUNDATION_LOGIN,
            *Organization.get_logins(),
        }

    @staticmethod
    def update_data(gh_user, *, save: bool = True, **kwargs) -> User | None:
        """Update GitHub user data.

        Args:
            gh_user (github.NamedUser.NamedUser): The GitHub user object.
            save (bool, optional): Whether to save the instance.
            **kwargs: optional extra attributes.

        Returns:
            User: The updated or created user instance.

        """
        user_node_id = User.get_node_id(gh_user)
        if not user_node_id:
            return None

        try:
            user = User.objects.get(node_id=user_node_id)
        except User.DoesNotExist:
            user = User(node_id=user_node_id)

        user.from_github(gh_user)

        for name, value in kwargs.items():
            setattr(user, name, value)

        if save:
            user.save()

        return user
