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

    @staticmethod
    def update_data(data, save=True):
        """Update post data."""
        url = data.get("url")
        if not url:
            return None

        try:
            post = Post.objects.get(url=url)
        except Post.DoesNotExist:
            post = Post(url=url)
        post.from_dict(data)
        if save:
            post.save()
        return post

    def from_dict(self, data):
        """Update instance based on dict data."""
        self.author_image_url = data.get("author_image_url", self.author_image_url)
        self.author_name = data.get("author_name", self.author_name)
        self.published_at = data.get("published_at", self.published_at)
        if "author_image_url" in data:
            self.author_image_url = data.get("author_image_url") or ""
        self.title = data.get("title", self.title)
        self.url = data.get("url", self.url)
