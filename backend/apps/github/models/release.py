"""Github app release model."""

from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.github.models.common import NodeModel
from apps.github.models.mixins.release import ReleaseIndexMixin


class Release(BulkSaveModel, NodeModel, ReleaseIndexMixin, TimestampedModel):
    """Release model."""

    node_id = models.CharField(max_length=255)

    class Meta:
        db_table = "github_releases"
        verbose_name_plural = "Releases"

    name = models.CharField(verbose_name="Name", max_length=200)
    tag_name = models.CharField(verbose_name="Tag name", max_length=100)
    description = models.TextField(verbose_name="Description", default="")

    is_draft = models.BooleanField(verbose_name="Is draft", default=False)
    is_pre_release = models.BooleanField(verbose_name="Is pre-release", default=False)

    sequence_id = models.PositiveBigIntegerField(verbose_name="Release ID", default=0)
    created_at = models.DateTimeField(verbose_name="Created at")
    published_at = models.DateTimeField(verbose_name="Published at")

    # FKs.
    author = models.ForeignKey(
        "github.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_releases",
    )
    repository = models.ForeignKey(
        "github.Repository",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="releases",
    )

    def __str__(self):
        """User human readable representation."""
        return f"{self.name} by {self.author}"

    @property
    def summary(self):
        """Return release summary."""
        return f"{self.tag_name} on {self.published_at.strftime('%b %d, %Y')}"

    def from_github(self, gh_release, author=None, repository=None):
        """Update instance based on GitHub release data."""
        field_mapping = {
            "created_at": "created_at",
            "description": "body",
            "is_draft": "draft",
            "is_pre_release": "prerelease",
            "name": "title",
            "published_at": "published_at",
            "sequence_id": "id",
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

    @staticmethod
    def bulk_save(releases):
        """Bulk save releases."""
        BulkSaveModel.bulk_save(Release, releases)

    @staticmethod
    def update_data(gh_release, author=None, repository=None, save=True):
        """Update release data."""
        release_node_id = Release.get_node_id(gh_release)
        try:
            release = Release.objects.get(node_id=release_node_id)
        except Release.DoesNotExist:
            release = Release(node_id=release_node_id)

        release.from_github(gh_release, author=author, repository=repository)
        if save:
            release.save()

        return release
