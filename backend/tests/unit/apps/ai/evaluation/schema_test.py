from apps.ai.evaluation.datasets.schema import (
    AgentOutput,
    BenchmarkSummary,
    EvalCase,
    EvalCategory,
    EvaluatorScore,
)


class TestEvalSchema:
    def test_eval_category_values(self):
        assert EvalCategory.PROJECT.value == "project"
        assert EvalCategory.CHAPTER.value == "chapter"
        assert EvalCategory.COMMUNITY.value == "community"
        assert EvalCategory.CONTRIBUTION.value == "contribution"
        assert EvalCategory.GSOC.value == "gsoc"
        assert EvalCategory.RAG.value == "rag"
        assert EvalCategory.COLLABORATIVE.value == "collaborative"
        assert EvalCategory.CLARIFICATION.value == "clarification"
        assert EvalCategory.ADVERSARIAL.value == "adversarial"

    def test_eval_case_creation_and_defaults(self):
        case = EvalCase(
            id="test-001",
            query="Test query",
            category=EvalCategory.PROJECT,
            expected_intent="project",
        )
        assert case.id == "test-001"
        assert case.query == "Test query"
        assert case.expected_tools == []
        assert case.forbidden_tools == []
        assert case.expected_keywords == []
        assert case.negative_assertions == []
        assert case.channel_id == ""
        assert case.notes == ""

    def test_agent_output_total_tokens(self):
        output = AgentOutput(
            query="Test query",
            response="Test response",
            intent="project",
            prompt_tokens=120,
            completion_tokens=45,
        )
        assert output.total_tokens == 165

    def test_evaluator_score_fields(self):
        score = EvaluatorScore(
            name="intent",
            passed=True,
            score=1.0,
            details={"actual_intent": "project"},
            reason="Matched",
        )
        assert score.name == "intent"
        assert score.passed is True
        assert score.score == 1.0
        assert score.details == {"actual_intent": "project"}
        assert score.reason == "Matched"

    def test_benchmark_summary_pass_rate(self):
        summary_empty = BenchmarkSummary()
        assert summary_empty.pass_rate == 0.0

        summary_half = BenchmarkSummary(total_cases=10, passed_cases=5)
        assert summary_half.pass_rate == 50.0

        summary_full = BenchmarkSummary(total_cases=3, passed_cases=3)
        assert summary_full.pass_rate == 100.0
