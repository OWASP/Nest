"""Export utilities for mentorship issues.

This module provides serialization functions for exporting issue data
in CSV and JSON formats with proper escaping and formatting.
"""

import csv
import json
from datetime import date, datetime
from enum import Enum
from io import StringIO


class ExportFormat(str, Enum):
    """Supported export formats."""

    CSV = "csv"
    JSON = "json"


# Fields to export from issues
EXPORT_FIELDS = [
    "number",
    "title",
    "state",
    "labels",
    "assignees",
    "author",
    "created_at",
    "url",
    "repository_name",
]

# Maximum issues per export request (prevents memory issues)
MAX_EXPORT_LIMIT = 1000


def _format_datetime(dt: datetime | None) -> str:
    """Format datetime to ISO string or empty string if None."""
    if dt is None:
        return ""
    return dt.isoformat()


def _format_list(items: list | None, separator: str = "; ") -> str:
    """Format a list to a separated string."""
    if not items:
        return ""
    return separator.join(str(item) for item in items)


def _issue_to_dict(issue) -> dict:
    """Convert an issue object to a dictionary for export.

    Args:
        issue: Issue model instance with related data prefetched.

    Returns:
        Dictionary containing export-ready issue data.
    """
    # Get assignee logins
    assignees = []
    if hasattr(issue, "assignees"):
        assignees = [a.login for a in issue.assignees.all() if hasattr(a, "login")]

    # Get label names
    labels = []
    if hasattr(issue, "labels"):
        labels = [label.name for label in issue.labels.all() if hasattr(label, "name")]

    # Get author login
    author = ""
    if hasattr(issue, "author") and issue.author:
        author = issue.author.login if hasattr(issue.author, "login") else str(issue.author)

    # Get repository name
    repository_name = ""
    if hasattr(issue, "repository") and issue.repository:
        repository_name = issue.repository.name if hasattr(issue.repository, "name") else ""

    return {
        "number": issue.number,
        "title": issue.title,
        "state": issue.state,
        "labels": labels,
        "assignees": assignees,
        "author": author,
        "created_at": getattr(issue, "created_at", None),
        "url": getattr(issue, "url", ""),
        "repository_name": repository_name,
    }


def serialize_issues_to_csv(issues: list) -> str:
    """Serialize issues to CSV format.

    Args:
        issues: List of Issue model instances.

    Returns:
        CSV string with UTF-8 BOM for Excel compatibility.
    """
    output = StringIO()

    # CSV headers
    headers = [
        "Number",
        "Title",
        "State",
        "Labels",
        "Assignees",
        "Author",
        "Created At",
        "URL",
        "Repository",
    ]

    writer = csv.writer(output, quoting=csv.QUOTE_ALL)
    writer.writerow(headers)

    for issue in issues:
        data = _issue_to_dict(issue)
        writer.writerow([
            data["number"],
            data["title"],
            data["state"],
            _format_list(data["labels"]),
            _format_list(data["assignees"]),
            data["author"],
            _format_datetime(data["created_at"]),
            data["url"],
            data["repository_name"],
        ])

    # Add UTF-8 BOM for Excel compatibility
    return "\ufeff" + output.getvalue()


def serialize_issues_to_json(issues: list, module_key: str = "") -> str:
    """Serialize issues to JSON format.

    Args:
        issues: List of Issue model instances.
        module_key: Optional module key for metadata.

    Returns:
        JSON string with metadata and issues array.
    """
    issues_data = []

    for issue in issues:
        data = _issue_to_dict(issue)
        issues_data.append({
            "number": data["number"],
            "title": data["title"],
            "state": data["state"],
            "labels": data["labels"],
            "assignees": data["assignees"],
            "author": data["author"],
            "createdAt": _format_datetime(data["created_at"]),
            "url": data["url"],
            "repositoryName": data["repository_name"],
        })

    result = {
        "exportedAt": date.today().isoformat(),
        "moduleKey": module_key,
        "count": len(issues_data),
        "issues": issues_data,
    }

    return json.dumps(result, indent=2, ensure_ascii=False)


def generate_export_filename(module_key: str, export_format: ExportFormat) -> str:
    """Generate a filename for the export.

    Args:
        module_key: The module key for identification.
        export_format: The export format (CSV or JSON).

    Returns:
        Filename string with date stamp.
    """
    date_str = date.today().strftime("%Y-%m-%d")
    extension = export_format.value
    return f"nest-{module_key}-issues-{date_str}.{extension}"
