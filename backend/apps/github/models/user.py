"""GitHub user model and related functionality."""

from django.core.exceptions import ValidationError
from django.db import models

from apps.common.models import TimestampedModel
from apps.github.constants import (
    GITHUB_LOGIN_REQUIRED,
    GITHUB_NODE_ID_NOT_FOUND,
    GITHUB_NODE_ID_REQUIRED,
    GITHUB_USER_DATA_REQUIRED,
)
from apps.github.models.common import GenericUserModel, NodeModel


class User(NodeModel, GenericUserModel, TimestampedModel):
    """Model representing a GitHub user or organization."""

    class Meta:
        db_table = "github_users"
        verbose_name_plural = "Users"
        ordering = ["login"]
        indexes = [
            models.Index(fields=["login"]),
            models.Index(fields=["type"]),
        ]

    bio = models.TextField(
        verbose_name="Bio",
        max_length=1000,
        blank=True,
        default="",
        help_text="User's GitHub biography",
    )
    type = models.CharField(
        verbose_name="User type",
        max_length=50,
        default="User",
        choices=[
            ("User", "User"),
            ("Organization", "Organization"),
        ],
        help_text="Distinguishes between User and Organization accounts",
    )
    public_repositories_count = models.PositiveIntegerField(
        verbose_name="Public repositories count",
        default=0,
        help_text="Number of public repositories",
    )

    def __str__(self):
        """Return the string representation of the user."""
        return f"{self.name or self.login}"

    def clean(self):
        """Validate required fields before saving the user."""
        super().clean()
        if not self.login:
            raise ValidationError(GITHUB_LOGIN_REQUIRED)
        if not self.node_id:
            raise ValidationError(GITHUB_NODE_ID_REQUIRED)

    def save(self, *args, **kwargs):
        """Save the user object after validation."""
        self.full_clean()
        super().save(*args, **kwargs)

    def from_github(self, gh_user):
        """Populate user fields with data from GitHub."""
        if not gh_user:
            raise ValueError(GITHUB_USER_DATA_REQUIRED)

        super().from_github(gh_user)

        field_mapping = {
            "avatar_url": "avatar_url",
            "company": "company",
            "email": "email",
            "followers_count": "followers",
            "following_count": "following",
            "location": "location",
            "login": "login",
            "name": "name",
            "created_at": "created_at",
            "updated_at": "updated_at",
            "bio": "bio",
            "type": "type",
            "public_repositories_count": "public_repos",
        }

        for model_field, gh_field in field_mapping.items():
            value = getattr(gh_user, gh_field, None)
            if value is not None:
                setattr(self, model_field, value)

    @staticmethod
    def update_data(gh_user, save=True):
        """Update or create user data based on GitHub user information."""
        if not gh_user:
            raise ValueError(GITHUB_USER_DATA_REQUIRED)

        user_node_id = User.get_node_id(gh_user)
        if not user_node_id:
            raise ValueError(GITHUB_NODE_ID_NOT_FOUND)

        try:
            user = User.objects.get(node_id=user_node_id)
        except User.DoesNotExist:
            user = User(node_id=user_node_id)

        user.from_github(gh_user)
        if save:
            user.save()
        return user
