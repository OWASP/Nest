"""OWASP app post model."""

from datetime import UTC, datetime

from django.db import models
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now

from apps.common.models import BulkSaveModel, TimestampedModel


class Post(BulkSaveModel, TimestampedModel):
    """Post model."""

    class Meta:
        db_table = "owasp_posts"
        indexes = [
            models.Index(fields=["-published_at"], name="post_published_at_desc_idx"),
        ]
        verbose_name_plural = "Posts"

    author_image_url = models.URLField(verbose_name="Author image URL", blank=True, default="")
    author_name = models.CharField(verbose_name="Author name", max_length=100)
    published_at = models.DateTimeField(verbose_name="Publication date")
    title = models.CharField(verbose_name="Title", max_length=200)
    url = models.URLField(verbose_name="URL", unique=True)

    def __str__(self):
        """Return human-readable representation."""
        return self.title

    @staticmethod
    def bulk_save(posts, fields=None) -> None:  # type: ignore[override]
        """Bulk save posts."""
        BulkSaveModel.bulk_save(Post, posts, fields=fields)

    @staticmethod
    def recent_posts():
        """Get recent posts."""
        return Post.objects.filter(published_at__lte=now()).order_by("-published_at")

    @staticmethod
    def update_data(data, *, save: bool = True) -> "Post":
        """Update post data."""
        url = data.get("url")

        try:
            post = Post.objects.get(url=url)
        except Post.DoesNotExist:
            post = Post(url=url)

        post.from_dict(data)
        if save:
            post.save()

        return post

    def from_dict(self, data) -> None:
        """Update instance based on dict data."""
        published_at = data["published_at"]
        published_at = (
            parse_datetime(published_at)
            if isinstance(published_at, str)
            else datetime(
                published_at.year,
                published_at.month,
                published_at.day,
                tzinfo=UTC,
            )
        )

        fields = {
            "author_image_url": data.get("author_image_url", "") or "",
            "author_name": data["author_name"],
            "published_at": published_at,
            "title": data["title"],
            "url": data["url"],
        }

        for key, value in fields.items():
            setattr(self, key, value)
