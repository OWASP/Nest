"""OWASP app post model."""

from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel


class Post(BulkSaveModel, TimestampedModel):

    class Meta:
        db_table = "owasp_post"
        verbose_name_plural = "Posts"

    author = models.CharField(verbose_name="Author name")
    author_image = models.URLField(verbose_name="Author image URL",blank=True,null=True)
    date = models.DateTimeField(verbose_name="Publication date")
    title = models.CharField(verbose_name="Title")
    url = models.URLField(verbose_name="URL",unique=True)
    
    
    def __str__(self):
        """Return human-readable representation."""
        return f"{self.title}"
    

    @staticmethod
    def bulk_save(posts, fields=None):
        """Bulk save posts."""
        BulkSaveModel.bulk_save(Post, posts, fields=fields)

    @staticmethod
    def recent_posts():
        """Get recent posts."""
        return Post.objects.all().order_by("-date")[:5]