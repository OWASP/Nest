"""Github app pull requests model."""

from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.github.models.common import NodeModel
from apps.github.models.managers.pullrequest import OpenPullRequestManager
from apps.github.models.mixins import IssueIndexMixin

# AI to create summary or hint!
# from apps.common.open_ai import OpenAi
# from apps.core.models.prompt import Prompt


class PullRequest(BulkSaveModel, IssueIndexMixin, NodeModel, TimestampedModel):
    """Pull request Model."""

    class Meta:
        db_table = "github_pull_requests"
        ordering = ("-updated_at", "-state")
        verbose_name_plural = "Pull Requests"

    class State(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"

    objects = models.Manager()
    open_pull_requests = OpenPullRequestManager()

    title = models.CharField(verbose_name="Title", max_length=1000)
    body = models.TextField(verbose_name="Body", default="")

    state = models.CharField(verbose_name="State", max_length=6, choices=State, default=State.OPEN)

    url = models.URLField(verbose_name="URL", max_length=500, default="")

    number = models.PositiveBigIntegerField(verbose_name="Number", default=0)

    sequence_id = models.PositiveBigIntegerField(verbose_name="Pull Requests ID", default=0)

    closed_at = models.DateTimeField(verbose_name="Closed at", blank=True, null=True)
    created_at = models.DateTimeField(verbose_name="Created at")
    updated_at = models.DateTimeField(verbose_name="Updated at", db_index=True)
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

    def __str__(self):
        """Issue human readable representation."""
        return f"{self.title} by {self.author}"

    @property
    def project(self):
        """Return project."""
        return self.repository.project

    @property
    def repository_id(self):
        """Return repository ID."""
        return self.repository.id

    def from_github(self, gh_pull_request, author=None, repository=None):
        """Update instance based on GitHub issue data."""
        field_mapping = {
            "body": "body",
            "number": "number",
            "sequence_id": "id",
            "state": "state",
            "title": "title",
            "url": "html_url",
            "created_at": "created_at",
            "updated_at": "updated_at",
            "merged_at": "merged_at",
            "closed_at": "closed_at",
        }

        # Direct fields.
        for model_field, gh_field in field_mapping.items():
            value = getattr(gh_pull_request, gh_field)
            if value is not None:
                setattr(self, model_field, value)

        # Author.
        self.author = author

        # Repository.
        self.repository = repository

    def save(self, *args, **kwargs):
        """Save method for PullRequest model."""
        super().save(*args, **kwargs)

    @staticmethod
    def bulk_save(pull_requests, fields=None):
        """Bulk save issues."""
        BulkSaveModel.bulk_save(PullRequest, pull_requests, fields=fields)

    @staticmethod
    def update_data(gh_pull_request, author=None, repository=None, save=True):
        """Update Pull Request data."""
        pull_request_node_id = PullRequest.get_node_id(gh_pull_request)
        try:
            pull_request = PullRequest.objects.get(node_id=pull_request_node_id)
        except PullRequest.DoesNotExist:
            pull_request = PullRequest(node_id=pull_request_node_id)

        pull_request.from_github(gh_pull_request, author=author, repository=repository)
        if save:
            pull_request.save()
        return pull_request
