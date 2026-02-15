from unittest.mock import MagicMock, patch

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


def test_program_recent_milestones():
    """Test the recent_milestones resolver."""
    mock_program = MagicMock(spec=Program)
    mock_modules_manager = MagicMock()
    mock_program.modules = mock_modules_manager
    mock_modules_manager.values_list.return_value = [1, 2]

    with patch("apps.mentorship.api.internal.nodes.program.Milestone") as mock_milestone:
        mock_chain = MagicMock()
        mock_milestone.open_milestones.filter.return_value = mock_chain
        mock_chain.select_related.return_value = mock_chain
        mock_chain.prefetch_related.return_value = mock_chain
        mock_chain.order_by.return_value = mock_chain
        mock_chain.distinct.return_value = mock_chain

        field = next(
            f
            for f in ProgramNode.__strawberry_definition__.fields
            if f.name == "recent_milestones"
        )
        result = field.base_resolver.wrapped_func(mock_program)

        mock_modules_manager.values_list.assert_called_once_with("project_id", flat=True)
        mock_milestone.open_milestones.filter.assert_called_once_with(
            repository__project__in=[1, 2]
        )
        assert result == mock_chain
