from unittest.mock import MagicMock

from apps.mentorship.api.internal.nodes.program import ProgramNode
from apps.mentorship.models.program import Program


def test_program_admins_ordering():
    mock_program = MagicMock(spec=Program)
    mock_admins_manager = MagicMock()
    mock_queryset = MagicMock()
    mock_program.admins = mock_admins_manager
    mock_admins_manager.order_by.return_value = mock_queryset
    field = next(f for f in ProgramNode.__strawberry_definition__.fields if f.name == "admins")
    result = field.base_resolver.wrapped_func(mock_program)
    mock_admins_manager.order_by.assert_called_once_with("github_user__login")
    assert result == mock_queryset
