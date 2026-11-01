"""Evaluation benchmark schemas and data structures."""

from dataclasses import dataclass, field
from enum import Enum


@dataclass
class AgentOutput:
    """Execution output captured from an agent run."""

    query: str
    response: str
    intent: str
    confidence: float = 0.0
    tools_used: list[str] = field(default_factory=list)
    sub_queries: list[dict] = field(default_factory=list)
    latency_ms: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        """Calculate total tokens consumed."""
        return self.prompt_tokens + self.completion_tokens


@dataclass
class BenchmarkSummary:
    """Aggregated evaluation benchmark summary."""

    total_cases: int = 0
    passed_cases: int = 0
    category_scores: dict[str, float] = field(default_factory=dict)
    avg_latency_ms: float = 0.0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0

    @property
    def pass_rate(self) -> float:
        """Calculate overall pass percentage between 0.0 and 100.0."""
        if not self.total_cases:
            return 0.0
        return round((self.passed_cases / self.total_cases) * 100, 2)


class EvalCategory(str, Enum):  # noqa: UP042
    """Category classification for evaluation test cases."""

    PROJECT = "project"
    CONTRIBUTION = "contribution"
    GSOC = "gsoc"
    CHAPTER = "chapter"
    COMMUNITY = "community"
    RAG = "rag"
    COLLABORATIVE = "collaborative"
    CLARIFICATION = "clarification"
    ADVERSARIAL = "adversarial"


@dataclass
class EvalCase:
    """Benchmark test case specification."""

    id: str
    query: str
    category: EvalCategory
    expected_intent: str
    expected_tools: list[str] = field(default_factory=list)
    forbidden_tools: list[str] = field(default_factory=list)
    allow_tools: bool = True
    expected_keywords: list[str] = field(default_factory=list)
    channel_id: str = ""
    notes: str = ""


@dataclass
class EvaluatorScore:
    """Evaluation result for an individual evaluator."""

    name: str
    passed: bool
    score: float
    details: dict = field(default_factory=dict)
    reason: str = ""
