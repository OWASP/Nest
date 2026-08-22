"""Infrastructure deployment runner CLI."""

from __future__ import annotations

import argparse
import logging
import sys

from scripts.deploy_runner import InfrastructureDeployRunner
from scripts.errors import RunnerError


def main() -> None:
    """Execute the infrastructure deployment runner."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    parser = argparse.ArgumentParser(description="Infrastructure deployment runner")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Refresh an existing deployment",
    )
    args = parser.parse_args()

    runner = InfrastructureDeployRunner()
    runner.configure_environment()

    try:
        if args.refresh:
            runner.refresh()
        else:
            runner.deploy()
    except RunnerError as exc:
        sys.stderr.write(f"Error: {exc}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
