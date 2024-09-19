"""OWASP app common models."""

import logging
import re

import yaml
from github.GithubException import GithubException, UnknownObjectException

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

    @property
    def index_md_raw_url(self):
        """Return project's raw index.md GitHub URL."""
        return (
            "https://raw.githubusercontent.com/OWASP/"
            f"{self.owasp_repository.key}/{self.owasp_repository.default_branch}/index.md"
        )

    def from_github(self, field_mapping, gh_repository, repository):
        """Update instance based on GitHub repository data."""
        # Fetch project metadata from index.md file.
        project_metadata = {}
        try:
            index_md_content = get_repository_file_content(self.index_md_raw_url)
            yaml_content = re.search(r"^---\n(.*?)\n---", index_md_content, re.DOTALL)
            project_metadata = yaml.safe_load(yaml_content.group(1)) or {} if yaml_content else {}

            # Direct fields.
            for model_field, gh_field in field_mapping.items():
                value = project_metadata.get(gh_field)
                if value:
                    setattr(self, model_field, value)
        except yaml.scanner.ScannerError:
            logger.exception("Unable to parse metadata", extra={"repository": gh_repository.name})
        except GithubException as e:
            if e.data["status"] == "404" and "This repository is empty" in e.data["message"]:
                repository.is_empty = True
        except UnknownObjectException:
            pass

        return project_metadata

    def get_related_url(self, url):
        """Get OWASP entity related URL."""
        if url in {self.github_url, self.owasp_url}:
            return None

        if match := GITHUB_REPOSITORY_RE.match(url):
            return f"https://github.com/{match.group(1)}/{match.group(2)}".lower()

        if match := GITHUB_USER_RE.match(url):
            return f"https://github.com/{match.group(1)}".lower()

        return None
