import pytest

from apps.ai.common.intent import Intent
from apps.ai.evaluation.fixture_agents import UnsupportedFixtureError, use_rag_fixtures
from apps.ai.flows import assistant, collaborative


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
