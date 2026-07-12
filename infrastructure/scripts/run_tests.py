"""CLI for infrastructure unit and integration Terraform tests."""

from __future__ import annotations

import argparse
import logging
import sys

from scripts.errors import TestRunnerError
from scripts.runner import InfrastructureTestRunner


def main() -> None:
    """Run infrastructure unit or integration tests."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    parser = argparse.ArgumentParser(description="Infrastructure unit and integration test runner")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--unit", action="store_true", help="Run unit tests (default)")
    group.add_argument("--integration", action="store_true", help="Run integration tests")
    group.add_argument(
        "--get-tag", action="store_true", help="Print LocalStack image tag and exit"
    )
    group.add_argument(
        "--get-image",
        action="store_true",
        help="Print full LocalStack image reference (with digest) and exit",
    )
    args = parser.parse_args()

    runner = InfrastructureTestRunner()
    runner.configure_environment()

    try:
        if args.get_tag:
            runner.print_localstack_tag()
            return
        if args.get_image:
            runner.print_localstack_image()
            return
        if args.integration:
            runner.run_integration()
        else:
            runner.run_unit()
    except TestRunnerError as exc:
        sys.stderr.write(f"Error: {exc}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
