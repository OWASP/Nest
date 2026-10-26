import pytest

from apps.ai.evaluation.telemetry.cost_models import calculate_token_cost
from apps.ai.evaluation.telemetry.tracker import TelemetryTracker


class TestTelemetryTracker:
    def test_calculate_token_cost_openai(self):
        # 100k prompt + 50k completion on gpt-4o-mini
        cost = calculate_token_cost(100_000, 50_000, model="gpt-4o-mini")
        assert cost == 0.045

    def test_calculate_token_cost_gemini(self):
        cost = calculate_token_cost(1_000_000, 1_000_000, model="gemini-2.5-flash")
        assert cost == 2.8

    @pytest.mark.parametrize(
        ("prompt_tokens", "completion_tokens", "expected_cost"),
        [(1_000_000, 0, 0.4), (0, 1_000_000, 1.6)],
    )
    def test_calculate_token_cost_gpt_41_mini(
        self, prompt_tokens, completion_tokens, expected_cost
    ):
        assert (
            calculate_token_cost(prompt_tokens, completion_tokens, model="gpt-4.1-mini")
            == expected_cost
        )

    def test_calculate_token_cost_unknown_model(self):
        with pytest.raises(ValueError, match="Unknown model pricing: unknown-model"):
            calculate_token_cost(100, 50, model="unknown-model")

    def test_calculate_token_cost_default_model(self):
        assert calculate_token_cost(100_000, 50_000) == 0.045

    @pytest.mark.parametrize(
        ("model", "expected_cost"),
        [("gemini/gemini-2.5-flash", 2.8), ("openai/gpt-4.1-mini", 2.0)],
    )
    def test_calculate_token_cost_provider_prefix(self, model, expected_cost):
        assert calculate_token_cost(1_000_000, 1_000_000, model=model) == expected_cost

    def test_calculate_token_cost_unknown_prefixed_model(self):
        with pytest.raises(ValueError, match="Unknown model pricing: gemini/unknown-model"):
            calculate_token_cost(100, 50, model="gemini/unknown-model")

    def test_telemetry_tracker_aggregations(self):
        tracker = TelemetryTracker(model="gemini-2.5-flash")
        assert tracker.avg_latency_ms == 0.0
        assert tracker.p50_latency_ms == 0.0

        tracker.record(latency_ms=100.0, prompt_tokens=100, completion_tokens=50)
        tracker.record(latency_ms=200.0, prompt_tokens=200, completion_tokens=100)
        tracker.record(latency_ms=300.0, prompt_tokens=300, completion_tokens=150)
        tracker.record(latency_ms=400.0, prompt_tokens=400, completion_tokens=200)

        assert tracker.total_prompt_tokens == 1000
        assert tracker.total_completion_tokens == 500
        assert tracker.total_tokens == 1500
        assert tracker.avg_latency_ms == 250.0
        assert tracker.p50_latency_ms == 250.0
        assert tracker.p90_latency_ms == 370.0
        assert tracker.p95_latency_ms == 385.0
        assert tracker.estimated_total_cost_usd == 0.00155

    @pytest.mark.parametrize("invalid", [-1, float("nan"), float("inf"), -float("inf")])
    @pytest.mark.parametrize("field", ["latency_ms", "prompt_tokens", "completion_tokens"])
    def test_record_rejects_invalid_values_without_mutating(self, field, invalid):
        tracker = TelemetryTracker()
        tracker.record(latency_ms=100.0, prompt_tokens=100, completion_tokens=50)

        with pytest.raises(ValueError, match="must be"):
            tracker.record(**{"latency_ms": 200.0, field: invalid})

        assert tracker.latencies_ms == [100.0]
        assert tracker.total_prompt_tokens == 100
        assert tracker.total_completion_tokens == 50

    @pytest.mark.parametrize("invalid", [True, False, 1.5, "1", None])
    @pytest.mark.parametrize("field", ["prompt_tokens", "completion_tokens"])
    def test_record_rejects_non_integer_tokens_without_mutating(self, field, invalid):
        tracker = TelemetryTracker()
        tracker.record(latency_ms=100.0, prompt_tokens=100, completion_tokens=50)

        with pytest.raises(ValueError, match="Token counts must be non-negative integers"):
            tracker.record(**{"latency_ms": 200.0, field: invalid})

        assert tracker.latencies_ms == [100.0]
        assert tracker.total_prompt_tokens == 100
        assert tracker.total_completion_tokens == 50

    @pytest.mark.parametrize("p", [-1, 101, float("nan"), float("inf"), -float("inf")])
    @pytest.mark.parametrize("latencies", [[], [100.0]])
    def test_percentile_rejects_invalid_values(self, p, latencies):
        tracker = TelemetryTracker(latencies_ms=latencies)
        with pytest.raises(ValueError, match="Percentile must be finite and between 0 and 100"):
            tracker.percentile_latency(p)

    @pytest.mark.parametrize("p", [0, 50, 100])
    def test_percentile_boundaries_and_single_run(self, p):
        tracker = TelemetryTracker()
        assert tracker.percentile_latency(p) == 0.0
        tracker.record(latency_ms=100.0)
        assert tracker.percentile_latency(p) == 100.0

    def test_percentile_endpoints_and_odd_median(self):
        tracker = TelemetryTracker(latencies_ms=[300.0, 100.0, 200.0])
        assert tracker.percentile_latency(0) == 100.0
        assert tracker.p50_latency_ms == 200.0
        assert tracker.percentile_latency(100) == 300.0
