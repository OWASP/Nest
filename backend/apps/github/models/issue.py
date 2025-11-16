"""Github app issue model."""

from __future__ import annotations

from functools import lru_cache

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from apps.common.index import IndexBase
from apps.common.models import BulkSaveModel
from apps.common.open_ai import OpenAi
from apps.core.models.prompt import Prompt
from apps.github.models.managers.issue import OpenIssueManager

from .generic_issue_model import GenericIssueModel


class Issue(GenericIssueModel):
    """Issue model."""

    objects = models.Manager()
    open_issues = OpenIssueManager()

    class Meta:
        db_table = "github_issues"
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["number"]),
        ]
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

    comments = GenericRelation("github.Comment", related_query_name="issue")

    milestone = models.ForeignKey(
        "github.Milestone",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="issues",
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

    @property
    def latest_comment(self):
        """Get the latest comment for this issue.

        Returns:
            Comment | None: The most recently created comment, or None if no comments exist.

        """
        return self.comments.order_by("-nest_created_at").first()

    def from_github(self, gh_issue, *, author=None, milestone=None, repository=None):
        """Update the instance based on GitHub issue data.

        Args:
            gh_issue (github.Issue.Issue): The GitHub issue object.
            author (User, optional): The author of the issue.
            milestone (Milestone, optional): The milestone related to the issue.
            repository (Repository, optional): The repository instance.

        """
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

        # Milestone.
        self.milestone = milestone

        # Repository.
        self.repository = repository

    def generate_hint(self, open_ai: OpenAi | None = None, max_tokens: int = 1000) -> None:
        """Generate a hint for the issue using AI.

        Args:
            open_ai (OpenAi, optional): The OpenAI instance.
            max_tokens (int, optional): The maximum number of tokens for the AI response.

        """
        if not self.is_indexable or not (prompt := Prompt.get_github_issue_hint()):
            return

        open_ai = open_ai or OpenAi()
        open_ai.set_input(f"{self.title}\r\n{self.body}")
        open_ai.set_max_tokens(max_tokens).set_prompt(prompt)
        self.hint = open_ai.complete() or ""

    def generate_summary(self, open_ai: OpenAi | None = None, max_tokens: int = 500) -> None:
        """Generate a summary for the issue using AI.

        Args:
            open_ai (OpenAi, optional): The OpenAI instance.
            max_tokens (int, optional): The maximum number of tokens for the AI response.

        """
        if not self.is_indexable or not (
            prompt := (
                Prompt.get_github_issue_documentation_project_summary()
                if self.project.is_documentation_type
                else Prompt.get_github_issue_project_summary()
            )
        ):
            return

        open_ai = open_ai or OpenAi()
        open_ai.set_input(f"{self.title}\r\n{self.body}")
        open_ai.set_max_tokens(max_tokens).set_prompt(prompt)
        self.summary = open_ai.complete() or ""

    def save(self, *args, **kwargs) -> None:
        """Save issue."""
        if self.is_open:
            if not self.hint:
                self.generate_hint()

            if not self.summary:
                self.generate_summary()

        super().save(*args, **kwargs)

    @staticmethod
    def bulk_save(issues, fields=None) -> None:  # type: ignore[override]
        """Bulk save issues."""
        BulkSaveModel.bulk_save(Issue, issues, fields=fields)

    @staticmethod
    @lru_cache
    def open_issues_count():
        """Return open issues count."""
        return IndexBase.get_total_count("issues")

    @staticmethod
    def update_data(gh_issue, *, author=None, milestone=None, repository=None, save: bool = True):
        """Update issue data.

        Args:
            gh_issue (github.Issue.Issue): The GitHub issue object.
            author (User, optional): The author of the issue.
            milestone (Milestone, optional): The milestone related to the issue.
            repository (Repository, optional): The repository instance.
            save (bool, optional): Whether to save the instance.

        Returns:
            Issue: The updated or created issue instance.

        """
        issue_node_id = Issue.get_node_id(gh_issue)
        try:
            issue = Issue.objects.get(node_id=issue_node_id)
        except Issue.DoesNotExist:
            issue = Issue(node_id=issue_node_id)

        issue.from_github(gh_issue, author=author, milestone=milestone, repository=repository)
        if save:
            issue.save()

        return issue
