from copy import deepcopy
from dataclasses import replace
from types import SimpleNamespace

import pytest

from apps.ai.evaluation.datasets.dataset import get_case_by_id
from apps.ai.evaluation.datasets.rag_fixtures import get_rag_fixture
from apps.ai.evaluation.flow_runner import (
    collect_flow_case,
    get_flow_errors,
    run_flow_case,
    score_flow_case,
    score_flow_intent,
)
from apps.ai.flows import assistant, collaborative


@pytest.fixture(autouse=True)
def block_external_providers(mocker):
    """Fail if a test attempts a real model or embedding operation."""
    mocker.patch(
        "apps.ai.common.llm_config.LLM",
        side_effect=AssertionError("Live models must not run in collector tests"),
    )
    mocker.patch(
        "apps.ai.agents.rag.tools.get_embedder",
        side_effect=AssertionError("Live retrieval must not run in collector tests"),
    )


@pytest.fixture
def boundaries(mocker):
    """Keep production control flow and fixture search, replacing model boundaries."""
    agent = SimpleNamespace(
        role="OWASP Knowledge Specialist",
        llm=SimpleNamespace(model="test-model"),
        tools=[],
    )
    create_agent = mocker.patch(
        "apps.ai.evaluation.rag_runner.create_rag_agent",
        return_value=agent,
    )
    analyze = mocker.patch.object(
        assistant, "analyze_query", return_value={"is_simple": True, "sub_queries": []}
    )
    route = mocker.patch.object(
        assistant, "route", return_value={"intent": "rag", "confidence": 0.95}
    )

    def answer_with_fixture(agent, query=None, **_kwargs):
        if agent.tools:
            agent.tools[0].run(query=query)
            return "OWASP trademark logo policy"
        return "Combined answer"

    execute = mocker.patch.object(assistant, "execute_task", side_effect=answer_with_fixture)
    cache_read = mocker.patch.object(
        assistant, "get_cached_response", return_value="Cached answer"
    )
    cache_write = mocker.patch.object(assistant, "store_cached_response")
    return SimpleNamespace(
        agent=agent,
        create_agent=create_agent,
        analyze=analyze,
        route=route,
        execute=execute,
        cache_read=cache_read,
        cache_write=cache_write,
    )


@pytest.fixture
def _original_functions(boundaries):
    """Verify restoration after every collector test, including failure cases."""
    assert assistant.get_cached_response is boundaries.cache_read
    names = (
        "process_query",
        "analyze_query",
        "route",
        "handle_collaborative_query",
        "execute_task",
        "get_cached_response",
        "store_cached_response",
        "get_intent_to_agent_map",
    )
    originals = {name: getattr(assistant, name) for name in names}
    collaborative_map = collaborative.get_intent_to_agent_map
    log_exception = assistant.logger.exception
    yield
    for name, function in originals.items():
        assert getattr(assistant, name) is function
    assert collaborative.get_intent_to_agent_map is collaborative_map
    assert assistant.logger.exception == log_exception


@pytest.mark.usefixtures("_original_functions")
def test_collector_requires_live_opt_in(boundaries):
    with pytest.raises(ValueError, match="live=True"):
        collect_flow_case("rag-002")
    boundaries.analyze.assert_not_called()
    boundaries.create_agent.assert_not_called()


@pytest.mark.parametrize(
    ("case_id", "scenario", "error"),
    [
        ("unknown-case", "relevant", ValueError),
        ("rag-001", "relevant", KeyError),
        ("rag-002", "unknown-scenario", KeyError),
    ],
)
@pytest.mark.usefixtures("_original_functions")
def test_invalid_selection_fails_before_model_execution(boundaries, case_id, scenario, error):
    with pytest.raises(error):
        collect_flow_case(case_id, scenario, live=True)
    boundaries.analyze.assert_not_called()
    boundaries.route.assert_not_called()
    boundaries.create_agent.assert_not_called()
    boundaries.execute.assert_not_called()


@pytest.mark.usefixtures("_original_functions")
def test_channel_case_is_rejected_before_model_execution(mocker, boundaries):
    case = replace(get_case_by_id("rag-002"), channel_id="C_TEST")
    mocker.patch("apps.ai.evaluation.flow_runner.get_case_by_id", return_value=case)
    with pytest.raises(ValueError, match="Channel-scoped"):
        collect_flow_case("rag-002", live=True)
    boundaries.analyze.assert_not_called()
    boundaries.create_agent.assert_not_called()


@pytest.mark.parametrize("case_id", ["rag-002", "rag-003"])
@pytest.mark.parametrize("scenario", ["relevant", "irrelevant", "empty", "mixed"])
@pytest.mark.usefixtures("_original_functions")
def test_collector_records_real_flow_and_fixture_search(boundaries, case_id, scenario):
    result = collect_flow_case(case_id, scenario, live=True)
    case = get_case_by_id(case_id)
    documents = get_rag_fixture(case_id, scenario)
    supporting = get_rag_fixture(case_id, "relevant")

    assert result["scope"] == "assistant_flow"
    assert result["case_id"] == case_id
    assert result["scenario"] == scenario
    assert result["query"] == case.query
    assert result["response"] == "OWASP trademark logo policy"
    assert result["error"] is None
    assert "status" not in result
    assert "scores" not in result
    assert [event["stage"] for event in result["events"]] == [
        "process_query",
        "analyze_query",
        "route",
        "execute_task",
    ]
    assert result["events"][2]["result"] == {"intent": "rag", "confidence": 0.95}
    assert result["events"][3]["model"] == "test-model"
    assert result["tool_calls"] == [
        {
            "tool": boundaries.agent.tools[0].name,
            "query": case.query,
            "limit": 5,
            "result_count": len(documents),
            "supporting_result_count": sum(document in supporting for document in documents),
        }
    ]
    boundaries.execute.assert_called_once_with(boundaries.agent, case.query)
    boundaries.cache_read.assert_not_called()
    boundaries.cache_write.assert_not_called()


@pytest.mark.usefixtures("_original_functions")
def test_caught_provider_error_remains_in_events(boundaries):
    boundaries.execute.side_effect = RuntimeError("Provider failed")
    result = collect_flow_case("rag-002", live=True)
    assert result["error"] is None
    assert isinstance(result["response"], str)
    assert result["response"].strip()
    assert any(
        event["stage"] == "execute_task" and event.get("error") == "RuntimeError: Provider failed"
        for event in result["events"]
    )
    assert any(
        event["stage"] == "logged_error" and event.get("error") == "RuntimeError: Provider failed"
        for event in result["events"]
    )
    assert result["tool_calls"] == []


@pytest.mark.usefixtures("_original_functions")
def test_misrouting_is_recorded_without_constructing_uncontrolled_agent(boundaries):
    boundaries.route.return_value = {"intent": "project", "confidence": 0.9}
    result = collect_flow_case("rag-002", live=True)
    assert result["events"][2]["result"]["intent"] == "project"
    expected_error = "UnsupportedFixtureError: No controlled fixtures for intent 'project'"
    assert any(event.get("error") == expected_error for event in result["events"])
    boundaries.create_agent.assert_not_called()
    boundaries.execute.assert_not_called()
    assert result["tool_calls"] == []


def test_escaping_error_preserves_trace(mocker, boundaries):
    process = mocker.patch.object(
        assistant, "process_query", side_effect=RuntimeError("Flow failed")
    )
    original_map = assistant.get_intent_to_agent_map
    original_collaborative_map = collaborative.get_intent_to_agent_map
    result = collect_flow_case("rag-002", live=True)
    assert result["response"] is None
    assert result["error"] == "RuntimeError: Flow failed"
    assert result["events"] == [{"stage": "process_query", "error": "RuntimeError: Flow failed"}]
    assert assistant.process_query is process
    assert assistant.get_intent_to_agent_map is original_map
    assert collaborative.get_intent_to_agent_map is original_collaborative_map
    assert assistant.get_cached_response is boundaries.cache_read


@pytest.mark.usefixtures("_original_functions")
def test_real_collaboration_uses_fixtures_without_router(mocker, boundaries):
    sub_queries = [
        {"query": "Explain trademark usage", "intent": "rag"},
        {"query": "Explain logo usage", "intent": "rag"},
    ]
    boundaries.analyze.return_value = {"is_simple": False, "sub_queries": sub_queries}
    synthesizer = SimpleNamespace(
        role="OWASP Result Synthesizer", llm=SimpleNamespace(model="test-model"), tools=[]
    )
    mocker.patch.object(collaborative, "create_synthesizer_agent", return_value=synthesizer)
    result = collect_flow_case("rag-002", live=True)
    assert result["response"] == "Combined answer"
    assert result["error"] is None
    boundaries.route.assert_not_called()
    assert boundaries.create_agent.call_count == 2
    assert [call["query"] for call in result["tool_calls"]] == [
        item["query"] for item in sub_queries
    ]
    assert all(event["stage"] != "route" for event in result["events"])
    assert [event["role"] for event in result["events"] if event["stage"] == "execute_task"] == [
        "OWASP Knowledge Specialist",
        "OWASP Knowledge Specialist",
        "OWASP Result Synthesizer",
    ]


@pytest.fixture
def raw_record():
    """Provide an observation without scores without executing the assistant."""
    return {
        "case_id": "rag-002",
        "query": get_case_by_id("rag-002").query,
        "response": None,
        "events": [],
        "tool_calls": [],
        "error": None,
    }


@pytest.mark.parametrize(("intent", "passed"), [("rag", True), ("project", False)])
def test_intent_scoring_uses_observed_routing(raw_record, intent, passed):
    raw_record["events"] = [{"stage": "route", "result": {"intent": intent, "confidence": 0.81}}]
    result = score_flow_intent(raw_record)
    assert result["skipped"] == []
    assert len(result["scores"]) == 1
    score = result["scores"][0]
    assert score["passed"] is passed
    assert score["details"]["actual_intent"] == intent
    assert score["details"]["expected_intent"] == "rag"
    assert score["details"]["confidence"] == 0.81
    assert "scores" not in raw_record


@pytest.mark.parametrize(
    "events",
    [
        [],
        [{"stage": "handle_collaborative_query", "result": "Combined answer"}],
        [{"stage": "route", "error": "RuntimeError: Router failed"}],
        [{"stage": "route", "result": None}],
    ],
)
def test_intent_scoring_skips_unavailable_decisions(raw_record, events):
    raw_record["events"] = events
    assert score_flow_intent(raw_record) == {
        "scores": [],
        "skipped": [
            {
                "evaluator": "intent",
                "reason": "No successful router result was recorded",
            }
        ],
    }


def test_intent_scoring_uses_last_successful_route(raw_record):
    raw_record["events"] = [
        {"stage": "route", "result": {"intent": "project", "confidence": 0.4}},
        {"stage": "route", "result": {"intent": "rag", "confidence": 0.9}},
        {"stage": "route", "error": "RuntimeError: Later route failed"},
    ]
    result = score_flow_intent(raw_record)
    assert result["scores"][0]["passed"] is True
    assert result["scores"][0]["details"]["confidence"] == 0.9
    assert get_flow_errors(raw_record) == [raw_record["events"][-1]]


def test_intent_scoring_rejects_unknown_case(raw_record):
    raw_record["case_id"] = "unknown-case"
    with pytest.raises(ValueError, match="Unknown benchmark case"):
        score_flow_intent(raw_record)


def test_error_extraction_preserves_caught_and_escaping_failures(raw_record):
    raised = {"stage": "execute_task", "error": "RuntimeError: Provider failed"}
    logged = {
        "stage": "logged_error",
        "message": "Failed to process query",
        "error": "RuntimeError: Provider failed",
    }
    unknown_logged = {"stage": "logged_error", "message": "Failure", "error": None}
    raw_record["events"] = [
        {"stage": "process_query", "result": "Fallback answer"},
        raised,
        logged,
        unknown_logged,
    ]
    raw_record["error"] = "ValueError: Collector failed"
    errors = get_flow_errors(raw_record)
    assert errors == [
        raised,
        logged,
        unknown_logged,
        {"stage": "collector", "error": "ValueError: Collector failed"},
    ]
    errors[0]["error"] = "Edited report"
    assert raised["error"] == "RuntimeError: Provider failed"
    assert len(raw_record["events"]) == 4


def test_error_extraction_returns_empty_for_success(raw_record):
    raw_record["events"] = [{"stage": "process_query", "result": "Answer"}]
    assert get_flow_errors(raw_record) == []


@pytest.fixture
def record_for_scoring(raw_record):
    """Provide a complete positive-evidence RAG observation."""
    return raw_record | {
        "scope": "assistant_flow",
        "scenario": "relevant",
        "response": "OWASP trademark logo policy",
        "events": [{"stage": "route", "result": {"intent": "rag", "confidence": 0.95}}],
        "tool_calls": [
            {"tool": "Semantic search for OWASP content", "supporting_result_count": 1}
        ],
    }


@pytest.mark.parametrize("case_id", ["rag-002", "rag-003"])
@pytest.mark.parametrize(
    ("scenario", "status"),
    [
        ("relevant", "passed"),
        ("mixed", "passed"),
        ("irrelevant", "needs_review"),
        ("empty", "needs_review"),
    ],
)
def test_grader_scores_positive_evidence_and_reviews_negative_evidence(
    record_for_scoring, case_id, scenario, status
):
    record_for_scoring["case_id"] = case_id
    record_for_scoring["scenario"] = scenario
    if case_id == "rag-003":
        record_for_scoring["response"] = "OWASP code of conduct policy for event speakers"
    if scenario in ("irrelevant", "empty"):
        record_for_scoring["tool_calls"][0]["supporting_result_count"] = 0
    before = deepcopy(record_for_scoring)
    result = score_flow_case(record_for_scoring)
    assert result["status"] == status
    assert result["errors"] == []
    assert result["failure_reasons"] == []
    names = [score["name"] for score in result["scores"]]
    assert names[:2] == ["intent", "tool_selection"]
    if status == "passed":
        assert names[-1] == "response_coverage"
        assert result["skipped"] == []
    else:
        assert "response_coverage" not in names
        assert result["skipped"][0]["evaluator"] == "response_coverage"
    assert record_for_scoring == before
    assert result is not record_for_scoring


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    [
        ("tool_calls", [], "Missing expected tools"),
        (
            "tool_calls",
            [{"tool": "Semantic search for OWASP content", "supporting_result_count": 0}],
            "No supporting fixture",
        ),
        ("response", None, "empty response"),
        ("response", " ", "empty response"),
        ("response", "OWASP", "Missing expected keywords"),
        (
            "events",
            [{"stage": "route", "result": {"intent": "project", "confidence": 0.9}}],
            "Expected intent",
        ),
    ],
)
def test_grader_rejects_incomplete_or_incorrect_observations(
    record_for_scoring, field, value, reason
):
    record_for_scoring[field] = value
    result = score_flow_case(record_for_scoring)
    assert result["status"] == "failed"
    assert any(reason in failure for failure in result["failure_reasons"])


@pytest.mark.parametrize("scenario", ["relevant", "empty"])
@pytest.mark.parametrize("caught", [False, True])
def test_execution_errors_fail_even_with_matching_fallback_text(
    record_for_scoring, scenario, caught
):
    record_for_scoring["scenario"] = scenario
    if caught:
        record_for_scoring["events"].append(
            {
                "stage": "logged_error",
                "message": "Provider failed",
                "error": "RuntimeError: Provider failed",
            }
        )
    else:
        record_for_scoring["error"] = "RuntimeError: Provider failed"
    result = score_flow_case(record_for_scoring)
    assert result["status"] == "failed"
    assert result["errors"]
    assert "Execution errors were recorded" in result["failure_reasons"]


def test_missing_route_requires_review_even_when_other_checks_pass(record_for_scoring):
    record_for_scoring["events"] = [{"stage": "handle_collaborative_query", "result": "Answer"}]
    result = score_flow_case(record_for_scoring)
    assert result["status"] == "needs_review"
    assert result["skipped"][0]["evaluator"] == "intent"
    assert result["failure_reasons"] == []


def test_grader_rejects_unknown_case(record_for_scoring):
    record_for_scoring["case_id"] = "unknown-case"
    with pytest.raises(ValueError, match="Unknown benchmark case"):
        score_flow_case(record_for_scoring)


@pytest.mark.parametrize(
    ("scenario", "status"),
    [
        ("relevant", "passed"),
        ("mixed", "passed"),
        ("irrelevant", "needs_review"),
        ("empty", "needs_review"),
    ],
)
@pytest.mark.usefixtures("_original_functions")
def test_flow_runner_collects_and_grades_real_control_flow(boundaries, scenario, status):
    result = run_flow_case("rag-002", scenario, live=True)
    assert result["scope"] == "assistant_flow"
    assert result["status"] == status
    assert result["tool_calls"]
    assert result["events"]
    boundaries.analyze.assert_called_once()


def test_flow_runner_retains_live_opt_in(boundaries):
    with pytest.raises(ValueError, match="live=True"):
        run_flow_case("rag-002")
    boundaries.analyze.assert_not_called()
