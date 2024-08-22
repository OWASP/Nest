"""OWASP app common models."""

import logging
import re
from base64 import b64decode

import yaml
from github.GithubException import GithubException, UnknownObjectException

logger = logging.getLogger(__name__)


class MarkdownMetadata:
    """Markdown metadata."""

    class Meta:
        abstract = True

    def from_github(self, field_mapping, gh_repository, repository):
        """Update instance based on GitHub repository data."""
        # Fetch project metadata from index.md file.
        project_metadata = {}
        try:
            index_md = gh_repository.get_contents("index.md")
            md_content = b64decode(index_md.content).decode()
            yaml_content = re.search(r"^---\n(.*?)\n---", md_content, re.DOTALL)
            project_metadata = yaml.safe_load(yaml_content.group(1)) or {} if yaml_content else {}

            # Direct fields.
            for model_field, gh_field in field_mapping.items():
                value = project_metadata.get(gh_field)
                if value is not None:
                    setattr(self, model_field, value)
        except yaml.scanner.ScannerError:
            logger.exception("Unable to parse metadata", extra={"repository": gh_repository.name})
        except GithubException as e:
            if e.data["status"] == "404" and "This repository is empty" in e.data["message"]:
                repository.is_empty = True
        except UnknownObjectException:
            pass

        return project_metadata
