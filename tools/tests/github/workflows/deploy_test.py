"""Regression tests for the staging deployment routing decision."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPOSITORY_ROOT = Path(__file__).resolve().parents[4]


def run_release(script, env, *, check):
    """Execute repository-owned workflow code with stubbed Terraform."""
    return subprocess.run(  # noqa: S603 - Trusted local workflow, isolated test environment.
        ["/bin/bash", "-eo", "pipefail", "-c", script], env=env, check=check
    )


@pytest.fixture
def release_step():
    """Read the real workflow shell block rather than copying its behavior."""
    workflow = yaml.safe_load((REPOSITORY_ROOT / ".github/workflows/run-deploy.yaml").read_text())
    return next(
        step["run"]
        for step in workflow["jobs"]["run-deploy"]["steps"]
        if step["name"] == "Deploy staging release"
    )


@pytest.fixture
def terraform_stub(tmp_path):
    """Capture Terraform operations without any AWS or Terraform installation."""
    executable = tmp_path / "terraform"
    executable.write_text(
        f"#!{sys.executable}\n"
        "import json, os, sys\n"
        "with open(os.environ['TEST_CALLS'], 'a') as log:\n"
        "    log.write(json.dumps(sys.argv[1:]) + '\\n')\n"
        "if sys.argv[1] == 'output':\n"
        "    print(os.environ['TEST_OUTPUT'])\n"
        "elif sys.argv[1] == 'plan' and os.environ.get('TEST_FAIL_PLAN'):\n"
        "    sys.exit(1)\n"
        "elif sys.argv[1] == 'show':\n"
        "    print('Test release plan')\n"
    )
    executable.chmod(0o755)
    return {
        "PATH": f"{tmp_path}{os.pathsep}/usr/bin{os.pathsep}/bin",
        "TEST_CALLS": str(tmp_path / "calls.jsonl"),
        "GITHUB_STEP_SUMMARY": str(tmp_path / "summary.md"),
    }


@pytest.mark.parametrize(
    ("current", "desired", "expected"),
    [(True, False, False), (False, False, False), (False, True, False), (True, True, True)],
)
def test_release_routing_before_health_checks(
    release_step, terraform_stub, current, desired, expected
):
    """Disable routing immediately, but preserve the old route before enabling."""
    env = terraform_stub | {
        "TEST_OUTPUT": json.dumps({"route_slack_to_nestbot": {"value": current}}),
        "TF_VAR_route_slack_to_nestbot": str(desired).lower(),
    }
    run_release(release_step, env, check=True)
    calls = [json.loads(line) for line in Path(env["TEST_CALLS"]).read_text().splitlines()]
    plan = next(call for call in calls if call[0] == "plan")
    assert f"-var=route_slack_to_nestbot={str(expected).lower()}" in plan
    assert calls[-1] == ["apply", "-auto-approve", "tfplan"]


@pytest.mark.parametrize("output", ["{}", '{"route_slack_to_nestbot":{"value":"invalid"}}'])
def test_release_rejects_unknown_current_route(release_step, terraform_stub, output):
    """Never apply changes when the previous route cannot be established."""
    env = terraform_stub | {"TEST_OUTPUT": output, "TF_VAR_route_slack_to_nestbot": "true"}
    result = run_release(release_step, env, check=False)
    assert result.returncode != 0
    calls = [json.loads(line) for line in Path(env["TEST_CALLS"]).read_text().splitlines()]
    assert not any(call[0] in {"plan", "apply"} for call in calls)


def test_release_does_not_apply_failed_plan(release_step, terraform_stub):
    """A rollback request still must not apply an invalid release plan."""
    env = terraform_stub | {
        "TEST_OUTPUT": '{"route_slack_to_nestbot":{"value":true}}',
        "TF_VAR_route_slack_to_nestbot": "false",
        "TEST_FAIL_PLAN": "1",
    }
    result = run_release(release_step, env, check=False)
    assert result.returncode != 0
    calls = [json.loads(line) for line in Path(env["TEST_CALLS"]).read_text().splitlines()]
    assert not any(call[0] == "apply" for call in calls)
