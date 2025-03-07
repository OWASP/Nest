"""GitHub app utils."""

from urllib.parse import urlparse

import requests

from apps.github.constants import GITHUB_REPOSITORY_RE


def check_owasp_site_repository(key):
    """Check OWASP site repository."""
    return key.startswith(
        (
            "www-chapter-",
            "www-committee-",
            "www-event",
            "www-project-",
        )
    )


def check_funding_policy_compliance(platform, target):
    """Check OWASP funding policy compliance."""
    if not target:
        return True

    if platform == "github":
        return target.lower() == "owasp"
    if platform == "custom":
        location = urlparse(target).netloc.lower()
        owasp_org = "owasp.org"
        return location == owasp_org or location.endswith(f".{owasp_org}")

    return False


def get_repository_file_content(url, timeout=30):
    """Get repository file content."""
    return requests.get(url, timeout=timeout).text


def get_repository_path(url):
    """Parse repository URL to owner and repository name."""
    match = GITHUB_REPOSITORY_RE.search(url.split("#")[0])
    return "/".join((match.group(1), match.group(2))) if match else None


def normalize_url(url, check_path=False):
    """Normalize URL."""
    parsed_url = urlparse(url)
    if not parsed_url.netloc or (check_path and not parsed_url.path):
        return None

    http_prefix = "http://"
    https_prefix = "https://"
    if not parsed_url.scheme:
        url = f"{https_prefix}{url}"

    normalized_url = (
        f"{https_prefix}{url[len(http_prefix) :]}" if url.startswith(http_prefix) else url
    )

    return normalized_url.split("#")[0].strip().rstrip("/")
