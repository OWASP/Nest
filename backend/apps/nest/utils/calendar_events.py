"""Nest Calendar Events utilities."""

import shlex
from argparse import ArgumentParser


def parse_reminder_args(text: str):
    """Parse reminder command arguments.

    Args:
        text (str): The text containing the reminder command arguments.

    Returns:
        Namespace: The parsed arguments as a Namespace object.

    """
    parser = ArgumentParser(prog="/set-reminder", description="Set a reminder for a Slack event.")
    parser.add_argument(
        "--channel", type=str, help="The channel to send the reminder to.", required=True
    )
    parser.add_argument(
        "--event_number", type=int, help="The event number to set the reminder for.", required=True
    )
    parser.add_argument(
        "--minutes_before",
        type=int,
        help="Minutes before the event to send the reminder.",
        default=10,
    )
    parser.add_argument(
        "--message",
        type=str,
        nargs="*",
        default=[],
        help="Optional message to include in the reminder.",
    )
    parser.add_argument(
        "--recurrence",
        type=str,
        choices=["once", "daily", "weekly", "monthly"],
        default="once",
        help="Optional recurrence pattern for the reminder.",
    )

    return parser.parse_args(shlex.split(text or ""))
