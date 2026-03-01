"""Github app pull requests model."""

from django.db import models

from apps.common.models import BulkSaveModel
from apps.github.models.managers.pull_request import OpenPullRequestManager

from .generic_issue_model import GenericIssueModel


class PullRequest(GenericIssueModel):
    """Pull request Model."""

    objects = models.Manager()
    open_pull_requests = OpenPullRequestManager()

    class Meta:
        """Model options."""

        db_table = "github_pull_requests"
        indexes = [
            models.Index(fields=["-created_at"]),
        ]
        ordering = ("-updated_at", "-state")
        verbose_name_plural = "Pull Requests"

    merged_at = models.DateTimeField(verbose_name="Merged at", blank=True, null=True)

    # FKs.
    author = models.ForeignKey(
        "github.User",
        verbose_name="Author",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_pull_requests",
    )
    milestone = models.ForeignKey(
        "github.Milestone",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="pull_requests",
    )
    repository = models.ForeignKey(
        "github.Repository",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="pull_requests",
    )

    # M2Ms.
    assignees = models.ManyToManyField(
        "github.User",
        verbose_name="Assignees",
        related_name="assigned_pull_requests",
        blank=True,
    )
    labels = models.ManyToManyField(
        "github.Label",
        verbose_name="Labels",
        related_name="pull_request_labels",
        blank=True,
    )
    related_issues = models.ManyToManyField(
        "github.Issue",
        verbose_name="Issues",
        related_name="pull_requests",
        blank=True,
    )

    def from_github(self, gh_pull_request, *, author=None, milestone=None, repository=None):
        """Update the instance based on GitHub pull request data.

        Args:
            gh_pull_request (github.PullRequest.PullRequest): The GitHub pull request object.
            author (User, optional): The author of the pull request.
            repository (Repository, optional): The repository instance.
            milestone (Milestone, optional): The milestone related to the pull request.

        """
        field_mapping = {
            "body": "body",
            "closed_at": "closed_at",
            "created_at": "created_at",
            "merged_at": "merged_at",
            "number": "number",
            "sequence_id": "id",
            "state": "state",
            "title": "title",
            "updated_at": "updated_at",
            "url": "html_url",
        }

        # Direct fields.
        for model_field, gh_field in field_mapping.items():
            value = getattr(gh_pull_request, gh_field)
            if value is not None:
                setattr(self, model_field, value)

        # Author.
        self.author = author

        # Milestone.
        self.milestone = milestone

        # Repository.
        self.repository = repository

    def save(self, *args, **kwargs) -> None:
        """Save Pull Request."""
        super().save(*args, **kwargs)

    @staticmethod
    def bulk_save(pull_requests, fields=None) -> None:  # type: ignore[override]
        """Bulk save pull requests."""
        BulkSaveModel.bulk_save(PullRequest, pull_requests, fields=fields)

    @staticmethod
    def update_data(
        gh_pull_request,
        *,
        author=None,
        milestone=None,
        repository=None,
        save: bool = True,
    ) -> "PullRequest":
        """Update pull request data.

        Args:
            gh_pull_request (github.PullRequest.PullRequest): The GitHub pull request object.
            author (User, optional): The author of the pull request.
            milestone (Milestone, optional): The milestone related to the pull request.
            repository (Repository, optional): The repository instance.
            save (bool, optional): Whether to save the instance.

        Returns:
            PullRequest: The updated or created pull request instance.

        """
        pull_request_node_id = PullRequest.get_node_id(gh_pull_request)
        try:
            pull_request = PullRequest.objects.get(node_id=pull_request_node_id)
        except PullRequest.DoesNotExist:
            pull_request = PullRequest(node_id=pull_request_node_id)

        pull_request.from_github(
            gh_pull_request, author=author, milestone=milestone, repository=repository
        )
        if save:
            pull_request.save()

        return pull_request
