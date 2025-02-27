"""Slack app utils."""

import logging
import re
from datetime import datetime
from functools import lru_cache
from html import escape as escape_html
from urllib.parse import urljoin

import requests
import yaml
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from github import Github
from lxml import html
from requests.exceptions import RequestException

from apps.common.constants import NL, OWASP_NEWS_URL

logger = logging.getLogger(__name__)


ISSUES_INDEX = 5
GITHUB_COM_INDEX = 2
MIN_PARTS_LENGTH = 4

DEADLINE_FORMAT_ERROR = "Invalid deadline format. Use YYYY-MM-DD or YYYY-MM-DD HH:MM."
DEADLINE_FUTURE_ERROR = "Deadline must be in the future."
FETCH_ISSUE_ERROR = "Failed to fetch issue from GitHub: {error}"
INVALID_ISSUE_LINK_FORMAT = "Invalid GitHub issue link format."
ISSUE_LINK_ERROR = "Issue link must belong to an OWASP repository."
PRICE_POSITIVE_ERROR = "Price must be a positive value."
PRICE_VALID_ERROR = "Price must be a valid number."


def escape(content):
    """Escape HTML content."""
    return escape_html(content, quote=False)


@lru_cache
def get_gsoc_projects(year):
    """Get GSoC projects."""
    from apps.owasp.api.search.project import get_projects

    return get_projects(
        attributes=["idx_name", "idx_url"],
        query=f"gsoc{year}",
        searchable_attributes=[
            "idx_custom_tags",
            "idx_languages",
            "idx_tags",
            "idx_topics",
        ],
    )["hits"]


@lru_cache
def get_news_data(limit=10, timeout=30):
    """Get news data."""
    response = requests.get(OWASP_NEWS_URL, timeout=timeout)
    tree = html.fromstring(response.content)
    h2_tags = tree.xpath("//h2")

    items_total = 0
    items = []
    for h2 in h2_tags:
        if anchor := h2.xpath(".//a[@href]"):
            author_tag = h2.xpath("./following-sibling::p[@class='author']")
            items.append(
                {
                    "author": author_tag[0].text_content().strip() if author_tag else "",
                    "title": anchor[0].text_content().strip(),
                    "url": urljoin(OWASP_NEWS_URL, anchor[0].get("href")),
                }
            )
            items_total += 1

        if items_total == limit:
            break

    return items


def get_or_create_issue(issue_link):
    """Fetch or create an Issue instance from the GitHub API."""
    from apps.github.models.issue import Issue
    from apps.github.models.repository import Repository
    from apps.github.models.user import User

    logger.info("Fetching or creating issue for link: %s", issue_link)

    # Extract repository owner, repo name, and issue number from the issue link
    # Example: https://github.com/OWASP/Nest/issues/XYZ
    parts = issue_link.strip("/").split("/")
    if (
        len(parts) < MIN_PARTS_LENGTH
        or parts[GITHUB_COM_INDEX] != "github.com"
        or parts[ISSUES_INDEX] != "issues"
    ):
        raise ValidationError(INVALID_ISSUE_LINK_FORMAT)

    try:
        return Issue.objects.get(url=issue_link)
    except Issue.DoesNotExist:
        pass

    github_client = Github(settings.GITHUB_TOKEN)
    issue_number = int(parts[6])
    owner = parts[3]
    repo_name = parts[4]

    try:
        # Fetch the repository and issue from GitHub
        gh_repo = github_client.get_repo(f"{owner}/{repo_name}")
        gh_issue = gh_repo.get_issue(issue_number)
        repository = Repository.objects.get(name=repo_name)
        author = User.objects.get(login=gh_issue.user.login)

        # Update or create the issue in the database
        return Issue.update_data(gh_issue, author=author, repository=repository)
    except Exception as e:
        logger.exception("Failed to fetch issue from GitHub: %s")
        raise ValidationError(FETCH_ISSUE_ERROR.format(error=e)) from e


@lru_cache
def get_staff_data(timeout=30):
    """Get staff data."""
    file_path = "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/_data/staff.yml"
    try:
        return sorted(
            yaml.safe_load(
                requests.get(
                    file_path,
                    timeout=timeout,
                ).text
            ),
            key=lambda p: p["name"],
        )
    except (RequestException, yaml.scanner.ScannerError):
        logger.exception("Unable to parse OWASP staff data file", extra={"file_path": file_path})


def get_text(blocks):
    """Convert blocks to plain text."""
    text = []

    for block in blocks:
        match block.get("type"):
            case "section":
                if "text" in block and block["text"].get("type") == "mrkdwn":
                    text.append(strip_markdown(block["text"]["text"]))
                elif "fields" in block:
                    text.append(
                        NL.join(
                            strip_markdown(field["text"])
                            for field in block["fields"]
                            if field.get("type") == "mrkdwn"
                        )
                    )
            case "divider":
                text.append("---")
            case "context":
                text.append(
                    NL.join(
                        strip_markdown(element["text"])
                        for element in block["elements"]
                        if element.get("type") == "mrkdwn"
                    )
                )
            case "actions":
                text.append(
                    NL.join(
                        strip_markdown(element["text"]["text"])
                        for element in block["elements"]
                        if element.get("type") == "button"
                    )
                )
            # TODO(arkid15r): consider removing this.
            case "image":
                text.append(f"Image: {block.get('image_url', '')}")
            case "header":
                if "text" in block and block["text"].get("type") == "plain_text":
                    text.append(block["text"]["text"])

    return NL.join(text).strip()


def strip_markdown(text):
    """Strip markdown formatting."""
    slack_link_pattern = re.compile(r"<(https?://[^|]+)\|([^>]+)>")
    return slack_link_pattern.sub(r"\2 (\1)", text).replace("*", "")


def validate_deadline(deadline_str):
    """Validate that the deadline is in a valid datetime format."""
    try:
        # Try parsing the deadline in YYYY-MM-DD format
        deadline = datetime.strptime(deadline_str, "%Y-%m-%d").replace(
            tzinfo=timezone.get_current_timezone()
        )
    except ValueError:
        try:
            # Try parsing the deadline in YYYY-MM-DD HH:MM format
            deadline = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M").replace(
                tzinfo=timezone.get_current_timezone()
            )
        except ValueError as e:
            raise ValidationError(DEADLINE_FORMAT_ERROR) from e

    if deadline < timezone.now():
        raise ValidationError(DEADLINE_FUTURE_ERROR)

    return deadline


def validate_github_issue_link(issue_link):
    """Validate that the issue link belongs to a valid OWASP-related repository."""
    if not issue_link.startswith("https://github.com/OWASP"):
        raise ValidationError(ISSUE_LINK_ERROR)
    return issue_link


def validate_price(price):
    """Validate that the price is a positive float value."""
    try:
        price = float(price)
        if price <= 0:
            raise ValidationError(PRICE_POSITIVE_ERROR)
    except ValueError as e:
        raise ValidationError(PRICE_VALID_ERROR) from e
    return price
