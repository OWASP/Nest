"""OWASP app project models."""

from django.db import models

from apps.common.models import TimestampedModel
from apps.owasp.models.common import MarkdownMetadata


class Project(MarkdownMetadata, TimestampedModel):
    """Project model."""

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

    level = models.CharField(
        verbose_name="Level", max_length=20, choices=ProjectLevel, default=ProjectLevel.OTHER
    )
    level_raw = models.CharField(verbose_name="Level raw", max_length=50, default="")

    type = models.CharField(
        verbose_name="Type", max_length=20, choices=ProjectType, default=ProjectType.OTHER
    )
    type_raw = models.CharField(verbose_name="Type raw", max_length=50, default="")

    tags = models.JSONField(verbose_name="Tags", default=list)

    owasp_repository = models.ForeignKey(
        "github.Repository", on_delete=models.SET_NULL, blank=True, null=True
    )

    def __str__(self):
        """Project human readable representation."""
        return f"{self.name or self.key}"

    def from_github(self, gh_repository, repository):
        """Update instance based on GitHub repository data."""
        field_mapping = {
            "description": "pitch",
            "name": "title",
            "tags": "tags",
        }
        project_metadata = MarkdownMetadata.from_github(
            self, field_mapping, gh_repository, repository
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
