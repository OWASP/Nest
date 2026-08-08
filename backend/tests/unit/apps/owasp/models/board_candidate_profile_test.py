"""Tests for BoardCandidateProfile model."""

from apps.owasp.models.board_candidate_profile import BoardCandidateProfile
from apps.owasp.models.entity_member import EntityMember


class TestBoardCandidateProfileModel:
    """Tests for BoardCandidateProfile model."""

    def test_str_representation(self) -> None:
        """Test __str__ returns the correct representation."""
        candidate = EntityMember(member_name="Jane Doe")
        profile = BoardCandidateProfile(candidate=candidate)

        assert str(profile) == "Profile for Jane Doe"

    def test_meta_options(self) -> None:
        """Test model meta options."""
        assert BoardCandidateProfile._meta.db_table == "owasp_board_candidate_profile"
        assert BoardCandidateProfile._meta.verbose_name_plural == "Board Candidate Profiles"

    def test_has_timestamp_fields(self) -> None:
        """Test model has timestamp fields from TimestampedModel."""
        assert hasattr(BoardCandidateProfile, "nest_created_at")
        assert hasattr(BoardCandidateProfile, "nest_updated_at")

    def test_raw_markdown_default_empty(self) -> None:
        """Test raw_markdown field defaults to empty string."""
        field = BoardCandidateProfile._meta.get_field("raw_markdown")
        assert field.default == ""
        assert field.blank is True
