"""Shared building blocks for OWASP Board Candidate mutation inputs."""

from __future__ import annotations

import datetime

import pydantic

GITHUB_LOGIN_MAX_LENGTH = 39
MAX_KEY_LENGTH = 100
MAX_NAME_LENGTH = 200
MAX_REORDER_KEYS = 100
MAX_TEXT_LENGTH = 2000
MIN_ELECTION_YEAR = 2000


class BaseInput(pydantic.BaseModel):
    """Base Pydantic input with shared config."""

    model_config = pydantic.ConfigDict(str_strip_whitespace=True)


def validate_year(value: int) -> int:
    """Ensure the election year falls in a plausible range."""
    max_year = datetime.datetime.now(tz=datetime.UTC).year + 1
    if not MIN_ELECTION_YEAR <= value <= max_year:
        message = f"Year must be between {MIN_ELECTION_YEAR} and {max_year}."
        raise ValueError(message)
    return value
