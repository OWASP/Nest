from apps.ai.evals.datasets.schema import AgentOutput, EvalCase, EvalCategory
from apps.ai.evals.evaluators.intent_evaluator import IntentEvaluator


class TestIntentEvaluator:
    def setup_method(self):
        self.evaluator = IntentEvaluator()

    def test_intent_exact_match(self):
        case = EvalCase(
            id="test-1",
            query="Find OWASP chapters",
            category=EvalCategory.CHAPTER,
            expected_intent="chapter",
        )
        output = AgentOutput(
            query=case.query,
            response="Here are chapters...",
            intent="chapter",
            confidence=0.98,
        )

        score = self.evaluator.evaluate(case, output)
        assert score.passed is True
        assert score.score == 1.0
        assert "matched" in score.reason.lower()
        assert score.details["actual_intent"] == "chapter"
        assert score.details["expected_intent"] == "chapter"
        assert score.details["confidence"] == 0.98

    def test_intent_case_insensitive_and_whitespace(self):
        case = EvalCase(
            id="test-2",
            query="Find OWASP projects",
            category=EvalCategory.PROJECT,
            expected_intent="project",
        )
        output = AgentOutput(
            query=case.query,
            response="Here are projects...",
            intent="  PROJECT  ",
            confidence=0.92,
        )

        score = self.evaluator.evaluate(case, output)
        assert score.passed is True
        assert score.score == 1.0

    def test_intent_mismatch(self):
        case = EvalCase(
            id="test-3",
            query="GSoC information",
            category=EvalCategory.GSOC,
            expected_intent="gsoc",
        )
        output = AgentOutput(
            query=case.query,
            response="RAG response...",
            intent="rag",
            confidence=0.65,
        )

        score = self.evaluator.evaluate(case, output)
        assert score.passed is False
        assert score.score == 0.0
        assert "Expected intent 'gsoc', but got 'rag'" in score.reason
