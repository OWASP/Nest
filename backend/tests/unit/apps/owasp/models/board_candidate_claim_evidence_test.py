"""Tests for BoardCandidateClaimEvidence model."""

from unittest.mock import MagicMock, Mock, PropertyMock, patch

import pytest
from django.core.exceptions import ValidationError

from apps.owasp.models.board_candidate_claim_evidence import BoardCandidateClaimEvidence


class TestBoardCandidateClaimEvidenceModel:
    """Tests for BoardCandidateClaimEvidence model."""

    def test_str_representation(self):
        """Test __str__ returns the evidence title."""
        evidence = BoardCandidateClaimEvidence(title="Test Evidence Title")

        assert str(evidence) == "Test Evidence Title"

    def test_meta_options(self):
        """Test model meta options."""
        assert BoardCandidateClaimEvidence._meta.db_table == "owasp_board_candidate_claim_evidence"
        assert (
            BoardCandidateClaimEvidence._meta.verbose_name_plural
            == "Board Candidate Claim Evidences"
        )

    def test_meta_indexes(self):
        """Test model indexes are defined."""
        index_names = {index.name for index in BoardCandidateClaimEvidence._meta.indexes}

        assert "owasp_evidence_claim_active" in index_names

    def test_has_timestamp_fields(self):
        """Test model has timestamp fields from TimestampedModel."""
        assert hasattr(BoardCandidateClaimEvidence, "nest_created_at")
        assert hasattr(BoardCandidateClaimEvidence, "nest_updated_at")

    def test_description_default_empty(self):
        """Test description field defaults to empty string."""
        field = BoardCandidateClaimEvidence._meta.get_field("description")

        assert field.default == ""

    def test_file_field_nullable(self):
        """Test file field is nullable."""
        field = BoardCandidateClaimEvidence._meta.get_field("file")

        assert field.null
        assert field.blank

    def test_file_name_field_blank(self):
        """Test file_name field allows blank."""
        field = BoardCandidateClaimEvidence._meta.get_field("file_name")

        assert field.blank
        assert field.max_length == 1000

    def test_file_size_field_nullable(self):
        """Test file_size field is nullable."""
        field = BoardCandidateClaimEvidence._meta.get_field("file_size")

        assert field.null
        assert field.blank

    def test_is_removed_default_false(self):
        """Test is_removed field defaults to False."""
        field = BoardCandidateClaimEvidence._meta.get_field("is_removed")

        assert field.default is False

    def test_removed_at_field_nullable(self):
        """Test removed_at field is nullable."""
        field = BoardCandidateClaimEvidence._meta.get_field("removed_at")

        assert field.null
        assert field.blank

    def test_removed_reason_field_blank(self):
        """Test removed_reason field allows blank."""
        field = BoardCandidateClaimEvidence._meta.get_field("removed_reason")

        assert field.blank

    def test_title_max_length(self):
        """Test title field max_length."""
        field = BoardCandidateClaimEvidence._meta.get_field("title")

        assert field.max_length == 1000

    def test_source_url_field_blank(self):
        """Test source_url field allows blank."""
        field = BoardCandidateClaimEvidence._meta.get_field("source_url")

        assert field.blank

    def test_clean_locked_claim_raises_validation_error(self):
        """Test that clean raises ValidationError when claim is locked."""
        mock_claim = Mock()
        mock_claim.is_locked = True

        evidence = BoardCandidateClaimEvidence(
            title="Test Evidence", source_url="https://example.com"
        )
        evidence.claim_id = 1

        with (
            patch.object(
                type(evidence), "claim", new_callable=PropertyMock, return_value=mock_claim
            ),
            pytest.raises(
                ValidationError, match=r"Cannot add or modify evidence on a locked claim."
            ),
        ):
            evidence.clean()

    def test_clean_unlocked_claim_with_source_url_passes(self):
        """Test that clean passes for unlocked claim with source_url."""
        mock_claim = Mock()
        mock_claim.is_locked = False

        evidence = BoardCandidateClaimEvidence(
            title="Test Evidence", source_url="https://example.com"
        )
        evidence.claim_id = 1

        with patch.object(
            type(evidence), "claim", new_callable=PropertyMock, return_value=mock_claim
        ):
            evidence.clean()

    def test_clean_no_file_and_no_source_url_raises_validation_error(self):
        """Test that clean raises ValidationError when neither file nor source_url."""
        mock_claim = Mock()
        mock_claim.is_locked = False

        evidence = BoardCandidateClaimEvidence(title="Test Evidence", source_url="")
        evidence.claim_id = 1
        evidence.file = None

        with (
            patch.object(
                type(evidence), "claim", new_callable=PropertyMock, return_value=mock_claim
            ),
            pytest.raises(ValidationError, match=r"Either file or source_url is required."),
        ):
            evidence.clean()

    def test_clean_with_file_sets_file_name(self):
        """Test that clean auto-sets file_name from file when not provided."""
        mock_claim = Mock()
        mock_claim.is_locked = False

        mock_file = MagicMock()
        mock_file.name = "document.pdf"
        mock_file.size = 12345
        mock_file.__bool__ = Mock(return_value=True)

        evidence = BoardCandidateClaimEvidence(title="Test Evidence")
        evidence.claim_id = 1
        evidence.file = mock_file
        evidence.file_name = ""
        evidence.file_size = None

        with patch.object(
            type(evidence), "claim", new_callable=PropertyMock, return_value=mock_claim
        ):
            evidence.clean()

        assert evidence.file_name == "document.pdf"
        assert evidence.file_size == 12345

    def test_clean_with_file_preserves_existing_file_name(self):
        """Test that clean preserves existing file_name when already set."""
        mock_claim = Mock()
        mock_claim.is_locked = False

        mock_file = MagicMock()
        mock_file.name = "document.pdf"
        mock_file.size = 12345
        mock_file.__bool__ = Mock(return_value=True)

        evidence = BoardCandidateClaimEvidence(title="Test Evidence")
        evidence.claim_id = 1
        evidence.file = mock_file
        evidence.file_name = "custom_name.pdf"
        evidence.file_size = 99999

        with patch.object(
            type(evidence), "claim", new_callable=PropertyMock, return_value=mock_claim
        ):
            evidence.clean()

        assert evidence.file_name == "custom_name.pdf"
        assert evidence.file_size == 99999

    def test_clean_without_claim_id_skips_locked_check(self):
        """Test that clean skips locked check when claim_id is not set."""
        evidence = BoardCandidateClaimEvidence(
            title="Test Evidence", source_url="https://example.com"
        )
        evidence.claim_id = None

        evidence.clean()

    @patch.object(BoardCandidateClaimEvidence, "full_clean")
    @patch("apps.owasp.models.board_candidate_claim_evidence.TimestampedModel.save")
    def test_save_calls_full_clean(self, mock_super_save, mock_full_clean):
        """Test that save calls full_clean before saving."""
        evidence = BoardCandidateClaimEvidence(title="Test Evidence")

        evidence.save()

        mock_full_clean.assert_called_once()
        mock_super_save.assert_called_once()
