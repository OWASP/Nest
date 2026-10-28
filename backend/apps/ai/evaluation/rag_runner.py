"""Run controlled RAG-agent evaluations with fixed retrieval results."""

from copy import deepcopy
from dataclasses import asdict

from crewai.tools import BaseTool

from apps.ai.agents.rag import create_rag_agent
from apps.ai.agents.rag.tools import semantic_search
from apps.ai.evaluation.datasets.dataset import get_case_by_id
from apps.ai.evaluation.datasets.rag_fixtures import get_rag_fixture
from apps.ai.evaluation.datasets.schema import AgentOutput
from apps.ai.evaluation.evaluators.response_evaluator import ResponseEvaluator
from apps.ai.evaluation.evaluators.tool_evaluator import ToolEvaluator
from apps.ai.flows.assistant import execute_task


def create_fixture_search(
    case_id: str,
    scenario: str,
    tool_calls: list[dict],
) -> BaseTool:
    """Create an independent search tool backed by fixture documents."""
    documents = get_rag_fixture(case_id, scenario)

    def retrieve(query: str, limit: int = 5) -> list[dict]:
        if limit < 0:
            msg = "Retrieval limit must be non-negative"
            raise ValueError(msg)

        results = deepcopy(documents[:limit])
        tool_calls.append(
            {
                "tool": semantic_search.name,
                "query": query,
                "limit": limit,
                "result_count": len(results),
            }
        )
        return results

    return semantic_search.model_copy(
        update={"func": retrieve, "current_usage_count": 0}
    )


def run_rag_case(
    case_id: str,
    scenario: str = "relevant",
    *,
    live: bool = False,
) -> dict:
    """Run one RAG case and report the observed answer and tool executions."""
    if not live:
        msg = "Pass live=True to enable an LLM evaluation"
        raise ValueError(msg)

    case = get_case_by_id(case_id)
    if case is None:
        msg = f"Unknown benchmark case: {case_id}"
        raise ValueError(msg)

    tool_calls = []
    search_tool = create_fixture_search(case_id, scenario, tool_calls)

    agent = create_rag_agent()
    agent.tools = [search_tool]
    agent.cache = False

    response = execute_task(agent, case.query)
    output = AgentOutput(
        query=case.query,
        response=response,
        intent="",  # This runner does not execute the router.
        tools_used=[call["tool"] for call in tool_calls],
    )

    scores = [ToolEvaluator().evaluate(case, output)]
    if scenario == "relevant":
        scores.append(ResponseEvaluator().evaluate(case, output))

    failure_reasons = [score.reason for score in scores if not score.passed]

    if not response.strip():
        failure_reasons.append("Agent returned an empty response")

    if scenario == "relevant" and not any(
        call["result_count"] for call in tool_calls
    ):
        failure_reasons.append("No supporting fixture documents were returned")

    status = "passed" if scenario == "relevant" else "needs_review"
    if failure_reasons:
        status = "failed"

    return {
        "case_id": case.id,
        "scenario": scenario,
        "scope": "rag_agent",
        "query": case.query,
        "model": getattr(agent.llm, "model", None),
        "response": response,
        "tool_calls": tool_calls,
        "scores": [asdict(score) for score in scores],
        "failure_reasons": failure_reasons,
        "status": status,
    }
