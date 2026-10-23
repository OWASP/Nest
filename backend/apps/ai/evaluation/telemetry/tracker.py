"""Latency and resource telemetry tracking."""

import math
from dataclasses import dataclass, field

from apps.ai.evaluation.telemetry.cost_models import calculate_token_cost


@dataclass
class TelemetryTracker:
    """Aggregates latency and token resource metrics across benchmark runs."""

    latencies_ms: list[float] = field(default_factory=list)
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    model: str = "gpt-4o-mini"

    def record(
        self,
        latency_ms: float,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
    ) -> None:
        """Record an individual evaluation run execution metrics.

        Args:
            latency_ms: Execution duration in milliseconds.
            prompt_tokens: Count of prompt tokens.
            completion_tokens: Count of completion tokens.

        """
        self.latencies_ms.append(latency_ms)
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens

    @property
    def total_tokens(self) -> int:
        """Total tokens across all recorded runs."""
        return self.total_prompt_tokens + self.total_completion_tokens

    @property
    def avg_latency_ms(self) -> float:
        """Calculate arithmetic mean latency."""
        if not self.latencies_ms:
            return 0.0
        return round(sum(self.latencies_ms) / len(self.latencies_ms), 2)

    def percentile_latency(self, p: float) -> float:
        """Calculate the p-th percentile latency (e.g. 50, 90, 95).

        Args:
            p: Percentile between 0.0 and 100.0.

        Returns:
            Percentile value in milliseconds.

        """
        if not self.latencies_ms:
            return 0.0
        sorted_latencies = sorted(self.latencies_ms)
        k = math.ceil((p / 100.0) * len(sorted_latencies)) - 1
        idx = max(0, min(len(sorted_latencies) - 1, k))
        return round(sorted_latencies[idx], 2)

    @property
    def p50_latency_ms(self) -> float:
        """50th percentile (median) latency."""
        return self.percentile_latency(50.0)

    @property
    def p90_latency_ms(self) -> float:
        """90th percentile latency."""
        return self.percentile_latency(90.0)

    @property
    def p95_latency_ms(self) -> float:
        """95th percentile latency."""
        return self.percentile_latency(95.0)

    @property
    def estimated_total_cost_usd(self) -> float:
        """Calculate total estimated monetary cost in USD."""
        return calculate_token_cost(
            prompt_tokens=self.total_prompt_tokens,
            completion_tokens=self.total_completion_tokens,
            model=self.model,
        )
