from unittest.mock import MagicMock

import pytest

from apps.github.management.commands.github_enrich_issues import Command


@pytest.mark.parametrize(
    ("argument_name", "expected_properties"),
    [
        ("--offset", {"default": 0, "required": False, "type": int}),
        ("--force-update-hint", {"default": False, "required": False, "action": "store_true"}),
        ("--force-update-summary", {"default": False, "required": False, "action": "store_true"}),
        ("--update-hint", {"default": True, "required": False, "action": "store_true"}),
        ("--update-summary", {"default": True, "required": False, "action": "store_true"}),
    ],
)
def test_add_arguments(argument_name, expected_properties):
    mock_parser = MagicMock()

    command = Command()
    command.add_arguments(mock_parser)

    mock_parser.add_argument.assert_any_call(argument_name, **expected_properties)
