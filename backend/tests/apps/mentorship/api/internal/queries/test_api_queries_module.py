"""Pytest for mentorship module queries."""

from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ObjectDoesNotExist

from apps.mentorship.api.internal.queries.module import ModuleQuery
from apps.mentorship.models import Module


@pytest.fixture
def api_module_queries() -> ModuleQuery:
    """Pytest fixture to return an instance of the query resolver class."""
    return ModuleQuery()


class TestModuleQuery:
    """Tests for ModuleQuery."""

    @patch("apps.mentorship.api.internal.queries.module.Module.objects.filter")
    def test_get_program_modules_success(
        self, mock_module_filter: MagicMock, api_module_queries
    ) -> None:
        """Test successful retrieval of modules by program key."""
        mock_module = MagicMock(spec=Module)
        mock_module_filter_related = mock_module_filter.return_value.select_related.return_value
        mock_module_filter_related.prefetch_related.return_value.order_by.return_value = [
            mock_module
        ]
        result = api_module_queries.get_program_modules(program_key="program1")

        assert result == [mock_module]
        mock_module_filter.assert_called_once_with(program__key="program1")

    @patch("apps.mentorship.api.internal.queries.module.Module.objects.filter")
    def test_get_program_modules_empty(
        self, mock_module_filter: MagicMock, api_module_queries
    ) -> None:
        """Test retrieval of modules by program key returns empty list if no modules found."""
        mock_module_filter_related = mock_module_filter.return_value.select_related.return_value
        mock_module_filter_related.prefetch_related.return_value.order_by.return_value = []

        result = api_module_queries.get_program_modules(program_key="nonexistent_program")

        assert result == []
        mock_module_filter.assert_called_once_with(program__key="nonexistent_program")

    @patch("apps.mentorship.api.internal.queries.module.Module.objects.filter")
    def test_get_project_modules_success(
        self, mock_module_filter: MagicMock, api_module_queries
    ) -> None:
        """Test successful retrieval of modules by project key."""
        mock_module = MagicMock(spec=Module)
        mock_module_filter_related = mock_module_filter.return_value.select_related.return_value
        mock_module_filter_related.prefetch_related.return_value.order_by.return_value = [
            mock_module
        ]

        result = api_module_queries.get_project_modules(project_key="project1")

        assert result == [mock_module]
        mock_module_filter.assert_called_once_with(project__key="project1")

    @patch("apps.mentorship.api.internal.queries.module.Module.objects.filter")
    def test_get_project_modules_empty(
        self, mock_module_filter: MagicMock, api_module_queries
    ) -> None:
        """Test retrieval of modules by project key returns empty list if no modules found."""
        mock_module_filter_related = mock_module_filter.return_value.select_related.return_value
        mock_module_filter_related.prefetch_related.return_value.order_by.return_value = []

        result = api_module_queries.get_project_modules(project_key="nonexistent_project")

        assert result == []
        mock_module_filter.assert_called_once_with(project__key="nonexistent_project")

    @patch("apps.mentorship.api.internal.queries.module.Module.objects.select_related")
    def test_get_module_success(
        self, mock_module_select_related: MagicMock, api_module_queries
    ) -> None:
        """Test successful retrieval of a single module."""
        mock_module = MagicMock(spec=Module)
        mock_module_select_related.return_value.prefetch_related.return_value.get.return_value = (
            mock_module
        )

        result = api_module_queries.get_module(module_key="module1", program_key="program1")

        assert result == mock_module
        mock_module_select_related.assert_called_once_with("program", "project")
        mock_module_select_related.return_value.prefetch_related.return_value.get.assert_called_once_with(
            key="module1", program__key="program1"
        )

    @patch("apps.mentorship.api.internal.queries.module.Module.objects.select_related")
    def test_get_module_does_not_exist(
        self, mock_module_select_related: MagicMock, api_module_queries
    ) -> None:
        """Test when the module does not exist."""
        mock_module_select_related.return_value.prefetch_related.return_value.get.side_effect = (
            Module.DoesNotExist
        )

        with pytest.raises(
            ObjectDoesNotExist,
            match=r"Module with key 'nonexistent' under program 'program1' not found\.",
        ):
            api_module_queries.get_module(module_key="nonexistent", program_key="program1")

        mock_module_select_related.assert_called_once_with("program", "project")
        mock_module_select_related.return_value.prefetch_related.return_value.get.assert_called_once_with(
            key="nonexistent", program__key="program1"
        )
