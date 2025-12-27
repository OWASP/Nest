"""Data Transfer Objects for the AI core module."""

from typing import Any

from pydantic import BaseModel, Field


class RouterIntentDTO(BaseModel):
    """Data transfer object for Layer 1 intent classification."""

    label: str = Field(..., description="The classified intent label (STATIC/DYNAMIC)")
    confidence: float = Field(..., description="Confidence score of the classification")


class AIQueryDTO(BaseModel):
    """Data transfer object for incoming AI queries."""

    text: str = Field(..., description="The raw input text")
    context: dict[str, Any] = Field(default_factory=dict, description="Metadata context")


class AIResponseDTO(BaseModel):
    """Data transfer object for the final AI response."""

    answer: str = Field(..., description="Final text answer")
    source: str = Field(..., description="Data source (e.g., database, hybrid_rag)")
    intent: RouterIntentDTO = Field(..., description="Intent metadata from Layer 1")
    show_manual_search_btn: bool = Field(default=False, description="UX Escape Hatch")


class ProjectPublicDTO(BaseModel):
    """Sanitized project data for public exposure (Security Allowlist)."""

    name: str
    description: str | None = None
    url: str | None = None
    stars: int = 0
