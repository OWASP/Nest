from copy import deepcopy
from dataclasses import replace
from types import SimpleNamespace

import pytest

from apps.ai.agents.project import tools as project_tools
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
def project_boundaries(mocker, boundaries):
    """Use actual project tool clones and flow, replacing only model boundaries."""
    tools = [
        project_tools.get_flagship_projects,
        project_tools.get_production_projects,
        project_tools.get_lab_projects,
        project_tools.get_incubator_projects,
        project_tools.get_project_age,
        project_tools.search_projects,
    ]
    for tool in tools:
        mocker.patch.object(
            tool, "func", side_effect=AssertionError("Original project tool must not run")
        )
    boundaries.agent.role = "OWASP Project Specialist"
    boundaries.agent.tools = tools
    boundaries.project_factory = mocker.patch(
        "apps.ai.evaluation.project_runner.create_project_agent", return_value=boundaries.agent
    )
    boundaries.route.return_value = {"intent": "project", "confidence": 0.95}

    def answer_with_project_fixture(agent, query=None, **_kwargs):
        if not agent.tools:
            return "Combined project answer"
        search = next(
            tool for tool in agent.tools if tool.name == project_tools.search_projects.name
        )
        return search.run(query=query)

    boundaries.execute.side_effect = answer_with_project_fixture
    return boundaries


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
@pytest.mark.parametrize("case_id", ["rag-002", "proj-004"])
def test_collector_requires_live_opt_in(boundaries, case_id):
    with pytest.raises(ValueError, match="live=True"):
        collect_flow_case(case_id)
    boundaries.analyze.assert_not_called()
    boundaries.create_agent.assert_not_called()


@pytest.mark.parametrize(
    ("case_id", "scenario", "error"),
    [
        ("unknown-case", "relevant", ValueError),
        ("proj-003", "relevant", ValueError),
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
def test_project_collector_records_real_flow_and_controlled_search(project_boundaries):
    result = collect_flow_case("proj-004", live=True)
    query = get_case_by_id("proj-004").query
    assert result["scope"] == "assistant_flow"
    assert result["case_id"] == "proj-004"
    assert result["scenario"] == "relevant"
    assert result["query"] == query
    assert "Dependency-Check" in result["response"]
    assert result["error"] is None
    assert "status" not in result
    assert "scores" not in result
    assert [event["stage"] for event in result["events"]] == [
        "process_query",
        "analyze_query",
        "route",
        "execute_task",
    ]
    assert result["events"][2]["result"] == {"intent": "project", "confidence": 0.95}
    assert result["events"][3]["role"] == "OWASP Project Specialist"
    assert result["tool_calls"] == [
        {
            "tool": project_tools.search_projects.name,
            "query": query,
            "limit": 5,
            "result_count": 1,
        }
    ]
    project_boundaries.project_factory.assert_called_once_with()
    project_boundaries.create_agent.assert_not_called()
    project_boundaries.cache_read.assert_not_called()
    project_boundaries.cache_write.assert_not_called()


@pytest.mark.parametrize("scenario", ["irrelevant", "empty", "mixed", "all", "unknown"])
@pytest.mark.usefixtures("_original_functions")
def test_project_scenarios_are_rejected_before_models(project_boundaries, scenario):
    with pytest.raises(ValueError, match="only the relevant scenario"):
        collect_flow_case("proj-004", scenario, live=True)
    project_boundaries.analyze.assert_not_called()
    project_boundaries.route.assert_not_called()
    project_boundaries.project_factory.assert_not_called()
    project_boundaries.execute.assert_not_called()


@pytest.mark.parametrize("intent", ["rag", "community"])
@pytest.mark.usefixtures("_original_functions")
def test_project_misrouting_blocks_uncontrolled_experts(project_boundaries, intent):
    project_boundaries.route.return_value = {"intent": intent, "confidence": 0.9}
    result = collect_flow_case("proj-004", live=True)
    assert result["events"][2]["result"]["intent"] == intent
    assert any(
        event.get("error")
        == f"UnsupportedFixtureError: No controlled fixtures for intent '{intent}'"
        for event in result["events"]
    )
    assert result["tool_calls"] == []
    project_boundaries.project_factory.assert_not_called()
    project_boundaries.create_agent.assert_not_called()
    project_boundaries.execute.assert_not_called()


@pytest.mark.usefixtures("_original_functions")
def test_project_provider_failure_remains_observable(project_boundaries):
    project_boundaries.execute.side_effect = RuntimeError("Project provider failed")
    result = collect_flow_case("proj-004", live=True)
    assert result["error"] is None
    assert result["response"].strip()
    assert any(
        event["stage"] == "execute_task"
        and event.get("error") == "RuntimeError: Project provider failed"
        for event in result["events"]
    )
    assert result["tool_calls"] == []


@pytest.mark.usefixtures("_original_functions")
def test_project_tool_error_survives_when_execution_catches_it(project_boundaries):
    def catch_tool_error(agent, query=None, **_kwargs):
        with pytest.raises(ValueError, match="No controlled fixture"):
            agent.tools[1].run()
        search = next(
            tool for tool in agent.tools if tool.name == project_tools.search_projects.name
        )
        return search.run(query=query)

    project_boundaries.execute.side_effect = catch_tool_error
    result = collect_flow_case("proj-004", live=True)
    assert result["error"] is None
    assert "Dependency-Check" in result["response"]
    assert not any(event.get("error") for event in result["events"])
    assert result["tool_calls"][0] == {
        "tool": project_tools.get_production_projects.name,
        "error": f"No controlled fixture for tool '{project_tools.get_production_projects.name}'",
    }
    assert result["tool_calls"][1]["result_count"] == 1


@pytest.mark.usefixtures("_original_functions")
def test_project_collaboration_uses_controlled_experts_without_router(mocker, project_boundaries):
    sub_queries = [
        {"query": "Find Dependency-Check", "intent": "project"},
        {"query": "Explain Dependency-Check", "intent": "project"},
    ]
    project_boundaries.analyze.return_value = {"is_simple": False, "sub_queries": sub_queries}
    synthesizer = SimpleNamespace(
        role="OWASP Result Synthesizer", llm=SimpleNamespace(model="test-model"), tools=[]
    )
    mocker.patch.object(collaborative, "create_synthesizer_agent", return_value=synthesizer)
    result = collect_flow_case("proj-004", live=True)
    assert result["response"] == "Combined project answer"
    assert result["error"] is None
    project_boundaries.route.assert_not_called()
    assert project_boundaries.project_factory.call_count == 2
    assert [call["query"] for call in result["tool_calls"]] == [
        item["query"] for item in sub_queries
    ]
    assert all(event["stage"] != "route" for event in result["events"])


@pytest.mark.usefixtures("_original_functions")
def test_channel_case_is_rejected_before_model_execution(mocker, boundaries):
    case = replace(get_case_by_id("rag-002"), channel_id="C_TEST")
    mocker.patch("apps.ai.evaluation.flow_runner.get_case_by_id", return_value=case)
    with pytest.raises(ValueError, match="Channel-scoped"):
        collect_flow_case("rag-002", live=True)
    boundaries.analyze.assert_not_called()
    boundaries.create_agent.assert_not_called()


@pytest.mark.parametrize("case_id", ["rag-001", "rag-002", "rag-003"])
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


@pytest.mark.parametrize("case_id", ["rag-001", "rag-002", "rag-003"])
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
    if case_id == "rag-001":
        record_for_scoring["response"] = "OWASP improves software security"
    elif case_id == "rag-003":
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


@pytest.fixture
def project_record_for_scoring(record_for_scoring):
    case = get_case_by_id("proj-004")
    return record_for_scoring | {
        "case_id": case.id,
        "query": case.query,
        "response": "Dependency-Check detects dependencies with known vulnerabilities.",
        "events": [{"stage": "route", "result": {"intent": "project", "confidence": 0.95}}],
        "tool_calls": [{"tool": project_tools.search_projects.name, "result_count": 1}],
    }


def test_project_grader_uses_project_counts_and_preserves_raw_record(project_record_for_scoring):
    before = deepcopy(project_record_for_scoring)
    result = score_flow_case(project_record_for_scoring)
    assert result["status"] == "passed"
    assert [score["name"] for score in result["scores"]] == [
        "intent",
        "tool_selection",
        "response_coverage",
    ]
    assert all(score["passed"] for score in result["scores"])
    assert result["failure_reasons"] == []
    assert result["errors"] == []
    assert result["skipped"] == []
    assert result is not project_record_for_scoring
    assert project_record_for_scoring == before


@pytest.mark.parametrize("count", [None, 0, -1])
def test_project_grader_requires_positive_project_count(project_record_for_scoring, count):
    call = project_record_for_scoring["tool_calls"][0]
    if count is None:
        del call["result_count"]
    else:
        call["result_count"] = count
    call["supporting_result_count"] = 1
    result = score_flow_case(project_record_for_scoring)
    assert result["status"] == "failed"
    assert "No supporting fixture results were returned" in result["failure_reasons"]


def test_rag_grader_does_not_treat_irrelevant_results_as_support(record_for_scoring):
    record_for_scoring["tool_calls"][0] = {
        "tool": "Semantic search for OWASP content",
        "result_count": 5,
        "supporting_result_count": 0,
    }
    result = score_flow_case(record_for_scoring)
    assert result["status"] == "failed"
    assert "No supporting fixture results were returned" in result["failure_reasons"]


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    [
        ("tool_calls", [], "Missing expected tools"),
        ("response", "", "empty response"),
        ("response", "A useful OWASP project", "Missing expected keywords"),
        (
            "events",
            [{"stage": "route", "result": {"intent": "rag", "confidence": 0.9}}],
            "Expected intent",
        ),
    ],
)
def test_project_grader_rejects_incomplete_observations(
    project_record_for_scoring, field, value, reason
):
    project_record_for_scoring[field] = value
    result = score_flow_case(project_record_for_scoring)
    assert result["status"] == "failed"
    assert any(reason in failure for failure in result["failure_reasons"])


def test_project_without_routing_requires_review(project_record_for_scoring):
    project_record_for_scoring["events"] = []
    result = score_flow_case(project_record_for_scoring)
    assert result["status"] == "needs_review"
    assert result["skipped"][0]["evaluator"] == "intent"
    assert result["failure_reasons"] == []


@pytest.mark.parametrize("case_id", ["rag-002", "proj-004"])
@pytest.mark.parametrize("scenario", ["unknown", "all"])
def test_grader_rejects_unknown_scenarios(record_for_scoring, case_id, scenario):
    record_for_scoring.update(case_id=case_id, scenario=scenario)
    with pytest.raises(ValueError, match="Unsupported scenario"):
        score_flow_case(record_for_scoring)


@pytest.mark.parametrize("scenario", ["mixed", "empty", "irrelevant"])
def test_project_grader_rejects_unimplemented_scenarios(project_record_for_scoring, scenario):
    project_record_for_scoring["scenario"] = scenario
    with pytest.raises(ValueError, match="Unsupported scenario"):
        score_flow_case(project_record_for_scoring)


def test_grader_rejects_case_without_controlled_fixtures(record_for_scoring):
    record_for_scoring["case_id"] = "proj-003"
    with pytest.raises(ValueError, match="No grading rules"):
        score_flow_case(record_for_scoring)


def test_error_extraction_copies_tool_errors_and_preserves_order(raw_record):
    event = {"stage": "execute_task", "error": "Provider failed"}
    tool_error = {"tool": "Blocked tool", "error": "No fixture", "query": "Example"}
    raw_record["events"] = [event]
    raw_record["tool_calls"] = [
        {"tool": "Successful tool", "result_count": 1},
        tool_error,
        {"tool": "Successful tool", "error": None},
    ]
    raw_record["error"] = "Collector failed"
    before = deepcopy(raw_record)
    errors = get_flow_errors(raw_record)
    assert errors == [
        event,
        tool_error | {"stage": "tool"},
        {"stage": "collector", "error": "Collector failed"},
    ]
    errors[1]["error"] = "Changed report"
    assert raw_record == before


@pytest.mark.parametrize("case_id", ["rag-002", "proj-004"])
def test_failed_tool_call_cannot_supply_evidence(
    record_for_scoring, project_record_for_scoring, case_id
):
    record = project_record_for_scoring if case_id == "proj-004" else record_for_scoring
    record["tool_calls"][0]["error"] = "Tool failed after preparing results"
    result = score_flow_case(record)
    assert result["status"] == "failed"
    assert "No supporting fixture results were returned" in result["failure_reasons"]
    assert "Execution errors were recorded" in result["failure_reasons"]
    assert result["errors"][0]["stage"] == "tool"


@pytest.mark.usefixtures("_original_functions")
def test_project_runner_collects_and_grades_real_control_flow(project_boundaries):
    result = run_flow_case("proj-004", live=True)
    assert result["status"] == "passed"
    assert result["scope"] == "assistant_flow"
    assert result["errors"] == []
    assert result["tool_calls"][0]["result_count"] == 1
    project_boundaries.analyze.assert_called_once()


@pytest.mark.usefixtures("_original_functions")
def test_caught_project_tool_failure_fails_full_flow_grading(project_boundaries):
    def catch_error_and_answer(agent, query=None, **_kwargs):
        with pytest.raises(ValueError, match="No controlled fixture"):
            agent.tools[1].run()
        search = next(
            tool for tool in agent.tools if tool.name == project_tools.search_projects.name
        )
        return search.run(query=query)

    project_boundaries.execute.side_effect = catch_error_and_answer
    result = run_flow_case("proj-004", live=True)
    assert all(score["passed"] for score in result["scores"])
    assert result["status"] == "failed"
    assert result["failure_reasons"] == ["Execution errors were recorded"]
    assert result["errors"] == [result["tool_calls"][0] | {"stage": "tool"}]
    assert not any(event.get("error") for event in result["events"])


@pytest.mark.usefixtures("_original_functions")
def test_flagship_case_collects_and_grades_real_flow(project_boundaries):
    def answer_with_flagship(agent, query=None, **_kwargs):  # noqa: ARG001
        tool = next(
            tool for tool in agent.tools if tool.name == project_tools.get_flagship_projects.name
        )
        return tool.run()

    project_boundaries.execute.side_effect = answer_with_flagship
    result = run_flow_case("proj-001", live=True)
    assert result["status"] == "passed"
    assert result["case_id"] == "proj-001"
    assert "Juice Shop" in result["response"]
    assert "Dependency-Check" in result["response"]
    assert result["tool_calls"] == [
        {"tool": project_tools.get_flagship_projects.name, "limit": 15, "result_count": 2}
    ]
    assert result["errors"] == []
    assert all(score["passed"] for score in result["scores"])
    project_boundaries.create_agent.assert_not_called()


@pytest.mark.usefixtures("_original_functions")
def test_search_cannot_replace_required_flagship_tool(project_boundaries):
    result = run_flow_case("proj-001", live=True)
    project_boundaries.execute.assert_called_once()
    assert result["tool_calls"][0]["tool"] == project_tools.search_projects.name
    assert result["status"] == "failed"
    assert any("Missing expected tools" in reason for reason in result["failure_reasons"])
