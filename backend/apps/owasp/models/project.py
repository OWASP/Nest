"""OWASP app project models."""

from __future__ import annotations

import datetime
from functools import lru_cache
from typing import TYPE_CHECKING

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.indexes import GinIndex, OpClass
from django.db import models
from django.utils import timezone

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.common.utils import get_absolute_url
from apps.core.models.prompt import Prompt
from apps.github.models.issue import Issue
from apps.github.models.milestone import Milestone
from apps.github.models.pull_request import PullRequest
from apps.github.models.release import Release
from apps.owasp.models.common import RepositoryBasedEntityModel
from apps.owasp.models.enums.project import (
    ProjectLevel,
    ProjectType,
    validate_audience,
)
from apps.owasp.models.managers.project import ActiveProjectManager
from apps.owasp.models.mixins.project import ProjectIndexMixin

if TYPE_CHECKING:
    from apps.owasp.models.entity_member import EntityMember
    from apps.owasp.models.project_health_metrics import ProjectHealthMetrics

MAX_LEADERS_COUNT = 5


class Project(
    BulkSaveModel,
    ProjectIndexMixin,
    RepositoryBasedEntityModel,
    TimestampedModel,
):
    """Project model."""

    objects = models.Manager()
    active_projects = ActiveProjectManager()

    class Meta:
        db_table = "owasp_projects"
        indexes = [
            models.Index(fields=["-created_at"], name="project_created_at_desc_idx"),
            models.Index(fields=["-updated_at"], name="project_updated_at_desc_idx"),
            GinIndex(
                fields=["name"],
                name="project_name_gin_idx",
                opclasses=["gin_trgm_ops"],
                condition=models.Q(is_active=True),
            ),
            GinIndex(
                OpClass(
                    models.functions.Cast("leaders_raw", models.TextField()), name="gin_trgm_ops"
                ),
                name="project_leaders_raw_gin_idx",
            ),
        ]
        verbose_name_plural = "Projects"

    audience = models.JSONField(
        verbose_name="Audience",
        default=list,
        blank=True,
        validators=[validate_audience],
    )
    level = models.CharField(
        verbose_name="Level",
        max_length=20,
        choices=ProjectLevel.choices,
        default=ProjectLevel.OTHER,
    )
    level_raw = models.CharField(verbose_name="Level raw", max_length=50, default="")

    type = models.CharField(
        verbose_name="Type",
        max_length=20,
        choices=ProjectType.choices,
        default=ProjectType.OTHER,
    )
    type_raw = models.CharField(verbose_name="Type raw", max_length=100, default="")

    # These are synthetic fields generated based on related repositories data.
    commits_count = models.PositiveIntegerField(verbose_name="Commits", default=0)
    contributors_count = models.PositiveIntegerField(verbose_name="Contributors", default=0)
    forks_count = models.PositiveIntegerField(verbose_name="Forks", default=0)
    open_issues_count = models.PositiveIntegerField(verbose_name="Open issues", default=0)
    releases_count = models.PositiveIntegerField(verbose_name="Releases", default=0)
    stars_count = models.PositiveIntegerField(verbose_name="Stars", default=0)
    subscribers_count = models.PositiveIntegerField(verbose_name="Subscribers", default=0)
    watchers_count = models.PositiveIntegerField(verbose_name="Watchers", default=0)
    issues_count = models.PositiveIntegerField(verbose_name="Issues", default=0)
    unanswered_issues_count = models.PositiveIntegerField(
        verbose_name="Unanswered Issues", default=0
    )
    unassigned_issues_count = models.PositiveIntegerField(
        verbose_name="Unassigned Issues", default=0
    )
    active_issues_count = models.PositiveIntegerField(
        verbose_name="Open Issues Past 90 Days", default=0
    )

    languages = models.JSONField(verbose_name="Languages", default=list, blank=True, null=True)
    licenses = models.JSONField(verbose_name="Licenses", default=list, blank=True, null=True)
    topics = models.JSONField(verbose_name="Topics", default=list, blank=True, null=True)

    created_at = models.DateTimeField(verbose_name="Created at", blank=True, null=True)
    released_at = models.DateTimeField(verbose_name="Released at", blank=True, null=True)
    pushed_at = models.DateTimeField(verbose_name="Pushed at", blank=True, null=True)
    updated_at = models.DateTimeField(verbose_name="Updated at", blank=True, null=True)

    custom_tags = models.JSONField(verbose_name="Custom tags", default=list, blank=True)
    track_issues = models.BooleanField(verbose_name="Track issues", default=True)

    contribution_data = models.JSONField(
        verbose_name="Contribution Data",
        default=dict,
        blank=True,
        null=True,
        help_text="Daily contribution counts (YYYY-MM-DD -> count mapping)",
    )
    contribution_stats = models.JSONField(
        verbose_name="Contribution Statistics",
        default=dict,
        blank=True,
        null=True,
        help_text="Detailed contribution breakdown (commits, issues, pull requests, releases)",
    )

    # GKs.
    members = GenericRelation("owasp.EntityMember")

    # FKs.
    owasp_repository = models.ForeignKey(
        "github.Repository",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="+",
    )

    # M2Ms.
    organizations = models.ManyToManyField(
        "github.Organization",
        verbose_name="Organizations",
        blank=True,
    )
    owners = models.ManyToManyField(
        "github.User",
        verbose_name="Owners",
        blank=True,
    )
    repositories = models.ManyToManyField(
        "github.Repository",
        verbose_name="Repositories",
        blank=True,
    )
    issues = models.ManyToManyField(
        "github.Issue",
        verbose_name="Issues",
        blank=True,
    )

    def __str__(self) -> str:
        """Project human readable representation."""
        return f"{self.name or self.key}"

    @property
    def entity_leaders(self) -> list[EntityMember]:
        """Get the list of project leaders.

        Returns:
            list[EntityMember]: Up to the top leaders limited by `MAX_LEADERS_COUNT`.

        """
        return super().entity_leaders[:MAX_LEADERS_COUNT]

    @property
    def health_score(self) -> float | None:
        """Get the latest computed health score for the project.

        Returns:
            float | None: The most recent health score, or None if unavailable.

        """
        return self.last_health_metrics.score if self.last_health_metrics else None

    @property
    def is_code_type(self) -> bool:
        """Check if the project's type is CODE.

        Returns:
            bool: True if the project type equals `ProjectType.CODE`.

        """
        return self.type == ProjectType.CODE

    @property
    def is_documentation_type(self) -> bool:
        """Check if the project's type is DOCUMENTATION.

        Returns:
            bool: True if the project type equals `ProjectType.DOCUMENTATION`.

        """
        return self.type == ProjectType.DOCUMENTATION

    @property
    def is_funding_requirements_compliant(self) -> bool:
        """Check if the project complies with funding requirements.

        Returns:
            bool: True if all related repositories are funding-policy compliant.

        """
        return not self.repositories.filter(is_funding_policy_compliant=False).exists()

    @property
    def is_leader_requirements_compliant(self) -> bool:
        """Check if the project satisfies OWASP leader requirements.

        Returns:
            bool: True if the project has multiple leaders (more than one).

        """
        # https://owasp.org/www-committee-project/#div-practice
        # Have multiple Project Leaders who are not all employed by the same company.
        return self.leaders_count > 1

    @property
    def is_tool_type(self) -> bool:
        """Check if the project's type is TOOL.

        Returns:
            bool: True if the project type equals `ProjectType.TOOL`.

        """
        return self.type == ProjectType.TOOL

    @property
    def last_health_metrics(self) -> ProjectHealthMetrics | None:
        """Get the most recent health metrics for the project.

        Returns:
            ProjectHealthMetrics | None: Latest metrics record or None if missing.

        """
        return self.health_metrics.order_by("-nest_created_at").first()

    @property
    def leaders_count(self) -> int:
        """Get the number of project leaders.

        Returns:
            int: Count of leaders derived from `leaders_raw`.

        """
        return len(self.leaders_raw)

    @property
    def nest_key(self) -> str:
        """Get the Nest-specific project key.

        Returns:
            str: The project key with the "www-project-" prefix removed.

        """
        return self.key.replace("www-project-", "")

    @property
    def nest_url(self) -> str:
        """Get the absolute Nest URL for this project.

        Returns:
            str: The full Nest URL pointing to the project's page.

        """
        return get_absolute_url(f"/projects/{self.nest_key}")

    @property
    def open_issues(self):
        """Get open issues across the project's repositories.

        Returns:
            QuerySet[Issue]: A queryset of open issues with repository related data.

        """
        return Issue.open_issues.filter(
            repository__in=self.repositories.all(),
        ).select_related(
            "repository",
        )

    @property
    def open_pull_requests_count(self) -> int:
        """Get the number of open pull requests.

        Returns:
            int: Count of pull requests currently in the "open" state.

        """
        return self.pull_requests.filter(state="open").count()

    @property
    def owasp_page_last_updated_at(self) -> datetime.datetime | None:
        """Get the last updated timestamp of the project's OWASP page.

        Returns:
            datetime.datetime | None: The OWASP page's last update time, or None.

        """
        return self.owasp_repository.updated_at if self.owasp_repository else None

    @property
    def pull_requests(self):
        """Get pull requests across the project's repositories.

        Returns:
            QuerySet[PullRequest]: A queryset of pull requests with related data.

        """
        return (
            PullRequest.objects.filter(
                repository__in=self.repositories.all(),
            )
            .select_related(
                "author",
                "milestone",
                "repository__organization",
                "repository",
            )
            .prefetch_related(
                "assignees",
                "labels",
            )
        )

    @property
    def pull_requests_count(self) -> int:
        """Get the total number of pull requests.

        Returns:
            int: Count of pull requests across the project's repositories.

        """
        return self.pull_requests.count()

    @property
    def pull_request_last_created_at(self) -> datetime.datetime | None:
        """Get the most recent pull request creation timestamp.

        Returns:
            datetime.datetime | None: Latest `created_at` timestamp, or None.

        """
        return self.pull_requests.aggregate(
            models.Max("created_at"),
        )["created_at__max"]

    @property
    def published_releases(self) -> models.QuerySet[Release]:
        """Get published releases across the project's repositories.

        Returns:
            QuerySet[Release]: A queryset of non-draft releases with related data.

        """
        return Release.objects.filter(
            is_draft=False,
            published_at__isnull=False,
            repository__in=self.repositories.all(),
        ).select_related(
            "author",
            "repository",
            "repository__organization",
        )

    @property
    def recent_milestones(self) -> models.QuerySet[Milestone]:
        """Get milestones across the project's repositories.

        Returns:
            QuerySet[Milestone]: A queryset of milestones with related data.

        """
        return (
            Milestone.objects.filter(
                repository__in=self.repositories.all(),
            )
            .select_related(
                "author",
                "repository",
            )
            .prefetch_related(
                "labels",
            )
        )

    @property
    def recent_releases_count(self) -> int:
        """Get the number of recent releases.

        Returns:
            int: Count of releases published recently.

        """
        recent_period = timezone.now() - datetime.timedelta(days=60)
        return self.published_releases.filter(
            published_at__gte=recent_period,
        ).count()

    @property
    def repositories_count(self) -> int:
        """Get the number of repositories associated with this project.

        Returns:
            int: Count of repositories linked to the project.

        """
        return self.repositories.count()

    def deactivate(self) -> None:
        """Deactivate project."""
        self.is_active = False
        self.save(update_fields=("is_active",))

    def from_github(self, repository) -> None:
        """Update instance based on GitHub repository data.

        Args:
            repository (github.Repository): The GitHub repository instance.

        """
        self.owasp_repository = repository

        project_metadata = RepositoryBasedEntityModel.from_github(
            self,
            {
                "description": "pitch",
                "name": "title",
                "tags": "tags",
            },
        )

        # Level.
        project_level = project_metadata.get("level")
        if project_level:
            level_mapping = {
                2: ProjectLevel.INCUBATOR,
                3: ProjectLevel.LAB,
                3.5: ProjectLevel.PRODUCTION,
                4: ProjectLevel.FLAGSHIP,
            }
            self.level = level_mapping.get(project_level) or ProjectLevel.OTHER
            self.level_raw = project_level

        # Type.
        project_type = project_metadata.get("type")
        if project_type:
            self.type = project_type if project_type in ProjectType.values else ProjectType.OTHER
            self.type_raw = project_type

        self.created_at = repository.created_at
        self.updated_at = repository.updated_at

    def get_absolute_url(self):
        """Get absolute URL for project."""
        return f"/projects/{self.nest_key}"

    def save(self, *args, **kwargs) -> None:
        """Save the project instance."""
        if self.is_active and not self.summary and (prompt := Prompt.get_owasp_project_summary()):
            self.generate_summary(prompt=prompt)

        super().save(*args, **kwargs)

    @staticmethod
    @lru_cache
    def active_projects_count():
        """Return active projects count."""
        return Project.objects.filter(
            has_active_repositories=True,
            is_active=True,
        ).count()

    @staticmethod
    def bulk_save(projects: list, fields: list | None = None) -> None:  # type: ignore[override]
        """Bulk save projects.

        Args:
            projects (list[Project]): List of Project instances to save.
            fields (list[str], optional): List of fields to update.

        """
        BulkSaveModel.bulk_save(Project, projects, fields=fields)

    @staticmethod
    def update_data(gh_repository, repository, *, save: bool = True) -> Project:
        """Update project data from GitHub repository.

        Args:
            gh_repository (github.Repository): The GitHub repository instance.
            repository (github.Repository): The repository data to update from.
            save (bool, optional): Whether to save the instance.

        Returns:
            Project: The updated Project instance.

        """
        key = gh_repository.name.lower()
        try:
            project = Project.objects.get(key=key)
        except Project.DoesNotExist:
            project = Project(key=key)

        project.from_github(repository)
        if save:
            project.save()

        return project
