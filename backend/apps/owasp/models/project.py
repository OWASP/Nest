"""OWASP app project models."""

from functools import lru_cache

from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel
from apps.owasp.models.common import OwaspEntity
from apps.owasp.models.managers.project import ActiveProjectManager
from apps.owasp.models.mixins import ProjectIndexMixin


class Project(BulkSaveModel, OwaspEntity, ProjectIndexMixin, TimestampedModel):
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

    name = models.CharField(verbose_name="Name", max_length=100)
    key = models.CharField(verbose_name="Key", max_length=100, unique=True)
    description = models.CharField(verbose_name="Description", max_length=500, default="")

    is_active = models.BooleanField(verbose_name="Is active", default=True)
    has_active_repositories = models.BooleanField(
        verbose_name="Has active repositories", default=True
    )

    level = models.CharField(
        verbose_name="Level", max_length=20, choices=ProjectLevel, default=ProjectLevel.OTHER
    )
    level_raw = models.CharField(verbose_name="Level raw", max_length=50, default="")

    type = models.CharField(
        verbose_name="Type", max_length=20, choices=ProjectType, default=ProjectType.OTHER
    )
    type_raw = models.CharField(verbose_name="Type raw", max_length=100, default="")

    tags = models.JSONField(verbose_name="OWASP metadata tags", default=list)

    leaders_raw = models.JSONField(
        verbose_name="Project leaders list", default=list, blank=True, null=True
    )
    related_urls = models.JSONField(
        verbose_name="Project related URLs", default=list, blank=True, null=True
    )
    invalid_urls = models.JSONField(
        verbose_name="Invalid project related URLs", default=list, blank=True, null=True
    )

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

    def deactivate(self):
        """Deactivate project."""
        self.is_active = False
        self.save(update_fields=("is_active",))

    def from_github(self, gh_repository, repository):
        """Update instance based on GitHub repository data."""
        field_mapping = {
            "description": "pitch",
            "name": "title",
            "tags": "tags",
        }
        project_metadata = OwaspEntity.from_github(self, field_mapping, gh_repository, repository)

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

    @staticmethod
    @lru_cache(maxsize=128)
    def active_projects_count():
        """Return active projects count."""
        return Project.active_projects.count()

    @staticmethod
    def bulk_save(projects):
        """Bulk save projects."""
        BulkSaveModel.bulk_save(Project, projects)

    @staticmethod
    def update_data(gh_repository, repository, save=True):
        """Update project data."""
        key = gh_repository.name.lower()
        try:
            project = Project.objects.get(key=key)
        except Project.DoesNotExist:
            project = Project(key=key)

        project.from_github(gh_repository, repository)
        if save:
            project.save()

        return project
