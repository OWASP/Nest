"""Deterministic response keyword coverage evaluation."""

from apps.ai.evaluation.datasets.schema import AgentOutput, EvalCase, EvaluatorScore
from apps.ai.evaluation.evaluators.base import BaseEvaluator


class ResponseEvaluator(BaseEvaluator):
    """Check whether an answer contains the required keywords."""

    name: str = "response_coverage"

    def evaluate(self, case: EvalCase, output: AgentOutput) -> EvaluatorScore:
        """Score required keyword coverage and reject empty answers."""
        response = output.response.strip().casefold()
        keywords = case.expected_keywords

        matched = [keyword for keyword in keywords if keyword.casefold() in response]
        missing = [keyword for keyword in keywords if keyword.casefold() not in response]

        score = len(matched) / len(keywords) if keywords else 1.0

        if not response:
            score = 0.0
            reason = "Response is empty"
        elif missing:
            reason = f"Missing expected keywords: {missing}"
        elif keywords:
            reason = "All expected keywords found"
        else:
            reason = "No keyword requirements"

        return EvaluatorScore(
            name=self.name,
            passed=bool(response) and not missing,
            score=round(score, 2),
            reason=reason,
            details={
                "matched_keywords": matched,
                "missing_keywords": missing,
            },
        )
