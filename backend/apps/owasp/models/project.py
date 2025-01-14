"""OWASP app project models."""

from functools import lru_cache

from django.db import models

from apps.common.index import IndexBase
from apps.common.models import BulkSaveModel, TimestampedModel
from apps.common.utils import get_absolute_url
from apps.core.models.prompt import Prompt
from apps.github.models.issue import Issue
from apps.github.models.release import Release
from apps.owasp.models.common import GenericEntityModel, RepositoryBasedEntityModel
from apps.owasp.models.managers.project import ActiveProjectManager
from apps.owasp.models.mixins.project import ProjectIndexMixin


class Project(
    BulkSaveModel,
    GenericEntityModel,
    ProjectIndexMixin,
    RepositoryBasedEntityModel,
    TimestampedModel,
):
    """Project model."""

    objects = models.Manager()
    active_projects = ActiveProjectManager()

    class Meta:
        db_table = "owasp_projects"
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
        choices=ProjectLevel,
        default=ProjectLevel.OTHER,
    )
    level_raw = models.CharField(verbose_name="Level raw", max_length=50, default="")

    type = models.CharField(
        verbose_name="Type",
        max_length=20,
        choices=ProjectType,
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

    custom_tags = models.JSONField(verbose_name="Custom tags", default=list)
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

    def __str__(self):
        """Project human readable representation."""
        return f"{self.name or self.key}"

    @property
    def is_code_type(self):
        """Indicate whether project has CODE type."""
        return self.type == self.ProjectType.CODE

    @property
    def is_documentation_type(self):
        """Indicate whether project has DOCUMENTATION type."""
        return self.type == self.ProjectType.DOCUMENTATION

    @property
    def is_tool_type(self):
        """Indicate whether project has TOOL type."""
        return self.type == self.ProjectType.TOOL

    @property
    def is_indexable(self):
        """Projects to index."""
        return self.is_active and self.has_active_repositories

    @property
    def nest_key(self):
        """Get Nest key."""
        return self.key.replace("www-project-", "")

    @property
    def nest_url(self):
        """Get Nest URL for project."""
        return get_absolute_url(f"projects/{self.nest_key}")

    @property
    def open_issues(self):
        """Return open issues."""
        return Issue.open_issues.filter(repository__in=self.repositories.all())

    @property
    def published_releases(self):
        """Return project releases."""
        return Release.objects.filter(
            is_draft=False,
            published_at__isnull=False,
            repository__in=self.repositories.all(),
        )

    def deactivate(self):
        """Deactivate project."""
        self.is_active = False
        self.save(update_fields=("is_active",))

    def from_github(self, repository):
        """Update instance based on GitHub repository data."""
        field_mapping = {
            "description": "pitch",
            "name": "title",
            "tags": "tags",
        }
        project_metadata = RepositoryBasedEntityModel.from_github(self, field_mapping, repository)

        # Normalize tags.
        self.tags = (
            [tag.strip(", ") for tag in self.tags.split("," if "," in self.tags else " ")]
            if isinstance(self.tags, str)
            else self.tags
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

        # FKs.
        self.owasp_repository = repository

    def save(self, *args, **kwargs):
        """Save project."""
        if not self.summary and (prompt := Prompt.get_owasp_project_summary()):
            self.generate_summary(prompt=prompt)

        super().save(*args, **kwargs)

    @staticmethod
    @lru_cache
    def active_projects_count():
        """Return active projects count."""
        return IndexBase.get_total_count("projects")

    @staticmethod
    def bulk_save(projects, fields=None):
        """Bulk save projects."""
        BulkSaveModel.bulk_save(Project, projects, fields=fields)

    @staticmethod
    def get_gsoc_projects(year, attributes=None):
        """Return GSoC projects."""
        projects = Project.objects.filter(custom_tags__contains=[f"gsoc{year}"])
        if attributes:
            projects = projects.values(*attributes)

        return projects

    @staticmethod
    def update_data(gh_repository, repository, save=True):
        """Update project data."""
        key = gh_repository.name.lower()
        try:
            project = Project.objects.get(key=key)
        except Project.DoesNotExist:
            project = Project(key=key)

        project.from_github(repository)
        if save:
            project.save()

        return project
