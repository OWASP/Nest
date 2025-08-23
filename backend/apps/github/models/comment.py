"""GitHub app comment model."""

from django.db import models

from apps.common.models import BulkSaveModel


class Comment(BulkSaveModel, models.Model):
    """Represents a comment on a GitHub entity (Issue, PR, etc.)."""

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    github_id = models.BigIntegerField(unique=True)
    author = models.ForeignKey(
        "github.User", on_delete=models.SET_NULL, null=True, related_name="comments"
    )
    body = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    def __str__(self):
        """Return a string representation of the comment."""
        return f"{self.author} - {self.body[:40]}"

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
    def update_data(gh_comment, *, author=None, save: bool = True):
        """Update or create a Comment instance from a GitHub comment object.

        Args:
            gh_comment (github.IssueComment.IssueComment): GitHub comment object.
            author (User, optional): Comment author. Defaults to None.
            save (bool, optional): Whether to save the instance immediately. Defaults to True.

        Returns:
            Comment: The updated or newly created Comment instance.

        """
        try:
            comment = Comment.objects.get(github_id=gh_comment.id)
        except Comment.DoesNotExist:
            comment = Comment(github_id=gh_comment.id)

        comment.from_github(gh_comment, author=author)

        if save:
            comment.save()

        return comment
