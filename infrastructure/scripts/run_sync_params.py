"""SSM parameter sync runner CLI."""

from __future__ import annotations

import argparse
import logging
import sys

from scripts.errors import RunnerError
from scripts.sync_params_runner import InfrastructureParameterSyncRunner


def main() -> None:
    """Execute the SSM parameter sync runner."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    parser = argparse.ArgumentParser(description="SSM parameter sync runner")
    parser.add_argument(
        "--configuration",
        default="Production",
        help="Django configuration to set (default: Production)",
    )
    parser.add_argument(
        "--settings-module",
        default="settings.production",
        help="Django settings module to set (default: settings.production)",
    )
    args = parser.parse_args()

    try:
        InfrastructureParameterSyncRunner().sync(
            configuration=args.configuration,
            settings_module=args.settings_module,
        )
    except RunnerError as exc:
        sys.stderr.write(f"Error: {exc}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
