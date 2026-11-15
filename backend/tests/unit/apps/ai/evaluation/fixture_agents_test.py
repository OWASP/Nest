import pytest

from apps.ai.common.intent import Intent
from apps.ai.evaluation.fixture_agents import (
    UnsupportedFixtureError,
    use_project_fixtures,
    use_rag_fixtures,
)
from apps.ai.flows import assistant, collaborative


@pytest.fixture(autouse=True)
def block_live_models(mocker):
    """Reject accidental model construction in scope tests."""
    mocker.patch(
        "apps.ai.common.llm_config.LLM",
        side_effect=AssertionError("Live model construction must not run"),
    )


def test_fixture_scope_supplies_rag_agents_and_restores_factories(mocker):
    """Replace both factory lookups and restore them after normal exit."""
    agent = mocker.sentinel.agent
    create_agent = mocker.patch(
        "apps.ai.evaluation.fixture_agents.create_fixture_rag_agent",
        return_value=agent,
    )
    tool_calls = []
    flows = (assistant, collaborative)
    originals = {flow: flow.get_intent_to_agent_map for flow in flows}

    with use_rag_fixtures("rag-002", "relevant", tool_calls):
        create_agent.assert_not_called()
        for flow in flows:
            factories = flow.get_intent_to_agent_map()
            assert set(factories) == set(Intent.values())
            assert factories["rag"]() is agent

    assert create_agent.call_args_list == [
        mocker.call("rag-002", "relevant", tool_calls),
        mocker.call("rag-002", "relevant", tool_calls),
    ]
    for flow in flows:
        assert flow.get_intent_to_agent_map is originals[flow]


@pytest.mark.parametrize("flow", [assistant, collaborative])
@pytest.mark.parametrize("intent", ["chapter", "community", "contribution", "gsoc", "project"])
def test_unsupported_expert_is_blocked_and_scope_restores(mocker, flow, intent):
    """Reject unsupported experts without constructing an agent."""
    create_agent = mocker.patch("apps.ai.evaluation.fixture_agents.create_fixture_rag_agent")
    flows = (assistant, collaborative)
    originals = {item: item.get_intent_to_agent_map for item in flows}

    with (
        pytest.raises(UnsupportedFixtureError, match=intent),
        use_rag_fixtures("rag-002", "relevant", []),
    ):
        flow.get_intent_to_agent_map()[intent]()

    create_agent.assert_not_called()
    for item in flows:
        assert item.get_intent_to_agent_map is originals[item]


def test_project_scope_defers_agent_creation_and_restores_both_lookups(mocker):
    agent = mocker.sentinel.project_agent
    factory = mocker.patch(
        "apps.ai.evaluation.fixture_agents.create_fixture_project_agent",
        return_value=agent,
    )
    rag_factory = mocker.patch("apps.ai.evaluation.fixture_agents.create_fixture_rag_agent")
    calls = []
    flows = (assistant, collaborative)
    originals = {flow: flow.get_intent_to_agent_map for flow in flows}

    with use_project_fixtures("proj-004", calls):
        factory.assert_not_called()
        for flow in flows:
            factories = flow.get_intent_to_agent_map()
            assert set(factories) == set(Intent.values())
            assert factories[Intent.PROJECT.value]() is agent

    assert factory.call_args_list == [
        mocker.call("proj-004", calls),
        mocker.call("proj-004", calls),
    ]
    assert all(call.args[1] is calls for call in factory.call_args_list)
    rag_factory.assert_not_called()
    for flow in flows:
        assert flow.get_intent_to_agent_map is originals[flow]


@pytest.mark.parametrize("flow", [assistant, collaborative])
@pytest.mark.parametrize("intent", ["chapter", "community", "contribution", "gsoc", "rag"])
def test_project_scope_blocks_other_experts_and_restores(mocker, flow, intent):
    factory = mocker.patch("apps.ai.evaluation.fixture_agents.create_fixture_project_agent")
    flows = (assistant, collaborative)
    originals = {item: item.get_intent_to_agent_map for item in flows}

    with (
        pytest.raises(UnsupportedFixtureError, match=intent),
        use_project_fixtures("proj-004", []),
    ):
        flow.get_intent_to_agent_map()[intent]()

    factory.assert_not_called()
    for item in flows:
        assert item.get_intent_to_agent_map is originals[item]


@pytest.mark.parametrize(
    ("scope", "args"),
    [
        (use_project_fixtures, ("proj-003", [])),
        (use_rag_fixtures, ("proj-004", "relevant", [])),
        (use_rag_fixtures, ("rag-002", "unknown", [])),
    ],
)
def test_invalid_fixture_is_rejected_before_patching_or_agent_creation(mocker, scope, args):
    project_factory = mocker.patch(
        "apps.ai.evaluation.fixture_agents.create_fixture_project_agent"
    )
    rag_factory = mocker.patch("apps.ai.evaluation.fixture_agents.create_fixture_rag_agent")
    lookups = [mocker.spy(flow, "get_intent_to_agent_map") for flow in (assistant, collaborative)]

    with pytest.raises(KeyError), scope(*args):
        pytest.fail("Invalid fixtures must fail before entering the caller's body")

    project_factory.assert_not_called()
    rag_factory.assert_not_called()
    for flow, lookup in zip((assistant, collaborative), lookups, strict=True):
        assert flow.get_intent_to_agent_map is lookup
        lookup.assert_not_called()


@pytest.mark.parametrize(
    ("scope", "args", "intent", "factory_name"),
    [
        (use_project_fixtures, ("proj-004", []), "project", "create_fixture_project_agent"),
        (use_rag_fixtures, ("rag-002", "relevant", []), "rag", "create_fixture_rag_agent"),
    ],
)
def test_agent_construction_failure_restores_both_lookups(
    mocker, scope, args, intent, factory_name
):
    failure = RuntimeError("Agent construction failed")
    factory = mocker.patch(
        f"apps.ai.evaluation.fixture_agents.{factory_name}", side_effect=failure
    )
    originals = {flow: flow.get_intent_to_agent_map for flow in (assistant, collaborative)}

    with pytest.raises(RuntimeError, match="Agent construction failed") as caught, scope(*args):
        assistant.get_intent_to_agent_map()[intent]()

    assert caught.value is failure
    factory.assert_called_once_with(*args)
    for flow, original in originals.items():
        assert flow.get_intent_to_agent_map is original


@pytest.mark.parametrize(
    ("scope", "args"),
    [
        (use_project_fixtures, ("proj-004", [])),
        (use_rag_fixtures, ("rag-002", "relevant", [])),
    ],
)
def test_caller_failure_restores_both_lookups(scope, args):
    failure = RuntimeError("Caller failed")
    originals = {flow: flow.get_intent_to_agent_map for flow in (assistant, collaborative)}

    with pytest.raises(RuntimeError, match="Caller failed") as caught, scope(*args):
        raise failure

    assert caught.value is failure
    for flow, original in originals.items():
        assert flow.get_intent_to_agent_map is original
