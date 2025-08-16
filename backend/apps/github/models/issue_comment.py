"""GitHub app issue comment model."""

from django.db import models


class IssueComment(models.Model):
    """Represents a comment on a GitHub issue."""

    github_id = models.BigIntegerField(unique=True)
    issue = models.ForeignKey("github.Issue", on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        "github.User", on_delete=models.SET_NULL, null=True, related_name="issue_comments"
    )
    body = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    @classmethod
    def update_data(cls, gh_comment, issue_obj, author_obj):
        """Create or update an IssueComment instance from a GitHub API object."""
        comment, _ = cls.objects.update_or_create(
            github_id=gh_comment.id,
            defaults={
                "issue": issue_obj,
                "author": author_obj,
                "body": gh_comment.body,
                "created_at": gh_comment.created_at,
                "updated_at": gh_comment.updated_at,
            },
        )
        return comment

    def __str__(self):
        """Return a string representation of the issue comment."""
        return f"{self.issue} - {self.author} - {self.body}"
