"""Fixed project records; source checked 2026-11-15.

Paraphrased snapshots, not an exhaustive project catalogue.
Sources:
    https://owasp.org/projects/dependency-check
    https://owasp.org/projects/juice-shop
"""

from copy import deepcopy


def get_project_fixture(case_id: str) -> list[dict]:
    """Return independent records for a supported project case."""
    return deepcopy(PROJECT_FIXTURES[case_id])


PROJECT_FIXTURES = {
    "proj-001": [
        {
            "idx_name": "OWASP Dependency-Check",
            "idx_summary": (
                "A software composition analysis tool that identifies "
                "project dependencies with known vulnerabilities."
            ),
            "idx_url": "https://owasp.org/projects/dependency-check",
            "idx_level": "flagship",
        },
        {
            "idx_name": "OWASP Juice Shop",
            "idx_summary": (
                "An intentionally insecure web application for security training, "
                "awareness demonstrations, and capture-the-flag exercises."
            ),
            "idx_url": "https://owasp.org/projects/juice-shop",
            "idx_level": "flagship",
        },
    ],
    "proj-004": [
        {
            "idx_name": "OWASP Dependency-Check",
            "idx_summary": (
                "A software composition analysis tool that identifies "
                "project dependencies with known vulnerabilities."
            ),
            "idx_url": "https://owasp.org/projects/dependency-check",
            "idx_level": "flagship",
        }
    ],
}
