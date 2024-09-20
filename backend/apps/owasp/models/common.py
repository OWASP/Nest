"""OWASP app common models."""

import logging
import re

import yaml

from apps.github.constants import GITHUB_REPOSITORY_RE, GITHUB_USER_RE
from apps.github.utils import get_repository_file_content

logger = logging.getLogger(__name__)


class OwaspEntity:
    """Markdown metadata."""

    class Meta:
        abstract = True

    @property
    def github_url(self):
        """Get GitHub URL."""
        return f"https://github.com/owasp/{self.key}"

    @property
    def owasp_url(self):
        """Get OWASP URL."""
        return f"https://owasp.org/{self.key}"

    def from_github(self, field_mapping, repository):
        """Update instance based on GitHub repository data."""
        # Fetch project metadata from index.md file.
        project_metadata = {}
        index_md_content = get_repository_file_content(
            self.get_index_md_raw_url(repository=repository)
        )
        yaml_content = re.search(r"^---\n(.*?)\n---", index_md_content, re.DOTALL)
        project_metadata = yaml.safe_load(yaml_content.group(1)) or {} if yaml_content else {}

        # Direct fields.
        for model_field, gh_field in field_mapping.items():
            value = project_metadata.get(gh_field)
            if value:
                setattr(self, model_field, value)

        return project_metadata

    def get_index_md_raw_url(self, repository=None):
        """Return project's raw index.md GitHub URL."""
        owasp_repository = repository or self.owasp_repository
        return (
            "https://raw.githubusercontent.com/OWASP/"
            f"{owasp_repository.key}/{owasp_repository.default_branch}/index.md"
            if owasp_repository
            else None
        )

    def get_related_url(self, url):
        """Get OWASP entity related URL."""
        if url in {self.github_url, self.owasp_url}:
            return None

        if match := GITHUB_REPOSITORY_RE.match(url):
            return f"https://github.com/{match.group(1)}/{match.group(2)}".lower()

        if match := GITHUB_USER_RE.match(url):
            return f"https://github.com/{match.group(1)}".lower()

        return None
