import shlex
from pathlib import Path

import yaml


def test_release_image_scan_is_a_required_standalone_step():
    workflow = Path(__file__).resolve().parents[3] / ".github/workflows/run-image-scan.yaml"
    job = yaml.safe_load(workflow.read_text(encoding="utf-8"))["jobs"]["run-image-scan"]
    (scan,) = (
        step for step in job["steps"] if step.get("uses") == "./.github/actions/run-trivy-check"
    )
    assert not job.get("continue-on-error")
    assert not scan.get("continue-on-error")
    # A later command in the same shell can overwrite the scan's exit status.
    command = shlex.split(scan["with"]["command"].replace("\\\n", ""))
    assert command[:2] == ["make", "security-image-scan"]
    assert sorted(command[2:]) == [
        "BACKEND_IMAGE_NAME=$BACKEND_IMAGE",
        "FRONTEND_IMAGE_NAME=$FRONTEND_IMAGE",
    ]
