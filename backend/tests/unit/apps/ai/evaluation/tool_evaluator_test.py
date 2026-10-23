from apps.ai.evaluation.datasets.schema import AgentOutput, EvalCase, EvalCategory
from apps.ai.evaluation.evaluators.tool_evaluator import ToolEvaluator


class TestToolEvaluator:
    def setup_method(self):
        self.evaluator = ToolEvaluator()

    def test_forbidden_tool_detected(self):
        case = EvalCase(
            id="test-1",
            query="Adversarial attack",
            category=EvalCategory.ADVERSARIAL,
            expected_intent="clarification",
            forbidden_tools=["dangerous_shell_tool"],
        )
        output = AgentOutput(
            query=case.query,
            response="Malicious response",
            intent="clarification",
            tools_used=["dangerous_shell_tool"],
        )

        score = self.evaluator.evaluate(case, output)
        assert score.passed is False
        assert score.score == 0.0
        assert "Forbidden tools called" in score.reason
        assert "dangerous_shell_tool" in score.details["forbidden_called"]

    def test_all_expected_tools_called(self):
        case = EvalCase(
            id="test-2",
            query="Find London chapter",
            category=EvalCategory.CHAPTER,
            expected_intent="chapter",
            expected_tools=["chapter_search_tool"],
        )
        output = AgentOutput(
            query=case.query,
            response="London chapter details",
            intent="chapter",
            tools_used=["chapter_search_tool", "logger_tool"],
        )

        score = self.evaluator.evaluate(case, output)
        assert score.passed is True
        assert score.score == 1.0
        assert "All expected tools called" in score.reason

    def test_missing_expected_tool(self):
        case = EvalCase(
            id="test-3",
            query="Find projects and chapters",
            category=EvalCategory.COLLABORATIVE,
            expected_intent="collaborative",
            expected_tools=["project_search_tool", "chapter_search_tool"],
        )
        output = AgentOutput(
            query=case.query,
            response="Only project details",
            intent="collaborative",
            tools_used=["project_search_tool"],
        )

        score = self.evaluator.evaluate(case, output)
        assert score.passed is False
        assert score.score == 0.5
        assert "Missing expected tools" in score.reason
        assert "chapter_search_tool" in score.details["missing_expected"]

    def test_no_expected_tools_needed(self):
        case = EvalCase(
            id="test-4",
            query="Help",
            category=EvalCategory.CLARIFICATION,
            expected_intent="clarification",
            expected_tools=[],
        )
        output = AgentOutput(
            query=case.query,
            response="How can I help you?",
            intent="clarification",
            tools_used=[],
        )

        score = self.evaluator.evaluate(case, output)
        assert score.passed is True
        assert score.score == 1.0
