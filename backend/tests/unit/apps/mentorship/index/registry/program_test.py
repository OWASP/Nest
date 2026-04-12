"""Tests for mentorship program index."""

from unittest.mock import MagicMock, patch

import pytest

from apps.mentorship.index.registry.program import ProgramIndex
from apps.mentorship.models.program import Program


@pytest.fixture
def program_index(mocker):
    """Return an instance of the ProgramIndex."""
    mocker.patch("apps.common.index.IndexBase.__init__", return_value=None)
    return ProgramIndex()


class TestProgramIndex:
    def test_class_attributes(self):
        """Test that the basic class attributes are set correctly."""
        assert ProgramIndex.index_name == "programs"
        assert ProgramIndex.should_index == "is_indexable"
        assert isinstance(ProgramIndex.fields, tuple)
        assert len(ProgramIndex.fields) > 0
        assert isinstance(ProgramIndex.settings, dict)

    def test_get_entities(self, program_index):
        """Test that get_entities returns only published programs."""
        mock_filter_manager = MagicMock()
        mock_filter_manager.filter.return_value = "final_queryset"

        with patch.object(Program, "objects", mock_filter_manager):
            queryset = program_index.get_entities()

            mock_filter_manager.filter.assert_called_once_with(
                status=Program.ProgramStatus.PUBLISHED,
            )
            assert queryset == "final_queryset"
