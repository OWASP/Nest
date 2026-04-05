#!/usr/bin/env python3
"""Generate terraform-docs output for all Terraform directories in infrastructure."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
INFRA_ROOT = REPO_ROOT / "infrastructure"
CONFIG_PATH = INFRA_ROOT / ".terraform-docs.yml"


def terraform_directories() -> list[Path]:
    project_dirs = [
        INFRA_ROOT / "bootstrap",
        INFRA_ROOT / "live",
        INFRA_ROOT / "state",
    ]
    module_dirs = {
        path.parent
        for path in (INFRA_ROOT / "modules").rglob("*.tf")
        if ".terraform" not in path.parts
    }
    return project_dirs + sorted(module_dirs)


def main() -> int:
    terraform_docs = shutil.which("terraform-docs")
    if terraform_docs is None:
        print("terraform-docs is required but was not found on PATH.", file=sys.stderr)
        return 1

    for directory in terraform_directories():
        print(f"Generating terraform-docs for {directory.relative_to(REPO_ROOT)}...")
        result = subprocess.run(
            [terraform_docs, "--config", str(CONFIG_PATH), str(directory)],
            cwd=REPO_ROOT,
            check=False,
        )
        if result.returncode != 0:
            return result.returncode

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
