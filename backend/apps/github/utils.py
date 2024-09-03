"""GitHub app utils."""

from urllib.parse import urlparse

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
    if platform == "github":
        return target.lower() == "owasp"
    if platform == "custom":
        return urlparse(target).netloc.lower() == "owasp.org"

    return False


def get_node_id(node):
    """Extract node_id."""
    return node.raw_data["node_id"]


def get_repository_path(url):
    """Parse repository URL to owner and repository name."""
    match = GITHUB_REPOSITORY_RE.search(url.split("#")[0])
    return "/".join((match.group(1), match.group(2))) if match else None


def normalize_url(url):
    """Normalize GitHub URL."""
    http_prefix = "http://"
    https_prefix = "https://"
    normalized_url = (
        f"{https_prefix}{url[len(http_prefix):]}" if url.startswith(http_prefix) else url
    )

    return normalized_url.split("#")[0].lower().strip().rstrip("/")
