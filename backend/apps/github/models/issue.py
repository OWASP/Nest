"""Github app issue model."""

from functools import lru_cache

from django.db import models

from apps.common.index import IndexBase
from apps.common.models import BulkSaveModel
from apps.common.open_ai import OpenAi
from apps.core.models.prompt import Prompt
from apps.github.models.managers.issue import OpenIssueManager

from .generic_issue_model import GenericIssueModel


class Issue(GenericIssueModel):
    """Issue model."""

    open_issues = OpenIssueManager()

    class Meta:
        db_table = "github_issues"
        ordering = ("-updated_at", "-state")
        verbose_name_plural = "Issues"

    summary = models.TextField(
        verbose_name="Summary", default="", blank=True
    )  # AI generated summary
    hint = models.TextField(verbose_name="Hint", default="", blank=True)  # AI generated hint

    state_reason = models.CharField(
        verbose_name="State reason", max_length=200, default="", blank=True
    )

    is_locked = models.BooleanField(verbose_name="Is locked", default=False)
    lock_reason = models.CharField(
        verbose_name="Lock reason", max_length=200, default="", blank=True
    )

    comments_count = models.PositiveIntegerField(verbose_name="Comments", default=0)

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

        if not (prompt := Prompt.get_github_issue_hint()):
            return

        open_ai = open_ai or OpenAi()
        open_ai.set_input(f"{self.title}\r\n{self.body}")
        open_ai.set_max_tokens(max_tokens).set_prompt(prompt)
        self.hint = open_ai.complete() or ""

    def generate_summary(self, open_ai=None, max_tokens=500):
        """Generate issue summary."""
        if self.id and not self.is_indexable:
            return

        prompt = (
            Prompt.get_github_issue_documentation_project_summary()
            if self.project.is_documentation_type
            else Prompt.get_github_issue_project_summary()
        )
        if not prompt:
            return

        open_ai = open_ai or OpenAi()
        open_ai.set_input(f"{self.title}\r\n{self.body}")
        open_ai.set_max_tokens(max_tokens).set_prompt(prompt)
        self.summary = open_ai.complete() or ""

    def save(self, *args, **kwargs):
        """Save issue."""
        if self.is_open:
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
