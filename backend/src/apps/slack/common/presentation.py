"""default entities presentation for OWASP entities (project, events, etc)."""

from dataclasses import dataclass


@dataclass
class EntityPresentation:
    """Configuration for entities presentation.

    Attributes
        include_feedback (bool): Whether to include feedback in the presentation.
        include_metadata (bool): Whether to include metadata in the presentation.
        include_pagination (bool): Whether to include pagination in the presentation.
        include_timestamps (bool): Whether to include timestamps in the presentation.
        name_truncation (int): Maximum length for truncating entity names.
        summary_truncation (int): Maximum length for truncating entity summaries.

    """

    include_feedback: bool = True
    include_metadata: bool = True
    include_pagination: bool = True
    include_timestamps: bool = True
    name_truncation: int = 80
    summary_truncation: int = 300
