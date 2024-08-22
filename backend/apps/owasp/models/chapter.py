"""OWASP app chapter model."""

import re
from base64 import b64decode

import yaml
from django.db import models
from github.GithubException import UnknownObjectException

from apps.common.models import TimestampedModel


class Chapter(TimestampedModel):
    """Chapter model."""

    class Meta:
        db_table = "owasp_chapters"
        verbose_name_plural = "Chapters"

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
    type = models.CharField(
        verbose_name="Type", max_length=20, choices=ProjectType, default=ProjectType.OTHER
    )

    tags = models.JSONField(verbose_name="Tags", default=list)

    owasp_repository = models.ForeignKey(
        "github.Repository", on_delete=models.SET_NULL, blank=True, null=True
    )

    def __str__(self):
        """Repository human readable representation."""
        return f"{self.name}"

    def from_github(self, gh_repository, repository):
        """Update instance based on GitHub repository data."""
        # Fetch project metadata from index.md file.
        try:
            index_md = gh_repository.get_contents("index.md")
            md_content = b64decode(index_md.content).decode()
            yaml_content = re.search(r"^---\n(.*?)\n---", md_content, re.DOTALL)
            project_metadata = yaml.safe_load(yaml_content.group(1)) if yaml_content else {}

            field_mapping = {
                "name": "title",
                "description": "pitch",
                "tags": "tags",
            }

            # Direct fields.
            for model_field, gh_field in field_mapping.items():
                value = project_metadata.get(gh_field)
                if value is not None:
                    setattr(self, model_field, value)

            # Level.
            project_level = project_metadata.get("level")
            if project_level:
                level_mapping = {
                    2: self.ProjectLevel.INCUBATOR,
                    3: self.ProjectLevel.LAB,
                    3.5: self.ProjectLevel.PRODUCTION,
                    4: self.ProjectLevel.FLAGSHIP,
                }
                self.level = level_mapping.get(project_level, self.ProjectLevel.OTHER)

            # Type.
            project_type = project_metadata.get("type")
            if project_type in {self.ProjectType.CODE, self.ProjectType.DOCUMENTATION}:
                self.type = project_type
        except UnknownObjectException:
            pass

        # FKs.
        self.owasp_repository = repository
