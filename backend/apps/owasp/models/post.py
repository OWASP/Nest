"""OWASP app post model."""

from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel


class Post(BulkSaveModel, TimestampedModel):
    """Post model."""

    class Meta:
        db_table = "owasp_posts"
        verbose_name_plural = "Posts"

    author_name = models.CharField(verbose_name="Author name", max_length=100)
    author_image_url = models.URLField(verbose_name="Author image URL", blank=True, default="")
    published_at = models.DateTimeField(verbose_name="Publication date")
    title = models.CharField(verbose_name="Title", max_length=200)
    url = models.URLField(verbose_name="URL")

    def __str__(self):
        """Return human-readable representation."""
        return self.title

    @staticmethod
    def bulk_save(posts, fields=None):
        """Bulk save posts."""
        BulkSaveModel.bulk_save(Post, posts, fields=fields)

    @staticmethod
    def recent_posts():
        """Get recent posts."""
        return Post.objects.all().order_by("-published_at")
