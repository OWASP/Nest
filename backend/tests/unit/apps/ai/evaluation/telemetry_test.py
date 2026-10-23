from apps.ai.evaluation.telemetry.cost_models import calculate_token_cost
from apps.ai.evaluation.telemetry.tracker import TelemetryTracker


class TestTelemetryTracker:
    def test_calculate_token_cost_openai(self):
        # 100k prompt + 50k completion on gpt-4o-mini
        cost = calculate_token_cost(100_000, 50_000, model="gpt-4o-mini")
        assert cost == 0.045

    def test_calculate_token_cost_gemini(self):
        cost = calculate_token_cost(1_000_000, 1_000_000, model="gemini-2.5-flash")
        assert cost == 0.75

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
        assert tracker.p50_latency_ms == 200.0
        assert tracker.p90_latency_ms == 400.0
        assert tracker.p95_latency_ms == 400.0
        assert tracker.estimated_total_cost_usd > 0.0
