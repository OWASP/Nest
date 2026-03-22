"""Github app Milestone model."""

from django.db import models

from apps.common.models import BulkSaveModel
from apps.github.models.generic_issue_model import GenericIssueModel
from apps.github.models.managers.milestone import ClosedMilestoneManager, OpenMilestoneManager


class Milestone(GenericIssueModel):
    """GitHub Milestone model."""

    objects = models.Manager()
    open_milestones = OpenMilestoneManager()
    closed_milestones = ClosedMilestoneManager()

    class Meta:
        """Model options."""

        db_table = "github_milestones"
        verbose_name_plural = "Milestones"
        ordering = ["-updated_at", "-state"]

        indexes = [
            models.Index(fields=["-created_at"], name="github_milestone_created_at"),
            models.Index(fields=["-updated_at"], name="github_milestone_updated_at"),
        ]

    open_issues_count = models.PositiveIntegerField(default=0)
    closed_issues_count = models.PositiveIntegerField(default=0)
    due_on = models.DateTimeField(blank=True, null=True)

    # FKs.
    author = models.ForeignKey(
        "github.User",
        on_delete=models.CASCADE,
        related_name="milestones",
        blank=True,
        null=True,
    )

    repository = models.ForeignKey(
        "github.Repository",
        on_delete=models.CASCADE,
        related_name="milestones",
        blank=True,
        null=True,
    )

    # M2Ms.
    labels = models.ManyToManyField(
        "github.Label",
        related_name="milestones",
        blank=True,
    )

    def from_github(self, gh_milestone, author=None, repository=None) -> None:
        """Populate Milestone from GitHub API response.

        Args:
            gh_milestone (github.Milestone.Milestone): GitHub milestone object.
            author (User, optional): Author of the milestone. Defaults to None.
            repository (Repository, optional): Repository of the milestone. Defaults to None.

        """
        field_mapping = {
            "body": "description",
            "closed_at": "closed_at",
            "closed_issues_count": "closed_issues",
            "created_at": "created_at",
            "due_on": "due_on",
            "number": "number",
            "open_issues_count": "open_issues",
            "state": "state",
            "title": "title",
            "updated_at": "updated_at",
            "url": "html_url",
        }

        for model_field, gh_field in field_mapping.items():
            value = getattr(gh_milestone, gh_field)
            if value is not None:
                setattr(self, model_field, value)

        self.author = author
        self.repository = repository

    @staticmethod
    def bulk_save(milestones, fields=None):
        """Bulk save milestones."""
        BulkSaveModel.bulk_save(Milestone, milestones, fields=fields)

    @staticmethod
    def update_data(gh_milestone, *, author=None, repository=None, save=True):
        """Update Milestone data.

        Args:
            gh_milestone (github.Milestone.Milestone): GitHub milestone object.
            author (User, optional): Author of the issue. Defaults to None.
            repository (Repository, optional): Repository of the issue. Defaults to None.
            save (bool, optional): Whether to save the instance after updating. Defaults to True.

        """
        milestone_node_id = Milestone.get_node_id(gh_milestone)
        try:
            milestone = Milestone.objects.get(node_id=milestone_node_id)
        except Milestone.DoesNotExist:
            milestone = Milestone(node_id=milestone_node_id)

        milestone.from_github(gh_milestone, author, repository)
        if save:
            milestone.save()

        return milestone
