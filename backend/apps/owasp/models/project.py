"""OWASP app project models."""

from __future__ import annotations

import datetime
from functools import lru_cache

from django.db import models
from django.utils import timezone

from apps.common.index import IndexBase
from apps.common.models import BulkSaveModel, TimestampedModel
from apps.common.utils import get_absolute_url
from apps.core.models.prompt import Prompt
from apps.github.models.issue import Issue
from apps.github.models.milestone import Milestone
from apps.github.models.pull_request import PullRequest
from apps.github.models.release import Release
from apps.owasp.models.common import RepositoryBasedEntityModel
from apps.owasp.models.managers.project import ActiveProjectManager
from apps.owasp.models.mixins.project import ProjectIndexMixin


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
        ]
        verbose_name_plural = "Projects"

    class ProjectLevel(models.TextChoices):
        OTHER = "other", "Other"
        INCUBATOR = "incubator", "Incubator"
        LAB = "lab", "Lab"
        PRODUCTION = "production", "Production"
        FLAGSHIP = "flagship", "Flagship"

    class ProjectType(models.TextChoices):
        # These projects provide tools, libraries, and frameworks that can be leveraged by
        # developers to enhance the security of their applications.
        CODE = "code", "Code"

        # These projects seek to communicate information or raise awareness about a topic in
        # application security. Note that documentation projects should focus on an online-first
        # deliverable, where appropriate, but can take any media form.
        DOCUMENTATION = "documentation", "Documentation"

        # Some projects fall outside the above categories. Most are created to offer OWASP
        # operational support.
        OTHER = "other", "Other"

        # These are typically software or utilities that help developers and security
        # professionals test, secure, or monitor applications.
        TOOL = "tool", "Tool"

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

    languages = models.JSONField(verbose_name="Languages", default=list, blank=True, null=True)
    licenses = models.JSONField(verbose_name="Licenses", default=list, blank=True, null=True)
    topics = models.JSONField(verbose_name="Topics", default=list, blank=True, null=True)

    created_at = models.DateTimeField(verbose_name="Created at", blank=True, null=True)
    released_at = models.DateTimeField(verbose_name="Released at", blank=True, null=True)
    pushed_at = models.DateTimeField(verbose_name="Pushed at", blank=True, null=True)
    updated_at = models.DateTimeField(verbose_name="Updated at", blank=True, null=True)

    custom_tags = models.JSONField(verbose_name="Custom tags", default=list, blank=True)
    track_issues = models.BooleanField(verbose_name="Track issues", default=True)

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

    def __str__(self) -> str:
        """Project human readable representation."""
        return f"{self.name or self.key}"

    @property
    def is_code_type(self) -> bool:
        """Indicate whether project has CODE type."""
        return self.type == self.ProjectType.CODE

    @property
    def is_documentation_type(self) -> bool:
        """Indicate whether project has DOCUMENTATION type."""
        return self.type == self.ProjectType.DOCUMENTATION

    @property
    def is_funding_requirements_compliant(self) -> bool:
        """Indicate whether project is compliant with funding requirements."""
        return not self.repositories.filter(is_funding_policy_compliant=False).exists()

    @property
    def is_leader_requirements_compliant(self) -> bool:
        """Indicate whether project is compliant with project leaders requirements."""
        # https://owasp.org/www-committee-project/#div-practice
        # Have multiple Project Leaders who are not all employed by the same company.
        return self.leaders_count > 1

    @property
    def is_tool_type(self) -> bool:
        """Indicate whether project has TOOL type."""
        return self.type == self.ProjectType.TOOL

    @property
    def issues(self):
        """Return issues."""
        return Issue.objects.filter(
            repository__in=self.repositories.all(),
        ).select_related(
            "repository",
        )

    @property
    def issues_count(self) -> int:
        """Return count of issues."""
        return self.issues.count()

    @property
    def nest_key(self) -> str:
        """Get Nest key."""
        return self.key.replace("www-project-", "")

    @property
    def nest_url(self) -> str:
        """Get Nest URL for project."""
        return get_absolute_url(f"projects/{self.nest_key}")

    @property
    def leaders_count(self) -> int:
        """Return the count of leaders."""
        return len(self.leaders_raw)

    @property
    def open_issues(self):
        """Return open issues."""
        return Issue.open_issues.filter(
            repository__in=self.repositories.all(),
        ).select_related(
            "repository",
        )

    @property
    def open_pull_requests_count(self) -> int:
        """Return count of open pull requests."""
        return self.pull_requests.filter(state="open").count()

    @property
    def owasp_page_last_updated_at(self) -> datetime.datetime | None:
        """Return the last updated date of the OWASP page."""
        return self.owasp_repository.updated_at if self.owasp_repository else None

    @property
    def pull_requests(self):
        """Return pull requests."""
        return PullRequest.objects.filter(
            repository__in=self.repositories.all(),
        ).select_related(
            "repository",
        )

    @property
    def pull_requests_count(self) -> int:
        """Return count of pull requests."""
        return self.pull_requests.count()

    @property
    def pull_request_last_created_at(self) -> datetime.datetime | None:
        """Return last created pull request."""
        return self.pull_requests.aggregate(
            models.Max("created_at"),
        )["created_at__max"]

    @property
    def published_releases(self):
        """Return project releases."""
        return Release.objects.filter(
            is_draft=False,
            published_at__isnull=False,
            repository__in=self.repositories.all(),
        ).select_related(
            "repository",
        )

    @property
    def recent_milestones(self):
        """Return recent milestones."""
        return Milestone.objects.filter(
            repository__in=self.repositories.all(),
        ).select_related(
            "repository",
        )

    @property
    def recent_releases_count(self) -> int:
        """Return count of recent releases per a specific period."""
        recent_period = timezone.now() - datetime.timedelta(days=60)
        return self.published_releases.filter(
            published_at__gte=recent_period,
        ).count()

    @property
    def repositories_count(self) -> int:
        """Return count of repositories."""
        return self.repositories.count()

    @property
    def unanswered_issues_count(self) -> int:
        """Return count of unanswered issues."""
        return self.issues.filter(comments_count=0).count()

    @property
    def unassigned_issues_count(self) -> int:
        """Return count of unassigned issues."""
        return self.issues.filter(assignees__isnull=True).count()

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
                2: self.ProjectLevel.INCUBATOR,
                3: self.ProjectLevel.LAB,
                3.5: self.ProjectLevel.PRODUCTION,
                4: self.ProjectLevel.FLAGSHIP,
            }
            self.level = level_mapping.get(project_level) or self.ProjectLevel.OTHER
            self.level_raw = project_level

        # Type.
        project_type = project_metadata.get("type")
        if project_type:
            self.type = (
                project_type if project_type in self.ProjectType.values else self.ProjectType.OTHER
            )
            self.type_raw = project_type

        self.created_at = repository.created_at
        self.updated_at = repository.updated_at

    def save(self, *args, **kwargs) -> None:
        """Save the project instance."""
        if self.is_active and not self.summary and (prompt := Prompt.get_owasp_project_summary()):
            self.generate_summary(prompt=prompt)

        super().save(*args, **kwargs)

    @staticmethod
    @lru_cache
    def active_projects_count():
        """Return active projects count."""
        return IndexBase.get_total_count("projects", search_filters="idx_is_active:true")

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
