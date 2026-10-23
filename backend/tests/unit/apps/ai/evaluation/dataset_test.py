import pytest
from crewai.utilities.string_utils import sanitize_tool_name

from apps.ai.agents.chapter.tools import search_chapters
from apps.ai.agents.contribution.tools import (
    get_contribute_info,
    get_gsoc_info,
    get_gsoc_project_info,
)
from apps.ai.agents.project.tools import get_flagship_projects, search_projects
from apps.ai.agents.rag.tools import semantic_search
from apps.ai.common.intent import Intent
from apps.ai.evaluation.datasets.dataset import get_case_by_id, get_dataset
from apps.ai.evaluation.datasets.schema import AgentOutput, EvalCategory
from apps.ai.evaluation.evaluators.tool_evaluator import ToolEvaluator


class TestDataset:
    def test_get_all_cases(self):
        cases = get_dataset()
        assert len(cases) >= 25

    def test_unique_case_ids(self):
        cases = get_dataset()
        ids = [c.id for c in cases]
        assert len(ids) == len(set(ids))

    def test_filter_by_category_enum(self):
        proj_cases = get_dataset(EvalCategory.PROJECT)
        assert len(proj_cases) > 0
        assert all(c.category == EvalCategory.PROJECT for c in proj_cases)

    def test_filter_by_category_str(self):
        gsoc_cases = get_dataset("gsoc")
        assert len(gsoc_cases) > 0
        assert all(c.category == EvalCategory.GSOC for c in gsoc_cases)

    def test_get_case_by_id_found(self):
        case = get_case_by_id("proj-001")
        assert case is not None
        assert case.id == "proj-001"
        assert case.category == EvalCategory.PROJECT

    def test_get_case_by_id_not_found(self):
        case = get_case_by_id("non-existent-id")
        assert case is None

    @pytest.mark.parametrize("category", [None, EvalCategory.PROJECT])
    def test_dataset_results_do_not_modify_benchmark(self, category):
        case = get_dataset(category)[0]
        original_tools = case.expected_tools.copy()
        case.expected_tools.clear()
        case.query = "Changed by a benchmark run"

        fresh_case = get_case_by_id(case.id)
        assert fresh_case.expected_tools == original_tools
        assert fresh_case.query != case.query

        fresh_case.expected_tools.clear()
        assert get_dataset(category)[0].expected_tools == original_tools

    def test_all_cases_have_valid_fields(self):
        cases = get_dataset()
        for case in cases:
            assert case.id.strip() != ""
            assert case.query.strip() != ""
            assert case.expected_intent in Intent.values()
            assert isinstance(case.category, EvalCategory)

    def test_tool_expectations_use_registered_names(self):
        tool_names = {
            tool.name
            for tool in (
                search_chapters,
                search_projects,
                get_flagship_projects,
                get_contribute_info,
                get_gsoc_info,
                get_gsoc_project_info,
                semantic_search,
            )
        }
        for case in get_dataset():
            assert set(case.expected_tools) <= tool_names
            assert set(case.forbidden_tools) <= tool_names

    def test_rag_requires_retrieval(self):
        for case in get_dataset(EvalCategory.RAG):
            output = AgentOutput(query=case.query, response="Answer", intent="rag")
            evaluator = ToolEvaluator()
            assert evaluator.evaluate(case, output).passed is False
            output.tools_used = [semantic_search.name]
            assert evaluator.evaluate(case, output).passed is True

    def test_recorded_tool_names_match_dataset_expectations(self):
        case = get_case_by_id("chap-001")
        output = AgentOutput(
            query=case.query,
            response="London chapter details",
            intent="chapter",
            tools_used=[sanitize_tool_name(search_chapters.name)],
        )
        assert ToolEvaluator().evaluate(case, output).passed is True

    @pytest.mark.parametrize("category", [EvalCategory.CLARIFICATION, EvalCategory.ADVERSARIAL])
    @pytest.mark.parametrize("tool_name", [semantic_search.name, "unknown_future_tool"])
    def test_clarification_and_refusal_require_no_tools(self, category, tool_name):
        for case in get_dataset(category):
            output = AgentOutput(query=case.query, response="Response", intent="rag")
            evaluator = ToolEvaluator()
            assert evaluator.evaluate(case, output).passed is True
            output.tools_used = [tool_name]
            assert evaluator.evaluate(case, output).passed is False
