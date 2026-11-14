"""Supply controlled expert agents during sequential evaluations."""

from collections.abc import Callable, Generator
from contextlib import contextmanager
from functools import partial
from unittest.mock import patch

from crewai import Agent

from apps.ai.common.intent import Intent
from apps.ai.evaluation.datasets.rag_fixtures import get_rag_fixture
from apps.ai.evaluation.rag_runner import create_fixture_rag_agent
from apps.ai.flows import assistant, collaborative


class UnsupportedFixtureError(RuntimeError):
    """An expert was selected without controlled fixtures."""


@contextmanager
def use_rag_fixtures(
    case_id: str,
    scenario: str,
    tool_calls: list[dict],
) -> Generator[None]:
    """Supply fixture-backed RAG agents and reject other expert factories."""
    get_rag_fixture(case_id, scenario)

    def create_agent() -> Agent:
        return create_fixture_rag_agent(case_id, scenario, tool_calls)

    def unsupported_agent(intent: str) -> Agent:
        msg = f"No controlled fixtures for intent '{intent}'"
        raise UnsupportedFixtureError(msg)

    factories: dict[str, Callable[[], Agent]] = {
        intent: partial(unsupported_agent, intent) for intent in Intent.values()
    }
    factories[Intent.RAG.value] = create_agent

    with (
        patch.object(assistant, "get_intent_to_agent_map", return_value=factories),
        patch.object(collaborative, "get_intent_to_agent_map", return_value=factories),
    ):
        yield
