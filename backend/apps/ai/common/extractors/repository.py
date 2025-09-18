"""Content extractor for Repository."""

import json
import logging
import time

from apps.ai.common.constants import DELIMITER, GITHUB_REQUEST_INTERVAL_SECONDS
from apps.common.utils import is_valid_json
from apps.github.utils import get_repository_file_content

logger = logging.getLogger(__name__)


def extract_repository_content(repository) -> tuple[str, str]:
    """Extract structured content from repository data.

    Args:
        repository: Repository instance

    Returns:
        tuple[str, str]: (json_content, metadata_content)

    """
    repository_data = {}

    if repository.name:
        repository_data["name"] = repository.name
    if repository.key:
        repository_data["key"] = repository.key
    if repository.description:
        repository_data["description"] = repository.description
    if repository.homepage:
        repository_data["homepage"] = repository.homepage
    if repository.license:
        repository_data["license"] = repository.license
    if repository.topics:
        repository_data["topics"] = repository.topics

    status = {}
    if repository.is_archived:
        status["archived"] = True
    if repository.is_empty:
        status["empty"] = True
    if repository.is_owasp_repository:
        status["owasp_repository"] = True
    if repository.is_owasp_site_repository:
        status["owasp_site_repository"] = True
    if status:
        repository_data["status"] = status

    funding = {}
    if repository.is_funding_policy_compliant:
        funding["policy_compliant"] = True
    if repository.has_funding_yml:
        funding["has_funding_yml"] = True
    if funding:
        repository_data["funding"] = funding

    if repository.pages_status:
        repository_data["pages_status"] = repository.pages_status

    features = []
    if repository.has_downloads:
        features.append("downloads")
    if repository.has_issues:
        features.append("issues")
    if repository.has_pages:
        features.append("pages")
    if repository.has_projects:
        features.append("projects")
    if repository.has_wiki:
        features.append("wiki")
    if features:
        repository_data["features"] = features

    stats = {}
    if repository.commits_count:
        stats["commits"] = repository.commits_count
    if repository.contributors_count:
        stats["contributors"] = repository.contributors_count
    if repository.forks_count:
        stats["forks"] = repository.forks_count
    if repository.open_issues_count:
        stats["open_issues"] = repository.open_issues_count
    if repository.stars_count:
        stats["stars"] = repository.stars_count
    if repository.subscribers_count:
        stats["subscribers"] = repository.subscribers_count
    if repository.watchers_count:
        stats["watchers"] = repository.watchers_count
    if stats:
        repository_data["statistics"] = stats

    dates = {}
    if repository.created_at:
        dates["created"] = repository.created_at.strftime("%Y-%m-%d")
    if repository.updated_at:
        dates["last_updated"] = repository.updated_at.strftime("%Y-%m-%d")
    if repository.pushed_at:
        dates["last_pushed"] = repository.pushed_at.strftime("%Y-%m-%d")
    if dates:
        repository_data["dates"] = dates

    ownership = {}
    if repository.organization:
        ownership["organization"] = repository.organization.login
    if repository.owner:
        ownership["owner"] = repository.owner.login
    if ownership:
        repository_data["ownership"] = ownership

    markdown_files = [
        "README.md",
        "index.md",
        "info.md",
        "leaders.md",
    ]

    if repository.organization:
        owner = repository.organization.login
    else:
        owner = repository.owner.login if repository.owner else ""
    branch = repository.default_branch or "main"

    tab_files = []
    if owner and repository.key:
        contents_url = (
            f"https://api.github.com/repos/{owner}/{repository.key}/contents/?ref={branch}"
        )
        response = get_repository_file_content(contents_url)
        if response and is_valid_json(response):
            items = json.loads(response)
            for item in items:
                name = item.get("name", "")
                if name.startswith("tab_") and name.endswith(".md"):
                    tab_files.append(name)

    all_markdown_files = markdown_files + tab_files

    markdown_content = {}
    for file_path in all_markdown_files:
        try:
            if owner and repository.key:
                raw_url = (
                    f"https://raw.githubusercontent.com/{owner}/{repository.key}/"
                    f"{branch}/{file_path}"
                )
                content = get_repository_file_content(raw_url)

                if content and content.strip():
                    markdown_content[file_path] = content
                time.sleep(GITHUB_REQUEST_INTERVAL_SECONDS)

        except (ValueError, TypeError, OSError):
            logger.debug("Failed to fetch markdown file")
            continue

    if markdown_content:
        repository_data["markdown_content"] = markdown_content

    json_content = json.dumps(repository_data, indent=2)

    metadata_parts = []
    if repository.name:
        metadata_parts.append(f"Repository Name: {repository.name}")
    if repository.key:
        metadata_parts.append(f"Repository Key: {repository.key}")
    if repository.organization:
        metadata_parts.append(f"Organization: {repository.organization.login}")
    if repository.owner:
        metadata_parts.append(f"Owner: {repository.owner.login}")

    return (
        json_content,
        DELIMITER.join(filter(None, metadata_parts)),
    )
