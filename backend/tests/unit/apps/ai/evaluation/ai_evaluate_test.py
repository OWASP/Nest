import json
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError


@pytest.fixture
def runner(mocker):
    def fake_run(case_id, scenario, *, live):
        assert live is True
        return {
            "case_id": case_id,
            "scenario": scenario,
            "status": "passed" if scenario in ("relevant", "mixed") else "needs_review",
            "response": "Example answer",
        }

    return mocker.patch(
        "apps.ai.management.commands.ai_evaluate.run_rag_case",
        side_effect=fake_run,
    )


def test_command_requires_live_opt_in(runner):
    output = StringIO()

    with pytest.raises(CommandError, match="--live"):
        call_command("ai_evaluate", stdout=output)

    runner.assert_not_called()


def test_mixed_scenario_prints_a_report(runner):
    output = StringIO()

    call_command(
        "ai_evaluate",
        "--live",
        "--scenario",
        "mixed",
        stdout=output,
    )

    runner.assert_called_once_with("rag-002", "mixed", live=True)
    report = json.loads(output.getvalue())

    assert report["summary"] == {
        "total": 1,
        "passed": 1,
        "failed": 0,
        "needs_review": 0,
    }
    assert report["results"][0]["scenario"] == "mixed"


def test_relevant_scenario_prints_a_report(runner):
    output = StringIO()

    call_command("ai_evaluate", "--live", stdout=output)

    runner.assert_called_once_with("rag-002", "relevant", live=True)
    report = json.loads(output.getvalue())

    assert report["scope"] == "rag_agent"
    assert report["summary"] == {
        "total": 1,
        "passed": 1,
        "failed": 0,
        "needs_review": 0,
    }
    assert report["results"][0]["response"] == "Example answer"


@pytest.mark.parametrize("scenario", ["irrelevant", "empty"])
def test_review_required_is_not_reported_as_passing(runner, scenario):
    output = StringIO()

    with pytest.raises(CommandError, match="require review") as error:
        call_command(
            "ai_evaluate",
            "--live",
            "--scenario",
            scenario,
            stdout=output,
        )

    runner.assert_called_once_with("rag-002", scenario, live=True)
    report = json.loads(output.getvalue())

    assert error.value.returncode == 2
    assert report["summary"]["needs_review"] == 1
    assert report["summary"]["passed"] == 0


def test_failures_are_saved_and_remaining_scenarios_run(runner, tmp_path):
    runner.side_effect = [
        RuntimeError("Provider failed"),
        {
            "case_id": "rag-002",
            "scenario": "irrelevant",
            "status": "needs_review",
        },
        {
            "case_id": "rag-002",
            "scenario": "empty",
            "status": "needs_review",
        },
        {
            "case_id": "rag-002",
            "scenario": "mixed",
            "status": "passed",
        },
    ]
    destination = tmp_path / "report.json"
    destination_path = str(destination)
    output = StringIO()

    with pytest.raises(CommandError, match="failed") as error:
        call_command(
            "ai_evaluate",
            "--live",
            "--scenario",
            "all",
            "--output",
            destination_path,
            stdout=output,
        )

    report = json.loads(destination.read_text(encoding="utf-8"))

    assert error.value.returncode == 1
    assert runner.call_count == 4
    assert report == json.loads(output.getvalue())
    assert report["summary"] == {
        "total": 4,
        "passed": 1,
        "failed": 1,
        "needs_review": 2,
    }
    assert report["results"][0]["error"] == "RuntimeError: Provider failed"
    assert [result["scenario"] for result in report["results"]] == [
        "relevant",
        "irrelevant",
        "empty",
        "mixed",
    ]


@pytest.mark.parametrize(
    "arguments",
    [
        ["--case-id", "rag-001"],
        ["--scenario", "unknown"],
        ["--scope", "unknown"],
    ],
)
def test_invalid_selection_is_rejected(runner, arguments):
    output = StringIO()

    with pytest.raises(CommandError, match="invalid choice"):
        call_command("ai_evaluate", "--live", *arguments, stdout=output)

    runner.assert_not_called()


def test_invalid_output_directory_is_rejected_before_running(runner, tmp_path):
    destination = tmp_path / "missing-directory" / "report.json"
    destination_path = str(destination)
    output = StringIO()

    with pytest.raises(CommandError, match="existing directory"):
        call_command(
            "ai_evaluate",
            "--live",
            "--output",
            destination_path,
            stdout=output,
        )

    runner.assert_not_called()


def test_command_runs_selected_case(runner):
    output = StringIO()

    call_command(
        "ai_evaluate",
        "--live",
        "--case-id",
        "rag-003",
        stdout=output,
    )

    runner.assert_called_once_with(
        "rag-003",
        "relevant",
        live=True,
    )
    report = json.loads(output.getvalue())

    assert report["results"][0]["case_id"] == "rag-003"
    assert report["summary"]["passed"] == 1


@pytest.fixture
def flow_runner(mocker, runner):
    """Replace the full-flow runner independently of the direct-agent runner."""
    return mocker.patch(
        "apps.ai.management.commands.ai_evaluate.run_flow_case",
        side_effect=runner.side_effect,
    )


@pytest.mark.parametrize("scope", [None, "rag_agent", "assistant_flow"])
@pytest.mark.parametrize("case_id", ["rag-002", "rag-003"])
def test_scope_selects_exactly_one_runner(runner, flow_runner, scope, case_id):
    output = StringIO()
    arguments = ["--live", "--case-id", case_id]
    if scope is not None:
        arguments.extend(["--scope", scope])
    call_command("ai_evaluate", *arguments, stdout=output)
    selected, other = (flow_runner, runner) if scope == "assistant_flow" else (runner, flow_runner)
    selected.assert_called_once_with(case_id, "relevant", live=True)
    other.assert_not_called()
    report = json.loads(output.getvalue())
    assert report["scope"] == (scope or "rag_agent")
    assert report["results"][0]["case_id"] == case_id


@pytest.mark.parametrize("scope", ["rag_agent", "assistant_flow"])
def test_both_scopes_require_live_opt_in(runner, flow_runner, scope):
    with pytest.raises(CommandError, match="--live"):
        call_command("ai_evaluate", "--scope", scope, stdout=StringIO())
    runner.assert_not_called()
    flow_runner.assert_not_called()


def test_full_flow_rejects_bad_output_before_execution(runner, flow_runner, tmp_path):
    with pytest.raises(CommandError, match="existing directory"):
        call_command(
            "ai_evaluate",
            "--live",
            "--scope",
            "assistant_flow",
            "--output",
            str(tmp_path / "missing" / "report.json"),
            stdout=StringIO(),
        )
    runner.assert_not_called()
    flow_runner.assert_not_called()


@pytest.mark.parametrize("scope", ["rag_agent", "assistant_flow"])
def test_scope_failure_is_saved_and_remaining_scenarios_continue(
    runner, flow_runner, scope, tmp_path
):
    selected, other = (flow_runner, runner) if scope == "assistant_flow" else (runner, flow_runner)
    selected.side_effect = [
        RuntimeError("Provider failed"),
        {"status": "needs_review"},
        {"status": "needs_review"},
        {"status": "passed"},
    ]
    output = StringIO()
    destination = tmp_path / "report.json"
    with pytest.raises(CommandError) as caught:
        call_command(
            "ai_evaluate",
            "--live",
            "--scope",
            scope,
            "--scenario",
            "all",
            "--output",
            str(destination),
            stdout=output,
        )
    assert caught.value.returncode == 1
    report = json.loads(destination.read_text())
    assert report == json.loads(output.getvalue())
    assert report["scope"] == scope
    assert report["results"][0] == {
        "scope": scope,
        "case_id": "rag-002",
        "scenario": "relevant",
        "status": "failed",
        "error": "RuntimeError: Provider failed",
    }
    assert report["summary"] == {"total": 4, "passed": 1, "failed": 1, "needs_review": 2}
    assert [call.args[1] for call in selected.call_args_list] == [
        "relevant",
        "irrelevant",
        "empty",
        "mixed",
    ]
    other.assert_not_called()


@pytest.mark.parametrize("scope", ["rag_agent", "assistant_flow"])
def test_scope_review_report_is_saved_before_exit(runner, flow_runner, scope, tmp_path):
    destination = tmp_path / "review.json"
    output = StringIO()
    with pytest.raises(CommandError) as caught:
        call_command(
            "ai_evaluate",
            "--live",
            "--scope",
            scope,
            "--scenario",
            "all",
            "--output",
            str(destination),
            stdout=output,
        )
    assert caught.value.returncode == 2
    report = json.loads(destination.read_text())
    assert report == json.loads(output.getvalue())
    assert report["scope"] == scope
    assert report["summary"] == {"total": 4, "passed": 2, "failed": 0, "needs_review": 2}
    selected, other = (flow_runner, runner) if scope == "assistant_flow" else (runner, flow_runner)
    assert selected.call_count == 4
    other.assert_not_called()


def test_full_flow_diagnostics_are_preserved(runner, flow_runner, tmp_path):
    result = {
        "scope": "assistant_flow",
        "case_id": "rag-002",
        "scenario": "relevant",
        "status": "failed",
        "events": [{"stage": "route", "error": "Provider failed"}],
        "scores": [],
        "skipped": [{"evaluator": "intent", "reason": "No route"}],
        "errors": [{"stage": "route", "error": "Provider failed"}],
        "failure_reasons": ["Execution errors were recorded"],
    }
    flow_runner.side_effect = None
    flow_runner.return_value = result
    destination = tmp_path / "diagnostics.json"
    with pytest.raises(CommandError):
        call_command(
            "ai_evaluate",
            "--live",
            "--scope",
            "assistant_flow",
            "--output",
            str(destination),
            stdout=StringIO(),
        )
    assert json.loads(destination.read_text())["results"] == [result]
    runner.assert_not_called()
