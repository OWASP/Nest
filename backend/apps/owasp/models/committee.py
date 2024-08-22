"""OWASP app chapter model."""

import re
from base64 import b64decode

import yaml
from django.db import models
from github.GithubException import UnknownObjectException

from apps.common.models import TimestampedModel


class Committee(TimestampedModel):
    """Committee model."""

    class Meta:
        db_table = "owasp_committees"
        verbose_name_plural = "Committees"

    name = models.CharField(verbose_name="Name", max_length=100)
    key = models.CharField(verbose_name="Key", max_length=100, unique=True)
    description = models.CharField(verbose_name="Description", max_length=500, default="")

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
        except UnknownObjectException:
            pass

        # FKs.
        self.owasp_repository = repository
