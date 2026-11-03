"""Intent enums and validation."""

from __future__ import annotations

from enum import Enum
from typing import Self


class Intent(str, Enum):  # noqa: UP042
    """Intent classification enum."""

    description: str

    CHAPTER = "chapter", "Finds OWASP chapters, chapter leaders, and chapter activities worldwide"
    COMMUNITY = "community", "Finds community leaders, committees, and entity Slack channels"
    CONTRIBUTION = (
        "contribution",
        "Helps find contribution opportunities and guidelines for OWASP projects",
    )
    GSOC = "gsoc", "Provides Google Summer of Code program information and project details"
    PROJECT = "project", "Finds OWASP projects by topic, maturity level, or specific needs"
    RAG = "rag", "Searches OWASP documentation, policies, and repositories for general information"

    def __new__(cls, value: str, description: str = "") -> Self:
        """Create a new Intent enum member."""
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.description = description
        return obj

    @classmethod
    def descriptions(cls) -> dict[str, str]:
        """Get a mapping of intent values to their descriptions.

        Returns:
            Dictionary mapping intent string values to descriptions

        """
        return {intent.value: intent.description for intent in cls}

    @classmethod
    def values(cls) -> list[str]:
        """Get all intent values as a list.

        Returns:
            List of intent string values

        """
        return [intent.value for intent in cls]
