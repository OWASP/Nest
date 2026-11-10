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
    def test_date_replica_rankings(self):
        """Test date replicas map ascending and descending rules to the right fields."""
        with patch(
            "apps.mentorship.index.registry.program.IndexBase.configure_replicas"
        ) as mock_configure_replicas:
            ProgramIndex.configure_replicas()

        index_name, replicas = mock_configure_replicas.call_args.args
        assert index_name == "programs"
        assert replicas["created_at_asc"] == ["asc(idx_created_at)"]
        assert replicas["created_at_desc"] == ["desc(idx_created_at)"]
        assert replicas["updated_at_asc"] == ["asc(idx_updated_at)"]
        assert replicas["updated_at_desc"] == ["desc(idx_updated_at)"]

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
