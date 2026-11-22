"""Backend ECS task runner CLI."""

from __future__ import annotations

import argparse
import logging
import sys

from scripts.backend_tasks_runner import BACKEND_TASKS, BackendTaskRunner
from scripts.errors import RunnerError


def main() -> None:
    """Execute the backend task runner."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    parser = argparse.ArgumentParser(description="Backend ECS task runner")
    parser.add_argument(
        "task",
        choices=BACKEND_TASKS,
        help="backend task to run",
    )
    args = parser.parse_args()

    try:
        BackendTaskRunner(args.task).run()
    except RunnerError as exc:
        sys.stderr.write(f"Error: {exc}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
