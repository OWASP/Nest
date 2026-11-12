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
            forbidden_tools=["dangerous_shell_tool", "banned_tool"],
        )
        output = AgentOutput(
            query=case.query,
            response="Malicious response",
            intent="clarification",
            tools_used=["logger_tool", "dangerous_shell_tool", "banned_tool"],
        )

        score = self.evaluator.evaluate(case, output)
        assert score.passed is False
        assert score.score == 0.0
        assert "Forbidden tools called" in score.reason
        assert score.details == {
            "tools_used": ["banned_tool", "dangerous_shell_tool", "logger_tool"],
            "forbidden_called": ["banned_tool", "dangerous_shell_tool"],
        }

    def test_all_expected_tools_called(self):
        case = EvalCase(
            id="test-2",
            query="Find London chapter",
            category=EvalCategory.CHAPTER,
            expected_intent="chapter",
            expected_tools=["search_projects", "search_chapters"],
        )
        output = AgentOutput(
            query=case.query,
            response="London chapter details",
            intent="chapter",
            tools_used=["search_projects", "search_chapters", "logger_tool"],
        )

        score = self.evaluator.evaluate(case, output)
        assert score.passed is True
        assert score.score == 1.0
        assert "All expected tools called" in score.reason
        assert score.details["tools_used"] == ["logger_tool", "search_chapters", "search_projects"]
        assert score.details["expected_tools"] == ["search_chapters", "search_projects"]
        assert score.details["matched_expected"] == ["search_chapters", "search_projects"]

    def test_missing_expected_tool(self):
        case = EvalCase(
            id="test-3",
            query="Find projects and chapters",
            category=EvalCategory.COLLABORATIVE,
            expected_intent="project",
            expected_tools=["search_projects", "search_chapters", "get_contribute_info"],
        )
        output = AgentOutput(
            query=case.query,
            response="Only project details",
            intent="project",
            tools_used=["search_projects"],
        )

        score = self.evaluator.evaluate(case, output)
        assert score.passed is False
        assert score.score == 0.33
        assert "Missing expected tools" in score.reason
        assert score.details["missing_expected"] == ["get_contribute_info", "search_chapters"]

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
            tools_used=["search_projects", "search_chapters"],
        )

        score = self.evaluator.evaluate(case, output)
        assert score.passed is True
        assert score.score == 1.0
        assert score.details["tools_used"] == ["search_chapters", "search_projects"]
