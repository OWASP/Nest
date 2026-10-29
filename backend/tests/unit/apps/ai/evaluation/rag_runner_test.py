import pytest

from apps.ai.agents.rag.tools import semantic_search
from apps.ai.evaluation.rag_runner import create_fixture_search, run_rag_case


@pytest.fixture(autouse=True)
def block_live_embeddings(mocker):
    mocker.patch(
        "apps.ai.agents.rag.tools.get_embedder",
        side_effect=AssertionError("Live retrieval must not run in these tests"),
    )


def test_fixture_search_is_independent_and_honors_limits():
    original_function = semantic_search.func
    tool_calls = []
    search = create_fixture_search("rag-002", "relevant", tool_calls)

    first_result = search.run(query="A rephrased question", limit=1)
    original_text = first_result[0]["text"]
    first_result[0]["text"] = "Changed by another call"

    second_result = search.run(query="Another question", limit=1)

    assert second_result[0]["text"] == original_text
    assert search.run(query="No results requested", limit=0) == []
    assert [call["result_count"] for call in tool_calls] == [1, 1, 0]
    assert tool_calls[0]["query"] == "A rephrased question"
    assert search.name == semantic_search.name
    assert search.args_schema is semantic_search.args_schema
    assert semantic_search.func is original_function

    with pytest.raises(ValueError, match="non-negative"):
        search.run(query="Invalid limit", limit=-1)


@pytest.mark.parametrize(
    ("scenario", "use_tool", "limit", "response", "expected_status"),
    [
        ("relevant", True, 5, "OWASP trademark logo policy", "passed"),
        ("relevant", False, 5, "OWASP trademark logo policy", "failed"),
        ("relevant", True, 5, "OWASP", "failed"),
        ("relevant", True, 0, "OWASP trademark logo policy", "failed"),
        ("irrelevant", True, 5, "OWASP trademark logo policy", "needs_review"),
        ("empty", True, 5, "OWASP trademark logo policy", "needs_review"),
        ("empty", True, 5, " ", "failed"),
        ("mixed", True, 5, "OWASP trademark logo policy", "passed"),
        ("mixed", False, 5, "OWASP trademark logo policy", "failed"),
        ("mixed", True, 5, "OWASP", "failed"),
        ("mixed", True, 0, "OWASP trademark logo policy", "failed"),
        ("mixed", True, 1, "OWASP trademark logo policy", "failed"),
        ("mixed", True, 2, "OWASP trademark logo policy", "passed"),
    ],
)
def test_rag_runner_reports_observed_results(
    mocker,
    scenario,
    use_tool,
    limit,
    response,
    expected_status,
):
    factory = mocker.patch("apps.ai.evaluation.rag_runner.create_rag_agent")
    factory.return_value.llm.model = "test-model"

    def execute_with_fixture(agent, query):
        if use_tool:
            agent.tools[0].run(query=query, limit=limit)
        return response

    mocker.patch(
        "apps.ai.evaluation.rag_runner.execute_task",
        side_effect=execute_with_fixture,
    )

    result = run_rag_case("rag-002", scenario, live=True)

    assert result["status"] == expected_status
    assert result["response"] == response
    assert result["scope"] == "rag_agent"
    assert result["model"] == "test-model"
    assert len(result["tool_calls"]) == int(use_tool)

    expected_scores = ["tool_selection"]
    if scenario in ("relevant", "mixed"):
        expected_scores.append("response_coverage")

    assert [score["name"] for score in result["scores"]] == expected_scores


def test_rag_runner_requires_live_opt_in(mocker):
    factory = mocker.patch("apps.ai.evaluation.rag_runner.create_rag_agent")

    with pytest.raises(ValueError, match="live=True"):
        run_rag_case("rag-002")

    factory.assert_not_called()


@pytest.mark.parametrize(
    ("case_id", "expected_error"),
    [
        ("unknown-case", ValueError),
        ("rag-001", KeyError),
    ],
)
def test_missing_cases_or_fixtures_fail_before_agent_creation(
    mocker,
    case_id,
    expected_error,
):
    factory = mocker.patch("apps.ai.evaluation.rag_runner.create_rag_agent")

    with pytest.raises(expected_error):
        run_rag_case(case_id, live=True)

    factory.assert_not_called()


def test_agent_execution_errors_are_propagated(mocker):
    mocker.patch("apps.ai.evaluation.rag_runner.create_rag_agent")
    mocker.patch(
        "apps.ai.evaluation.rag_runner.execute_task",
        side_effect=RuntimeError("Provider failed"),
    )

    with pytest.raises(RuntimeError, match="Provider failed"):
        run_rag_case("rag-002", live=True)


@pytest.mark.parametrize(
    ("scenario", "limit", "expected_status", "supporting_count"),
    [
        ("relevant", 5, "passed", 1),
        ("mixed", 5, "passed", 1),
        ("mixed", 1, "failed", 0),
        ("irrelevant", 5, "needs_review", 0),
        ("empty", 5, "needs_review", 0),
    ],
)
def test_speaker_policy_case(
    mocker,
    scenario,
    limit,
    expected_status,
    supporting_count,
):
    factory = mocker.patch("apps.ai.evaluation.rag_runner.create_rag_agent")
    factory.return_value.llm.model = "test-model"
    response = "OWASP's code of conduct policy applies to event speakers."

    def execute_with_fixture(agent, query):
        agent.tools[0].run(query=query, limit=limit)
        return response

    mocker.patch(
        "apps.ai.evaluation.rag_runner.execute_task",
        side_effect=execute_with_fixture,
    )

    result = run_rag_case("rag-003", scenario, live=True)

    assert result["case_id"] == "rag-003"
    assert result["status"] == expected_status
    assert result["response"] == response
    assert len(result["tool_calls"]) == 1
    assert result["tool_calls"][0]["supporting_result_count"] == supporting_count
