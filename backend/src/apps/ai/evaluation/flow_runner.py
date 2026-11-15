"""Collect assistant-flow evaluations using controlled tool fixtures."""

from dataclasses import asdict

from apps.ai.evaluation.datasets.dataset import get_case_by_id
from apps.ai.evaluation.datasets.project_fixtures import PROJECT_FIXTURES
from apps.ai.evaluation.datasets.rag_fixtures import RAG_FIXTURES
from apps.ai.evaluation.datasets.schema import AgentOutput
from apps.ai.evaluation.evaluators.intent_evaluator import IntentEvaluator
from apps.ai.evaluation.evaluators.response_evaluator import ResponseEvaluator
from apps.ai.evaluation.evaluators.tool_evaluator import ToolEvaluator
from apps.ai.evaluation.fixture_agents import (
    use_project_fixtures,
    use_rag_fixtures,
)
from apps.ai.evaluation.flow_observer import observe_flow
from apps.ai.flows import assistant


def collect_flow_case(
    case_id: str,
    scenario: str = "relevant",
    *,
    live: bool = False,
) -> dict:
    """Collect an assistant execution using controlled tool fixtures."""
    if not live:
        msg = "Pass live=True to enable an LLM evaluation"
        raise ValueError(msg)

    case = get_case_by_id(case_id)
    if case is None:
        msg = f"Unknown benchmark case: {case_id}"
        raise ValueError(msg)

    if case.channel_id:
        msg = "Channel-scoped cases require controlled channel fixtures"
        raise ValueError(msg)

    tool_calls: list[dict] = []

    if case_id in RAG_FIXTURES:
        fixture_context = use_rag_fixtures(case_id, scenario, tool_calls)
    elif case_id in PROJECT_FIXTURES:
        if scenario != "relevant":
            msg = "Project fixtures currently support only the relevant scenario"
            raise ValueError(msg)

        fixture_context = use_project_fixtures(case_id, tool_calls)
    else:
        msg = f"No controlled fixtures for benchmark case: {case_id}"
        raise ValueError(msg)

    response = None
    error = None

    with (
        fixture_context,
        observe_flow() as events,
    ):
        try:
            response = assistant.process_query(case.query)
        except Exception as exception:  # noqa: BLE001 - preserve the execution trace
            error = f"{type(exception).__name__}: {exception}"

    return {
        "scope": "assistant_flow",
        "case_id": case.id,
        "scenario": scenario,
        "query": case.query,
        "response": response,
        "events": events,
        "tool_calls": tool_calls,
        "error": error,
    }


def score_flow_intent(record: dict) -> dict:
    """Evaluate recorded routing or explicitly skip an unavailable decision."""
    case = get_case_by_id(record["case_id"])
    if case is None:
        msg = f"Unknown benchmark case: {record['case_id']}"
        raise ValueError(msg)

    routing = next(
        (
            event["result"]
            for event in reversed(record["events"])
            if event["stage"] == "route" and isinstance(event.get("result"), dict)
        ),
        None,
    )

    if routing is None:
        return {
            "scores": [],
            "skipped": [
                {"evaluator": "intent", "reason": "No successful router result was recorded"}
            ],
        }

    output = AgentOutput(
        query=record["query"],
        response=record["response"] or "",
        intent=routing["intent"],
        confidence=routing["confidence"],
    )
    score = IntentEvaluator().evaluate(case, output)

    return {
        "scores": [asdict(score)],
        "skipped": [],
    }


def score_flow_case(record: dict) -> dict:
    """Grade a collected flow using its controlled fixture rules."""
    case = get_case_by_id(record["case_id"])
    if case is None:
        msg = f"Unknown benchmark case: {record['case_id']}"
        raise ValueError(msg)

    if case.id in RAG_FIXTURES:
        support_count_key = "supporting_result_count"
        supported_scenarios = tuple(RAG_FIXTURES[case.id])
    elif case.id in PROJECT_FIXTURES:
        support_count_key = "result_count"
        supported_scenarios = ("relevant",)
    else:
        msg = f"No grading rules for benchmark case: {case.id}"
        raise ValueError(msg)

    if record["scenario"] not in supported_scenarios:
        msg = f"Unsupported scenario '{record['scenario']}' for {case.id}"
        raise ValueError(msg)

    intent_result = score_flow_intent(record)
    scores = intent_result["scores"]
    skipped = intent_result["skipped"]

    output = AgentOutput(
        query=record["query"],
        response=record["response"] or "",
        intent="",
        tools_used=[call["tool"] for call in record["tool_calls"]],
    )
    scores.append(asdict(ToolEvaluator().evaluate(case, output)))

    requires_support = record["scenario"] in ("relevant", "mixed")
    if requires_support:
        scores.append(asdict(ResponseEvaluator().evaluate(case, output)))
    else:
        skipped.append(
            {
                "evaluator": "response_coverage",
                "reason": "Negative-evidence answers require manual review",
            }
        )

    failure_reasons = [score["reason"] for score in scores if not score["passed"]]

    if not output.response.strip():
        failure_reasons.append("Assistant returned an empty response")

    if requires_support and not any(
        not call.get("error") and call.get(support_count_key, 0) > 0
        for call in record["tool_calls"]
    ):
        failure_reasons.append("No supporting fixture results were returned")

    errors = get_flow_errors(record)
    if errors:
        failure_reasons.append("Execution errors were recorded")

    if failure_reasons:
        status = "failed"
    elif skipped:
        status = "needs_review"
    else:
        status = "passed"

    return record | {
        "scores": scores,
        "skipped": skipped,
        "errors": errors,
        "failure_reasons": failure_reasons,
        "status": status,
    }


def run_flow_case(
    case_id: str,
    scenario: str = "relevant",
    *,
    live: bool = False,
) -> dict:
    """Collect and grade one controlled assistant-flow evaluation."""
    record = collect_flow_case(case_id, scenario, live=live)
    return score_flow_case(record)


def get_flow_errors(record: dict) -> list[dict]:
    """Collect observed failures, including errors caught by the assistant."""
    errors = [
        event.copy()
        for event in record["events"]
        if event.get("error") or event["stage"] == "logged_error"
    ]

    errors.extend(call | {"stage": "tool"} for call in record["tool_calls"] if call.get("error"))

    if record["error"]:
        errors.append(
            {
                "stage": "collector",
                "error": record["error"],
            }
        )

    return errors
