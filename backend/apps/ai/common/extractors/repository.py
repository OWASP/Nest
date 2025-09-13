"""Content extractor for Repository."""

import logging

from apps.ai.common.constants import DELIMITER
from apps.github.utils import get_repository_file_content

logger = logging.getLogger(__name__)


def extract_repository_content(repository) -> tuple[str, str]:
    """Extract structured content from repository data.

    Args:
        repository: Repository instance

    Returns:
        tuple[str, str]: (prose_content, metadata_content)

    """
    prose_parts: list[str] = []
    metadata_parts: list[str] = []

    if repository.name:
        metadata_parts.append(f"Repository Name: {repository.name}")

    if repository.key:
        metadata_parts.append(f"Repository Key: {repository.key}")

    if repository.description:
        prose_parts.append(f"Description: {repository.description}")

    if repository.homepage:
        metadata_parts.append(f"Homepage: {repository.homepage}")

    if repository.license:
        metadata_parts.append(f"License: {repository.license}")

    if repository.topics:
        metadata_parts.append(f"Topics: {', '.join(repository.topics)}")

    status_parts = []
    if repository.is_archived:
        status_parts.append("Archived")
    if repository.is_empty:
        status_parts.append("Empty")
    if repository.is_owasp_repository:
        status_parts.append("OWASP Repository")
    if repository.is_owasp_site_repository:
        status_parts.append("OWASP Site Repository")
    if status_parts:
        metadata_parts.append(f"Repository Status: {', '.join(status_parts)}")

    if repository.is_funding_policy_compliant:
        metadata_parts.append("Funding Policy Compliant")
    if repository.has_funding_yml:
        metadata_parts.append("Has FUNDING.yml")
    if repository.funding_yml:
        metadata_parts.append("Has FUNDING.yml Data")

    if repository.pages_status:
        metadata_parts.append(f"Pages Status: {repository.pages_status}")

    features_parts = []
    if repository.has_downloads:
        features_parts.append("Downloads")
    if repository.has_issues:
        features_parts.append("Issues")
    if repository.has_pages:
        features_parts.append("Pages")
    if repository.has_projects:
        features_parts.append("Projects")
    if repository.has_wiki:
        features_parts.append("Wiki")
    if features_parts:
        metadata_parts.append(f"Repository Features: {', '.join(features_parts)}")

    if repository.commits_count:
        metadata_parts.append(f"Commits: {repository.commits_count}")
    if repository.contributors_count:
        metadata_parts.append(f"Contributors: {repository.contributors_count}")
    if repository.forks_count:
        metadata_parts.append(f"Forks: {repository.forks_count}")
    if repository.open_issues_count:
        metadata_parts.append(f"Open Issues: {repository.open_issues_count}")
    if repository.stars_count:
        metadata_parts.append(f"Stars: {repository.stars_count}")
    if repository.subscribers_count:
        metadata_parts.append(f"Subscribers: {repository.subscribers_count}")
    if repository.watchers_count:
        metadata_parts.append(f"Watchers: {repository.watchers_count}")

    if repository.created_at:
        metadata_parts.append(f"Created: {repository.created_at.strftime('%Y-%m-%d')}")
    if repository.updated_at:
        metadata_parts.append(f"Last Updated: {repository.updated_at.strftime('%Y-%m-%d')}")
    if repository.pushed_at:
        metadata_parts.append(f"Last Pushed: {repository.pushed_at.strftime('%Y-%m-%d')}")

    if repository.organization:
        metadata_parts.append(f"Organization: {repository.organization.login}")
    if repository.owner:
        metadata_parts.append(f"Owner: {repository.owner.login}")

    if repository.track_issues:
        metadata_parts.append(f"Track Issues: {repository.track_issues}")

    return (
        DELIMITER.join(filter(None, prose_parts)),
        DELIMITER.join(filter(None, metadata_parts)),
    )


def extract_repository_markdown_content(repository) -> tuple[str, str]:
    """Extract markdown content from repository files.

    Args:
        repository: Repository instance

    Returns:
        tuple[str, str]: (prose_content, metadata_content)

    """
    prose_parts: list[str] = []
    metadata_parts: list[str] = []

    if repository.description:
        prose_parts.append(f"Repository Description: {repository.description}")

    markdown_files = [
        "README.md",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        "SECURITY.md",
        "CHANGELOG.md",
        "LICENSE.md",
        "docs/README.md",
        "docs/index.md",
        "docs/overview.md",
        "docs/getting-started.md",
        "docs/installation.md",
        "docs/usage.md",
        "docs/api.md",
        "docs/development.md",
        "docs/deployment.md",
    ]

    fetched_files = []
    for file_path in markdown_files:
        try:
            if repository.organization:
                owner = repository.organization.login
            else:
                owner = repository.owner.login if repository.owner else ""

            if owner and repository.key:
                raw_url = (
                    f"https://raw.githubusercontent.com/{owner}/{repository.key}/"
                    f"{repository.default_branch or 'main'}/{file_path}"
                )
                content = get_repository_file_content(raw_url)

                if content and content.strip():
                    fetched_files.append(file_path)
                    prose_parts.append(f"## {file_path}\n\n{content}")

        except (ValueError, TypeError, OSError, ConnectionError):
            logger.debug("Failed to fetch")
            continue

    return (
        DELIMITER.join(filter(None, prose_parts)),
        DELIMITER.join(filter(None, metadata_parts)),
    )
