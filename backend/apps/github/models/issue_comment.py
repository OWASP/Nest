"""GitHub app issue comment model."""

from django.db import models

from apps.common.models import BulkSaveModel


class IssueComment(BulkSaveModel, models.Model):
    """Represents a comment on a GitHub issue."""

    github_id = models.BigIntegerField(unique=True)
    issue = models.ForeignKey("github.Issue", on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        "github.User", on_delete=models.SET_NULL, null=True, related_name="issue_comments"
    )
    body = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    def __str__(self):
        """Return a string representation of the issue comment."""
        return f"{self.issue} - {self.author} - {self.body}"

    def from_github(self, gh_comment, issue=None, author=None):
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

        self.issue = issue
        self.author = author

    @staticmethod
    def bulk_save(comments, fields=None):  # type: ignore[override]
        """Bulk save comments."""
        BulkSaveModel.bulk_save(IssueComment, comments, fields=fields)

    @staticmethod
    def update_data(gh_comment, *, issue=None, author=None, save=True):
        """Update IssueComment data.

        Args:
            gh_comment (github.IssueComment.IssueComment): GitHub comment object.
            issue (Issue, optional): Related issue. Defaults to None.
            author (User, optional): Comment author. Defaults to None.
            save (bool, optional): Whether to save the instance. Defaults to True.

        """
        try:
            comment = IssueComment.objects.get(github_id=gh_comment.id)
        except IssueComment.DoesNotExist:
            comment = IssueComment(github_id=gh_comment.id)

        comment.from_github(gh_comment, issue, author)

        if save:
            comment.save()

        return comment
