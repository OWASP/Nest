"""Intent classification accuracy evaluator."""

from apps.ai.evals.datasets.schema import AgentOutput, EvalCase, EvaluatorScore
from apps.ai.evals.evaluators.base import BaseEvaluator


class IntentEvaluator(BaseEvaluator):
    """Evaluates whether the agent routed the query to the correct intent."""

    name: str = "intent"

    def evaluate(self, case: EvalCase, output: AgentOutput) -> EvaluatorScore:
        """Evaluate intent classification accuracy.

        Args:
            case: Benchmark case containing expected intent.
            output: Agent output containing actual intent and confidence.

        Returns:
            EvaluatorScore with binary pass/fail and diagnostic metadata.

        """
        actual_intent = output.intent.strip().lower()
        expected_intent = case.expected_intent.strip().lower()

        passed = actual_intent == expected_intent
        reason = (
            f"Intent matched '{expected_intent}'"
            if passed
            else f"Expected intent '{expected_intent}', but got '{actual_intent}'"
        )

        return EvaluatorScore(
            name=self.name,
            passed=passed,
            score=1.0 if passed else 0.0,
            reason=reason,
            details={
                "actual_intent": actual_intent,
                "expected_intent": expected_intent,
                "confidence": output.confidence,
            },
        )
