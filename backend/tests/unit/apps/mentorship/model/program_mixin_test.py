"""Tests for mentorship program index mixin."""

from datetime import UTC, datetime
from unittest.mock import MagicMock

from apps.mentorship.models.mixins.program import ProgramIndexMixin
from apps.mentorship.models.program import Program


class TestProgramIndexMixin:
    """Tests for ProgramIndexMixin properties."""

    def _make_program_mock(self, **overrides):
        """Create a mock program with ProgramIndexMixin behavior."""
        defaults = {
            "key": "test-program",
            "status": Program.ProgramStatus.PUBLISHED,
            "description": "A test program",
            "experience_levels": ["beginner", "intermediate"],
            "started_at": datetime(2025, 1, 1, tzinfo=UTC),
            "ended_at": datetime(2025, 12, 31, tzinfo=UTC),
        }
        defaults.update(overrides)
        mock_name = defaults.pop("name", "Test Program")
        mock = MagicMock(**defaults)
        mock.name = mock_name
        mock.__class__ = Program
        return mock

    def test_is_indexable_published(self):
        """Test is_indexable returns True for published programs."""
        mock = self._make_program_mock(status=Program.ProgramStatus.PUBLISHED)
        assert ProgramIndexMixin.is_indexable.fget(mock)

    def test_is_indexable_draft(self):
        """Test is_indexable returns False for draft programs."""
        mock = self._make_program_mock(status=Program.ProgramStatus.DRAFT)
        assert not ProgramIndexMixin.is_indexable.fget(mock)

    def test_is_indexable_completed(self):
        """Test is_indexable returns False for completed programs."""
        mock = self._make_program_mock(status=Program.ProgramStatus.COMPLETED)
        assert not ProgramIndexMixin.is_indexable.fget(mock)

    def test_idx_name(self):
        """Test idx_name returns the program name."""
        mock = self._make_program_mock(name="Security Mentorship")
        assert ProgramIndexMixin.idx_name.fget(mock) == "Security Mentorship"

    def test_idx_key(self):
        """Test idx_key returns the program key."""
        mock = self._make_program_mock(key="security-mentorship")
        assert ProgramIndexMixin.idx_key.fget(mock) == "security-mentorship"

    def test_idx_status(self):
        """Test idx_status returns the program status."""
        mock = self._make_program_mock(status=Program.ProgramStatus.PUBLISHED)
        assert ProgramIndexMixin.idx_status.fget(mock) == "published"

    def test_idx_description(self):
        """Test idx_description returns the description."""
        mock = self._make_program_mock(description="My description")
        assert ProgramIndexMixin.idx_description.fget(mock) == "My description"

    def test_idx_description_none(self):
        """Test idx_description returns empty string when None."""
        mock = self._make_program_mock(description=None)
        assert ProgramIndexMixin.idx_description.fget(mock) == ""

    def test_idx_experience_levels(self):
        """Test idx_experience_levels returns the list."""
        mock = self._make_program_mock(experience_levels=["beginner", "advanced"])
        assert ProgramIndexMixin.idx_experience_levels.fget(mock) == ["beginner", "advanced"]

    def test_idx_experience_levels_none(self):
        """Test idx_experience_levels returns empty list when None."""
        mock = self._make_program_mock(experience_levels=None)
        assert ProgramIndexMixin.idx_experience_levels.fget(mock) == []

    def test_idx_started_at(self):
        """Test idx_started_at returns ISO formatted start datetime."""
        started = datetime(2025, 1, 1, 9, 0, 0, tzinfo=UTC)
        mock = self._make_program_mock(started_at=started)
        assert ProgramIndexMixin.idx_started_at.fget(mock) == started.isoformat()

    def test_idx_started_at_none(self):
        """Test idx_started_at returns None when started_at is None."""
        mock = self._make_program_mock(started_at=None)
        assert ProgramIndexMixin.idx_started_at.fget(mock) is None

    def test_idx_ended_at(self):
        """Test idx_ended_at returns ISO formatted end datetime."""
        ended = datetime(2025, 12, 31, 18, 0, 0, tzinfo=UTC)
        mock = self._make_program_mock(ended_at=ended)
        assert ProgramIndexMixin.idx_ended_at.fget(mock) == ended.isoformat()

    def test_idx_ended_at_none(self):
        """Test idx_ended_at returns None when ended_at is None."""
        mock = self._make_program_mock(ended_at=None)
        assert ProgramIndexMixin.idx_ended_at.fget(mock) is None
