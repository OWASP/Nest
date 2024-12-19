import pytest
from unittest.mock import MagicMock
from apps.github.management.commands.github_update_owasp_organization import Command

@pytest.mark.parametrize(
    "argument_name, expected_properties",
    [
        ("--offset", {"default": 0, "required": False, "type": int}),
        (
            "--repository",
            {
                "required": False,
                "type": str,
                "help": "The OWASP organization's repository name (e.g. Nest, www-project-nest')",
            },
        ),
    ],
)
def test_add_arguments(argument_name, expected_properties):
    mock_parser = MagicMock()
    command = Command()
    command.add_arguments(mock_parser)
    mock_parser.add_argument.assert_any_call(argument_name, **expected_properties)
