"""Github app issue model."""

from functools import lru_cache

from django.db import models

from apps.common.index import IndexBase
from apps.common.models import BulkSaveModel, TimestampedModel
from apps.common.open_ai import OpenAi
from apps.core.models.prompt import Prompt
from apps.github.models.common import NodeModel
from apps.github.models.managers.issue import OpenIssueManager
from apps.github.models.mixins import IssueIndexMixin


class Issue(BulkSaveModel, IssueIndexMixin, NodeModel, TimestampedModel):
    """Issue model."""

    objects = models.Manager()
    open_issues = OpenIssueManager()

    class Meta:
        db_table = "github_issues"
        ordering = ("-updated_at", "-state")
        verbose_name_plural = "Issues"

    class State(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"

    title = models.CharField(verbose_name="Title", max_length=1000)
    body = models.TextField(verbose_name="Body", default="")

    summary = models.TextField(
        verbose_name="Summary", default="", blank=True
    )  # AI generated summary
    hint = models.TextField(verbose_name="Hint", default="", blank=True)  # AI generated hint
    state = models.CharField(
        verbose_name="State", max_length=20, choices=State, default=State.OPEN
    )
    state_reason = models.CharField(
        verbose_name="State reason", max_length=200, default="", blank=True
    )
    url = models.URLField(verbose_name="URL", max_length=500, default="")
    number = models.PositiveBigIntegerField(verbose_name="Number", default=0)
    sequence_id = models.PositiveBigIntegerField(verbose_name="Issue ID", default=0)

    is_locked = models.BooleanField(verbose_name="Is locked", default=False)
    lock_reason = models.CharField(
        verbose_name="Lock reason", max_length=200, default="", blank=True
    )

    comments_count = models.PositiveIntegerField(verbose_name="Comments", default=0)

    closed_at = models.DateTimeField(verbose_name="Closed at", blank=True, null=True)
    created_at = models.DateTimeField(verbose_name="Created at")
    updated_at = models.DateTimeField(verbose_name="Updated at", db_index=True)

    # FKs.
    author = models.ForeignKey(
        "github.User",
        verbose_name="Author",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_issues",
    )
    repository = models.ForeignKey(
        "github.Repository",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="issues",
    )

    # M2Ms.
    assignees = models.ManyToManyField(
        "github.User",
        verbose_name="Assignees",
        related_name="issue",
        blank=True,
    )
    labels = models.ManyToManyField(
        "github.Label",
        verbose_name="Labels",
        related_name="issue",
        blank=True,
    )

    def __str__(self):
        """Issue human readable representation."""
        return f"{self.title} by {self.author}"

    @property
    def is_indexable(self):
        """Issues to index."""
        return (
            self.state == self.State.OPEN
            and not self.is_locked
            and self.repository.is_indexable
            and self.repository.track_issues
            and self.project.track_issues
        )

    @property
    def project(self):
        """Return project."""
        return self.repository.project

    @property
    def repository_id(self):
        """Return repository ID."""
        return self.repository.id

    def from_github(self, gh_issue, author=None, repository=None):
        """Update instance based on GitHub issue data."""
        field_mapping = {
            "body": "body",
            "comments_count": "comments",
            "closed_at": "closed_at",
            "created_at": "created_at",
            "is_locked": "locked",
            "lock_reason": "active_lock_reason",
            "number": "number",
            "sequence_id": "id",
            "state": "state",
            "state_reason": "state_reason",
            "title": "title",
            "updated_at": "updated_at",
            "url": "html_url",
        }

        # Direct fields.
        for model_field, gh_field in field_mapping.items():
            value = getattr(gh_issue, gh_field)
            if value is not None:
                setattr(self, model_field, value)

        # Author.
        self.author = author

        # Repository.
        self.repository = repository

    def generate_hint(self, open_ai=None, max_tokens=1000):
        """Generate issue hint."""
        if self.id and not self.is_indexable:
            return

        open_ai = open_ai or OpenAi()
        open_ai.set_input(f"{self.title}\r\n{self.body}")
        open_ai.set_max_tokens(max_tokens).set_prompt(Prompt.get_github_issue_hint())
        self.hint = open_ai.complete() or ""

    def generate_summary(self, open_ai=None, max_tokens=500):
        """Generate issue summary."""
        if self.id and not self.is_indexable:
            return

        open_ai = open_ai or OpenAi()
        open_ai.set_input(f"{self.title}\r\n{self.body}")
        open_ai.set_max_tokens(max_tokens).set_prompt(
            Prompt.get_github_issue_documentation_project_summary()
            if self.project.is_documentation_type
            else Prompt.get_github_issue_project_summary()
        )
        self.summary = open_ai.complete() or ""

    def save(self, *args, **kwargs):
        """Save issue."""
        if not self.hint:
            self.generate_hint()

        if not self.summary:
            self.generate_summary()

        super().save(*args, **kwargs)

    @staticmethod
    def bulk_save(issues, fields=None):
        """Bulk save issues."""
        BulkSaveModel.bulk_save(Issue, issues, fields=fields)

    @staticmethod
    @lru_cache
    def open_issues_count():
        """Return open issues count."""
        return IndexBase.get_total_count("issues")

    @staticmethod
    def update_data(gh_issue, author=None, repository=None, save=True):
        """Update issue data."""
        issue_node_id = Issue.get_node_id(gh_issue)
        try:
            issue = Issue.objects.get(node_id=issue_node_id)
        except Issue.DoesNotExist:
            issue = Issue(node_id=issue_node_id)

        issue.from_github(gh_issue, author=author, repository=repository)
        if save:
            issue.save()

        return issue
