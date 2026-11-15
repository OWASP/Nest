"""Supply controlled expert agents during sequential evaluations."""

from collections.abc import Callable, Generator
from contextlib import contextmanager
from functools import partial
from unittest.mock import patch

from crewai import Agent

from apps.ai.common.intent import Intent
from apps.ai.evaluation.datasets.project_fixtures import get_project_fixture
from apps.ai.evaluation.datasets.rag_fixtures import get_rag_fixture
from apps.ai.evaluation.project_runner import create_fixture_project_agent
from apps.ai.evaluation.rag_runner import create_fixture_rag_agent
from apps.ai.flows import assistant, collaborative


class UnsupportedFixtureError(RuntimeError):
    """An expert was selected without controlled fixtures."""


@contextmanager
def _use_fixture_agent(
    intent: str,
    factory: Callable[[], Agent],
) -> Generator[None]:
    """Install one controlled expert factory in both assistant paths."""

    def unsupported_agent(selected_intent: str) -> Agent:
        msg = f"No controlled fixtures for intent '{selected_intent}'"
        raise UnsupportedFixtureError(msg)

    factories: dict[str, Callable[[], Agent]] = {
        value: partial(unsupported_agent, value) for value in Intent.values()
    }
    factories[intent] = factory

    with (
        patch.object(assistant, "get_intent_to_agent_map", return_value=factories),
        patch.object(collaborative, "get_intent_to_agent_map", return_value=factories),
    ):
        yield


@contextmanager
def use_rag_fixtures(
    case_id: str,
    scenario: str,
    tool_calls: list[dict],
) -> Generator[None]:
    """Supply controlled RAG agents after validating the fixture."""
    get_rag_fixture(case_id, scenario)
    factory = partial(create_fixture_rag_agent, case_id, scenario, tool_calls)

    with _use_fixture_agent(Intent.RAG.value, factory):
        yield


@contextmanager
def use_project_fixtures(
    case_id: str,
    tool_calls: list[dict],
) -> Generator[None]:
    """Supply controlled project agents after validating the fixture."""
    get_project_fixture(case_id)
    factory = partial(create_fixture_project_agent, case_id, tool_calls)

    with _use_fixture_agent(Intent.PROJECT.value, factory):
        yield
