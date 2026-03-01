"""GitHub app comment model."""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.common.utils import truncate


class Comment(BulkSaveModel, TimestampedModel):
    """Represents a comment on a GitHub Issue."""

    class Meta:
        """Model options."""

        db_table = "github_comments"
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ("-nest_created_at",)

    github_id = models.BigIntegerField(unique=True, verbose_name="Github ID")
    created_at = models.DateTimeField(verbose_name="Created at", null=True, blank=True)
    updated_at = models.DateTimeField(
        verbose_name="Updated at", null=True, blank=True, db_index=True
    )
    author = models.ForeignKey(
        "github.User", on_delete=models.SET_NULL, null=True, related_name="comments"
    )
    body = models.TextField(verbose_name="Body")

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        """Return a string representation of the comment."""
        return f"{self.author} - {truncate(self.body, 50)}"

    def from_github(self, gh_comment, author=None):
        """Populate fields from a GitHub API comment object."""
        field_mapping = {
            "body": "body",
            "created_at": "created_at",
            "updated_at": "updated_at",
        }

        for model_field, gh_field in field_mapping.items():
            value = getattr(gh_comment, gh_field, None)
            if value is not None:
                setattr(self, model_field, value)

        self.author = author

    @staticmethod
    def bulk_save(comments, fields=None):  # type: ignore[override]
        """Bulk save comments."""
        BulkSaveModel.bulk_save(Comment, comments, fields=fields)

    @staticmethod
    def update_data(gh_comment, *, author=None, content_object=None, save: bool = True):
        """Update or create a Comment instance from a GitHub comment object.

        Args:
            gh_comment (github.IssueComment.IssueComment): GitHub comment object.
            author (User, optional): Comment author. Defaults to None.
            content_object (GenericForeignKey, optional): Content object. Defaults to None.
            save (bool, optional): Whether to save the instance immediately. Defaults to True.

        Returns:
            Comment: The updated or newly created Comment instance.

        """
        try:
            comment = Comment.objects.get(github_id=gh_comment.id)
        except Comment.DoesNotExist:
            comment = Comment(github_id=gh_comment.id)

        comment.from_github(gh_comment, author=author)

        if content_object is not None:
            comment.content_object = content_object

        if save:
            comment.save()

        return comment
