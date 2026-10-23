"""Abstract base evaluator definition."""

from abc import ABC, abstractmethod

from apps.ai.evaluation.datasets.schema import AgentOutput, EvalCase, EvaluatorScore


class BaseEvaluator(ABC):
    """Abstract contract for evaluation metrics."""

    name: str = "base"

    @abstractmethod
    def evaluate(self, case: EvalCase, output: AgentOutput) -> EvaluatorScore:
        """Evaluate an agent's output against an evaluation test case.

        Args:
            case: The benchmark test case specification.
            output: The recorded output from the agent execution.

        Returns:
            EvaluatorScore with pass status, score, and diagnostic details.

        """
        raise NotImplementedError
