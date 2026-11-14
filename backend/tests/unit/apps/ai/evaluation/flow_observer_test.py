from types import SimpleNamespace

import pytest

from apps.ai.evaluation.flow_observer import observe_flow
from apps.ai.flows import assistant


# test fake flow (flow observer)
def test_observer_records_calls_bypasses_cache_and_restores_functions(mocker):
    analysis = {"complexity": "simple"}

    analyze = mocker.patch.object(
        assistant,
        "analyze_query",
        return_value=analysis,
    )
    cache_read = mocker.patch.object(assistant, "get_cached_response")
    cache_write = mocker.patch.object(assistant, "store_cached_response")

    def fake_process_query(query):
        assistant.analyze_query(query)
        return "Test answer"

    mocker.patch.object(
        assistant,
        "process_query",
        new=fake_process_query,
    )

    names = (
        "process_query",
        "analyze_query",
        "route",
        "handle_collaborative_query",
        "execute_task",
        "get_cached_response",
        "store_cached_response",
    )
    originals = {name: getattr(assistant, name) for name in names}

    with observe_flow() as events:
        assert assistant.get_cached_response("Test question") is None
        assert assistant.store_cached_response("Test question", "Test answer") is None
        response = assistant.process_query("Test question")

    assert response == "Test answer"
    analyze.assert_called_once_with("Test question")
    cache_read.assert_not_called()
    cache_write.assert_not_called()

    assert events == [
        {"stage": "process_query", "result": "Test answer"},
        {"stage": "analyze_query", "result": {"complexity": "simple"}},
    ]

    analysis["complexity"] = "changed"
    assert events[1]["result"] == {"complexity": "simple"}

    for name, original in originals.items():
        assert getattr(assistant, name) is original


def test_observer_records_and_propagates_errors(mocker):
    failure = RuntimeError("Provider failed")
    process = mocker.patch.object(
        assistant,
        "process_query",
        side_effect=failure,
    )
    original_cache_read = assistant.get_cached_response

    with (
        pytest.raises(RuntimeError, match="Provider failed") as caught,
        observe_flow() as events,
    ):
        assistant.process_query("Test question")

    assert caught.value is failure
    assert events == [
        {
            "stage": "process_query",
            "error": "RuntimeError: Provider failed",
        },
    ]
    assert assistant.process_query is process
    assert assistant.get_cached_response is original_cache_read


def test_observer_records_errors_even_when_flow_returns_fallback(mocker):
    log_exception = mocker.patch.object(assistant.logger, "exception")
    provider = mocker.Mock(side_effect=RuntimeError("Provider failed"))

    def fake_process_query(query):
        try:
            provider()
        except RuntimeError:
            assistant.logger.exception("Agent execution failed")
            return f"Fallback for {query}"

    mocker.patch.object(
        assistant,
        "process_query",
        new=fake_process_query,
    )

    with observe_flow() as events:
        response = assistant.process_query("Test question")

    assert response == "Fallback for Test question"
    assert events == [
        {
            "stage": "process_query",
            "result": "Fallback for Test question",
        },
        {
            "stage": "logged_error",
            "message": "Agent execution failed",
            "error": "RuntimeError: Provider failed",
        },
    ]
    log_exception.assert_called_once_with("Agent execution failed")
    assert assistant.logger.exception is log_exception


@pytest.mark.parametrize("use_keywords", [False, True])
def test_observer_records_executing_agent(mocker, use_keywords):
    agent = SimpleNamespace(
        role="RAG Agent",
        llm=SimpleNamespace(model="test-model"),
    )
    execute = mocker.patch.object(
        assistant,
        "execute_task",
        return_value="Test answer",
    )

    if use_keywords:
        args = ()
        kwargs = {"agent": agent, "query": "Test question"}
    else:
        args = (agent, "Test question")
        kwargs = {}

    with observe_flow() as events:
        response = assistant.execute_task(*args, **kwargs)

    assert response == "Test answer"
    execute.assert_called_once_with(*args, **kwargs)
    assert assistant.execute_task is execute
    assert events == [
        {
            "stage": "execute_task",
            "role": "RAG Agent",
            "model": "test-model",
            "query": "Test question",
            "result": "Test answer",
        },
    ]
