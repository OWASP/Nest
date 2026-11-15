"""Controlled project-tool execution for evaluation."""

from crewai import Agent
from crewai.tools import BaseTool

from apps.ai.agents.project import create_project_agent
from apps.ai.agents.project.tools.formatters import format_project_results
from apps.ai.agents.project.tools.get_flagship_projects import (
    MAX_FLAGSHIP_PROJECTS,
    get_flagship_projects,
)
from apps.ai.agents.project.tools.get_incubator_projects import get_incubator_projects
from apps.ai.agents.project.tools.search import search_projects
from apps.ai.evaluation.datasets.project_fixtures import get_project_fixture


def create_fixture_project_search(
    case_id: str,
    tool_calls: list[dict],
) -> BaseTool:
    """Create project search backed by fixed records."""
    projects = get_project_fixture(case_id)

    def search(query: str, limit: int = 5) -> str:
        if limit < 0:
            msg = "Search limit must be non-negative"
            raise ValueError(msg)

        results = projects[:limit]
        tool_calls.append(
            {
                "tool": search_projects.name,
                "query": query,
                "limit": limit,
                "result_count": len(results),
            }
        )
        return format_project_results(results)

    return search_projects.model_copy(update={"func": search, "current_usage_count": 0})


def create_unavailable_project_tool(
    tool: BaseTool,
    tool_calls: list[dict],
) -> BaseTool:
    """Record and reject calls without controlled fixture data."""

    def unavailable(*_args, **_kwargs) -> str:
        msg = f"No controlled fixture for tool '{tool.name}'"
        tool_calls.append({"tool": tool.name, "error": msg})

        raise ValueError(msg)

    return tool.model_copy(update={"func": unavailable, "current_usage_count": 0})


def create_fixture_project_flagship(
    case_id: str,
    tool_calls: list[dict],
) -> BaseTool:
    """Create flagship lookup backed by fixed project records."""
    projects = get_project_fixture(case_id)

    def flagship(limit: int = 15) -> str:
        safe_limit = max(0, min(limit, MAX_FLAGSHIP_PROJECTS))
        results = [
            project
            for project in projects
            if str(project.get("idx_level", "")).lower() == "flagship"
        ][:safe_limit]

        tool_calls.append(
            {
                "tool": get_flagship_projects.name,
                "limit": limit,
                "result_count": len(results),
            }
        )
        return format_project_results(results, "Flagship")

    return get_flagship_projects.model_copy(update={"func": flagship, "current_usage_count": 0})


def create_fixture_project_agent(
    case_id: str,
    tool_calls: list[dict],
) -> Agent:
    """Create a project agent with controlled tool implementations."""
    controlled_tools = {
        search_projects.name: create_fixture_project_search(case_id, tool_calls),
        get_flagship_projects.name: create_fixture_project_flagship(case_id, tool_calls),
    }
    agent = create_project_agent()

    agent.tools = [
        controlled_tools[tool.name]
        if tool.name in controlled_tools
        else create_unavailable_project_tool(tool, tool_calls)
        for tool in agent.tools
    ]
    agent.cache = False
    return agent


def create_fixture_project_incubator(
    case_id: str,
    tool_calls: list[dict],
) -> BaseTool:
    """Create incubator lookup backed by fixed project records."""
    projects = get_project_fixture(case_id)

    def incubator(limit: int = 10) -> str:
        results = [
            project
            for project in projects
            if str(project.get("idx_level", "")).lower() == "incubator"
        ][:limit]

        tool_calls.append(
            {
                "tool": get_incubator_projects.name,
                "limit": limit,
                "result_count": len(results),
            }
        )
        return format_project_results(results, "Incubator")

    return get_incubator_projects.model_copy(update={"func": incubator, "current_usage_count": 0})
