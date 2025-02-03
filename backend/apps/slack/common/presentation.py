"""default entities presentation for OWASP entities (project, events, etc)."""

from dataclasses import dataclass


@dataclass
class EntityPresentation:
    """Configuration for entities presentation."""

    include_feedback: bool = True
    include_metadata: bool = True
    include_pagination: bool = True
    include_timestamps: bool = True
    name_truncation: int = 80
    summary_truncation: int = 300
