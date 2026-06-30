"""GitHub app utils."""

from __future__ import annotations

import datetime
import logging
from typing import TYPE_CHECKING
from urllib.parse import urlparse

import requests
from django.utils import timezone
from github.GithubException import GithubException
from requests.exceptions import RequestException

from apps.github.constants import GITHUB_REPOSITORY_RE, OWASP_GITHUB_IO, OWASP_LOGIN

if TYPE_CHECKING:
    from github import Github

logger: logging.Logger = logging.getLogger(__name__)


def check_owasp_site_repository(key: str) -> bool:
    """Check if the repository is an OWASP site repository.

    Args:
        key (str): The repository key.

    Returns:
        bool: True if the repository is an OWASP site repository, False otherwise.

    """
    return key.startswith(
        (
            "www-chapter-",
            "www-committee-",
            "www-event",
            "www-project-",
        )
    )


def check_funding_policy_compliance(platform: str, target: str | None) -> bool:
    """Check OWASP funding policy compliance.

    Args:
        platform (str): The funding platform (e.g., 'github', 'custom').
        target (str, optional): The funding target.

    Returns:
        bool: True if the funding policy is compliant, False otherwise.

    """
    if not target:
        return True

    if platform == "github":
        return target.lower() == "owasp"
    if platform == "custom":
        location = urlparse(target).netloc.lower()
        owasp_org = "owasp.org"
        return location == owasp_org or location.endswith(f".{owasp_org}")

    return False


def get_repository_file_content(url: str, *, timeout: float | None = 30) -> str:
    """Get the content of a file from a repository.

    Args:
        url (str): The URL of the file.
        timeout (float, optional): The request timeout in seconds.

    Returns:
        str: The content of the file, or empty string if the request fails.

    """
    try:
        return requests.get(url, timeout=timeout).text
    except RequestException as e:
        logger.exception("Failed to fetch file", extra={"URL": url, "error": str(e)})
        return ""


def get_repository_path(url: str) -> str | None:
    """Parse a repository URL to extract the owner and repository name.

    Args:
        url (str): The repository URL.

    Returns:
        str or None: The repository path in the format 'owner/repository_name',
        or None if parsing fails.

    """
    match = GITHUB_REPOSITORY_RE.search(url.split("#", maxsplit=1)[0])
    return "/".join((match.group(1), match.group(2))) if match else None


def normalize_url(url: str, *, check_path: bool = False) -> str | None:
    """Normalize a URL.

    Args:
        url (str): The URL to normalize.
        check_path (bool, optional): Whether to check if the URL has a path.

    Returns:
        str | None: The normalized URL, or None if the URL is invalid.

    """
    parsed_url = urlparse(url)
    if not parsed_url.netloc or (check_path and not parsed_url.path):
        return None

    http_prefix = "http://"  # NOSONAR
    https_prefix = "https://"
    if not parsed_url.scheme:
        url = f"{https_prefix}{url.lstrip('/')}"

    normalized_url = (
        f"{https_prefix}{url[len(http_prefix) :]}" if url.startswith(http_prefix) else url
    )

    return normalized_url.split("#")[0].strip().rstrip("/")


def get_latest_invite_link_commit(
    github: Github,
    *,
    file_path: str = "_includes/slack_invite.html",
    max_commits_to_scan: int = 500,
    repository_name: str | None = None,
) -> tuple[datetime.datetime | None, str | None]:
    """Return commit date and SHA of the newest matching change to the public Slack invite file.

    Matches commits whose message contains the words ``update``, ``slack``, and ``invite`` in
    that order (case-insensitive).
    Uses committer date (when the change landed).

    Args:
        github: Authenticated PyGithub client.
        file_path: Path within the repo to filter commits (default: Slack invite include).
        max_commits_to_scan: Stop after this many commits with no match.
        repository_name: Repository in ``owner/name`` form (default: ``owasp/owasp.github.io``).

    Returns:
        ``(timezone-aware datetime, full commit SHA)`` for the first matching commit
        (newest first), or ``(None, None)`` if none.

    """
    repository_name = repository_name or f"{OWASP_LOGIN}/{OWASP_GITHUB_IO}"
    try:
        repository = github.get_repo(repository_name)
    except GithubException:
        logger.exception("Failed to load repo %s", repository_name)
        raise

    commits = repository.get_commits(path=file_path)
    for index, data in enumerate(commits):
        if index >= max_commits_to_scan:
            logger.warning(
                "No commit matched within first %s commits for %s",
                max_commits_to_scan,
                file_path,
            )
            return None, None
        msg_lower = data.commit.message.lower()
        rest = msg_lower
        matched = True
        for word in ("update", "slack", "invite"):
            if word not in rest:
                matched = False
                break
            rest = rest.split(word, 1)[1]
        if not matched:
            continue
        dt = data.commit.committer.date
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, datetime.UTC)
        return dt, data.sha
    return None, None
