"""Intent enums and validation."""

from enum import Enum


class Intent(str, Enum):  # noqa: UP042
    """Intent classification enum."""

    CHAPTER = "chapter"
    COMMUNITY = "community"
    CONTRIBUTION = "contribution"
    GSOC = "gsoc"
    PROJECT = "project"
    RAG = "rag"

    @classmethod
    def values(cls) -> list[str]:
        """Get all intent values as a list.

        Returns:
            List of intent string values

        """
        return [intent.value for intent in cls]
