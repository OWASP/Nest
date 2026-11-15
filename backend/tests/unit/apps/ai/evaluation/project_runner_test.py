from types import SimpleNamespace

import pytest

from apps.ai.agents.project import tools as project_tools
from apps.ai.agents.project.tools.formatters import format_project_results
from apps.ai.evaluation.datasets.project_fixtures import get_project_fixture
from apps.ai.evaluation.project_runner import (
    create_fixture_project_agent,
    create_fixture_project_flagship,
    create_fixture_project_incubator,
    create_fixture_project_search,
    create_unavailable_project_tool,
)

TOOLS = (
    project_tools.get_flagship_projects,
    project_tools.get_production_projects,
    project_tools.get_lab_projects,
    project_tools.get_incubator_projects,
    project_tools.get_project_age,
    project_tools.search_projects,
)


@pytest.fixture(autouse=True)
def block_live_dependencies(mocker):
    """Reject real model construction and original tool execution."""
    mocker.patch(
        "apps.ai.common.llm_config.LLM",
        side_effect=AssertionError("Live model construction must not run"),
    )
    for tool in TOOLS:
        mocker.patch.object(
            tool, "func", side_effect=AssertionError("Original project tool must not run")
        )


@pytest.mark.parametrize(("limit", "count"), [(0, 0), (1, 1), (5, 1)])
def test_fixture_search_preserves_interface_and_records_calls(limit, count):
    original = project_tools.search_projects
    original_function = original.func
    calls = []
    search = create_fixture_project_search("proj-004", calls)
    query = "Dependency-Check"
    result = search.run(query=query, limit=limit)
    assert isinstance(result, str)
    assert result == format_project_results(get_project_fixture("proj-004")[:limit])
    assert calls == [
        {"tool": original.name, "query": query, "limit": limit, "result_count": count}
    ]
    assert search is not original
    assert search.name == original.name
    assert search.description == original.description
    assert search.args_schema is original.args_schema
    assert original.func is original_function


def test_negative_limit_is_rejected_without_recording_success():
    calls = []
    search = create_fixture_project_search("proj-004", calls)
    with pytest.raises(ValueError, match="non-negative"):
        search.run(query="Dependency-Check", limit=-1)
    assert calls == []


def test_unknown_case_is_rejected_before_agent_construction(mocker):
    factory = mocker.patch("apps.ai.evaluation.project_runner.create_project_agent")
    with pytest.raises(KeyError):
        create_fixture_project_agent("proj-003", [])
    factory.assert_not_called()


@pytest.mark.parametrize("original", TOOLS[1:-1], ids=lambda tool: tool.name)
def test_unavailable_tools_preserve_schema_and_record_errors(original):
    calls = []
    original_function = original.func
    blocked = create_unavailable_project_tool(original, calls)
    with pytest.raises(ValueError, match="No controlled fixture"):
        blocked.run()
    assert calls == [
        {
            "tool": original.name,
            "error": f"No controlled fixture for tool '{original.name}'",
        }
    ]
    assert blocked.name == original.name
    assert blocked.args_schema is original.args_schema
    assert original.func is original_function


def test_project_agent_keeps_all_choices_with_controlled_implementations(mocker):
    agent = SimpleNamespace(tools=list(TOOLS), cache=True)
    factory = mocker.patch(
        "apps.ai.evaluation.project_runner.create_project_agent", return_value=agent
    )
    original_functions = [tool.func for tool in TOOLS]
    calls = []
    result = create_fixture_project_agent("proj-004", calls)
    assert result is agent
    assert result.cache is False
    factory.assert_called_once_with()
    assert [tool.name for tool in result.tools] == [tool.name for tool in TOOLS]
    for cloned, original in zip(result.tools, TOOLS, strict=True):
        assert cloned is not original
        assert cloned.args_schema is original.args_schema
        if original is project_tools.search_projects:
            assert "Dependency-Check" in cloned.run(query="dependency")
        elif original is project_tools.get_flagship_projects:
            assert "Dependency-Check" in cloned.run()
        else:
            with pytest.raises(ValueError, match="No controlled fixture"):
                cloned.run()
    assert [call["tool"] for call in calls] == [tool.name for tool in TOOLS]
    assert calls[0]["result_count"] == 1
    assert all("error" in call for call in calls[1:-1])
    assert calls[-1]["result_count"] == 1
    assert [tool.func for tool in TOOLS] == original_functions


@pytest.mark.parametrize(("limit", "count"), [(-1, 0), (0, 0), (1, 1), (15, 2), (100, 2)])
def test_flagship_tool_preserves_interface_and_clamps_limit(limit, count):
    original = project_tools.get_flagship_projects
    original_function = original.func
    calls = []
    tool = create_fixture_project_flagship("proj-001", calls)
    result = tool.run(limit=limit)
    assert result == format_project_results(get_project_fixture("proj-001")[:count], "Flagship")
    assert calls == [{"tool": original.name, "limit": limit, "result_count": count}]
    assert tool is not original
    assert tool.name == original.name
    assert tool.description == original.description
    assert tool.args_schema is original.args_schema
    assert original.func is original_function


def test_flagship_default_matches_production_default():
    calls = []
    result = create_fixture_project_flagship("proj-001", calls).run()
    assert "Dependency-Check" in result
    assert "Juice Shop" in result
    assert calls[0]["limit"] == 15
    assert calls[0]["result_count"] == 2


def test_flagship_filters_levels_before_limiting(mocker):
    records = [
        {"idx_name": "Synthetic lab", "idx_level": "lab"},
        {"idx_name": "Synthetic flagship", "idx_level": "FLAGSHIP"},
        {"idx_name": "Synthetic unknown", "idx_level": None},
        {"idx_name": "Synthetic second", "idx_level": "flagship"},
    ]
    mocker.patch("apps.ai.evaluation.project_runner.get_project_fixture", return_value=records)
    calls = []
    result = create_fixture_project_flagship("synthetic", calls).run(limit=1)
    assert result == format_project_results([records[1]], "Flagship")
    assert calls[0]["result_count"] == 1


@pytest.mark.parametrize(("limit", "count"), [(15, 15), (30, 30), (100, 30)])
def test_flagship_maximum_matches_production_cap(mocker, limit, count):
    records = [
        {"idx_name": f"Synthetic project {index}", "idx_level": "flagship"} for index in range(40)
    ]
    mocker.patch("apps.ai.evaluation.project_runner.get_project_fixture", return_value=records)
    calls = []
    result = create_fixture_project_flagship("synthetic", calls).run(limit=limit)
    assert result == format_project_results(records[:count], "Flagship")
    assert calls[0]["result_count"] == count


@pytest.mark.parametrize(("limit", "count"), [(-1, 1), (0, 0), (1, 1), (10, 2)])
def test_incubator_helper_preserves_production_slicing_and_tool_interface(mocker, limit, count):
    records = [
        {"idx_name": "Synthetic flagship", "idx_level": "flagship"},
        {"idx_name": "Synthetic incubator one", "idx_level": "incubator"},
        {"idx_name": "Synthetic incubator two", "idx_level": "INCUBATOR"},
    ]
    mocker.patch("apps.ai.evaluation.project_runner.get_project_fixture", return_value=records)
    calls = []
    original = project_tools.get_incubator_projects
    original_function = original.func
    tool = create_fixture_project_incubator("synthetic", calls)
    assert tool.run(limit=limit) == format_project_results(records[1:][:count], "Incubator")
    assert calls == [{"tool": original.name, "limit": limit, "result_count": count}]
    assert tool.name == original.name
    assert tool.args_schema is original.args_schema
    assert tool is not original
    assert original.func is original_function


def test_incubator_default_returns_no_results_for_flagship_only_snapshot():
    calls = []
    result = create_fixture_project_incubator("proj-001", calls).run()
    assert result == "No projects found at Incubator level."
    assert calls == [
        {"tool": project_tools.get_incubator_projects.name, "limit": 10, "result_count": 0}
    ]
