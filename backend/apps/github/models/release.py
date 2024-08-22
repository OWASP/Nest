"""Github app release model."""

from django.db import models

from apps.common.models import TimestampedModel
from apps.github.models import NodeModel


class Release(NodeModel, TimestampedModel):
    """Release model."""

    class Meta:
        db_table = "github_releases"
        verbose_name_plural = "Releases"

    name = models.CharField(verbose_name="Name", max_length=200)
    tag_name = models.CharField(verbose_name="Tag name", max_length=100)
    description = models.TextField(verbose_name="Description", default="")

    is_draft = models.BooleanField(verbose_name="Is draft", default=False)
    is_pre_release = models.BooleanField(verbose_name="Is pre-release", default=False)

    created_at = models.DateTimeField(verbose_name="Created at")
    published_at = models.DateTimeField(verbose_name="Published at")

    # FKs.
    author = models.ForeignKey(
        "github.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    repository = models.ForeignKey(
        "github.Repository",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    def __str__(self):
        """User human readable representation."""
        return f"{self.repository.name} {self.name} by {self.author}"

    def from_github(self, gh_release, author=None, repository=None):
        """Update instance based on GitHub release data."""
        field_mapping = {
            "description": "body",
            "is_draft": "draft",
            "is_pre_release": "prerelease",
            "name": "title",
            "created_at": "created_at",
            "published_at": "published_at",
            "tag_name": "tag_name",
        }

        # Direct fields.
        for model_field, gh_field in field_mapping.items():
            value = getattr(gh_release, gh_field)
            if value is not None:
                setattr(self, model_field, value)

        # Author.
        self.author = author

        # Repository.
        self.repository = repository
