import json
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError


@pytest.fixture
def runner(mocker):
    def fake_run(case_id, scenario, *, live):
        return {
            "case_id": case_id,
            "scenario": scenario,
            "status": "passed" if scenario == "relevant" else "needs_review",
            "response": "Example answer",
        }

    return mocker.patch(
        "apps.ai.management.commands.ai_evaluate.run_rag_case",
        side_effect=fake_run,
    )


def test_command_requires_live_opt_in(runner):
    with pytest.raises(CommandError, match="--live"):
        call_command("ai_evaluate", stdout=StringIO())

    runner.assert_not_called()


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
    ]
    destination = tmp_path / "report.json"
    output = StringIO()

    with pytest.raises(CommandError, match="failed") as error:
        call_command(
            "ai_evaluate",
            "--live",
            "--scenario",
            "all",
            "--output",
            str(destination),
            stdout=output,
        )

    report = json.loads(destination.read_text(encoding="utf-8"))

    assert error.value.returncode == 1
    assert runner.call_count == 3
    assert report == json.loads(output.getvalue())
    assert report["summary"] == {
        "total": 3,
        "passed": 0,
        "failed": 1,
        "needs_review": 2,
    }
    assert report["results"][0]["error"] == "RuntimeError: Provider failed"
    assert [result["scenario"] for result in report["results"]] == [
        "relevant",
        "irrelevant",
        "empty",
    ]


@pytest.mark.parametrize(
    "arguments",
    [
        ["--case-id", "rag-001"],
        ["--scenario", "unknown"],
    ],
)
def test_invalid_selection_is_rejected(runner, arguments):
    with pytest.raises(CommandError, match="invalid choice"):
        call_command("ai_evaluate", "--live", *arguments, stdout=StringIO())

    runner.assert_not_called()


def test_invalid_output_directory_is_rejected_before_running(runner, tmp_path):
    destination = tmp_path / "missing-directory" / "report.json"

    with pytest.raises(CommandError, match="existing directory"):
        call_command(
            "ai_evaluate",
            "--live",
            "--output",
            str(destination),
            stdout=StringIO(),
        )

    runner.assert_not_called()