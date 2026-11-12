"""Latency and resource telemetry tracking."""

import math
from dataclasses import dataclass, field

from apps.ai.evaluation.telemetry.cost_models import calculate_token_cost

## currrently not used, but may be useful for future telemetry tracking
## no practical integration yet
## maybe integrate with the monitoring/observability project ??
MAX_PERCENTILE = 100.0


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

        Raises:
            ValueError: If latency is invalid or token counts are not non-negative integers.

        """
        if not math.isfinite(latency_ms) or latency_ms < 0:
            msg = "Latency must be finite and non-negative"
            raise ValueError(msg)
        if any(
            isinstance(tokens, bool) or not isinstance(tokens, int) or tokens < 0
            for tokens in (prompt_tokens, completion_tokens)
        ):
            msg = "Token counts must be non-negative integers"
            raise ValueError(msg)

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
        """Calculate the p-th percentile latency using linear interpolation.

        Args:
            p: Percentile between 0.0 and 100.0.

        Returns:
            Percentile value in milliseconds.

        Raises:
            ValueError: If p is not finite or is outside the range 0 to 100.

        """
        if not math.isfinite(p) or not 0 <= p <= MAX_PERCENTILE:
            msg = "Percentile must be finite and between 0 and 100"
            raise ValueError(msg)
        if not self.latencies_ms:
            return 0.0
        sorted_latencies = sorted(self.latencies_ms)
        position = (p / MAX_PERCENTILE) * (len(sorted_latencies) - 1)
        lower = sorted_latencies[math.floor(position)]
        upper = sorted_latencies[math.ceil(position)]
        return round(lower + (upper - lower) * (position % 1), 2)

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
