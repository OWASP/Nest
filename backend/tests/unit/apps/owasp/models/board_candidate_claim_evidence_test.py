"""Tests for BoardCandidateClaimEvidence model."""

from contextlib import contextmanager
from unittest.mock import MagicMock, Mock, patch

import pytest
from django.core.exceptions import ValidationError

from apps.owasp.models.board_candidate_claim import BoardCandidateClaim
from apps.owasp.models.board_candidate_claim_evidence import (
    BoardCandidateClaimEvidence,
    uuid_upload_to,
)


@contextmanager
def _mock_evidence_full_clean(*, claim_filter_exists=True):
    """Mock claim objects filter and FK validate to avoid DB access during full_clean."""
    with patch(
        "apps.owasp.models.board_candidate_claim_evidence.BoardCandidateClaim.objects"
    ) as mock_objects:
        mock_objects.filter.return_value.exists.return_value = claim_filter_exists
        with patch.object(BoardCandidateClaimEvidence._meta.get_field("claim"), "validate"):
            yield


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

    def test_file_field_has_validators(self):
        """Test file field has extension and size validators."""
        field = BoardCandidateClaimEvidence._meta.get_field("file")

        assert len(field.validators) == 2

    def test_uuid_upload_to_uses_correct_prefix(self):
        result = uuid_upload_to(None, "file.pdf")

        assert result.startswith("bod/claim/evidence/")

    def test_uuid_upload_to_preserves_extension(self):
        result = uuid_upload_to(None, "file.pdf")

        assert result.endswith(".pdf")

    @pytest.mark.parametrize(
        ("filename", "expected_ext"),
        [
            ("doc.docx", ".docx"),
            ("image.png", ".png"),
            ("photo.jpeg", ".jpeg"),
            ("photo.jpg", ".jpg"),
            ("data.xlsx", ".xlsx"),
            ("data.xls", ".xls"),
            ("webpage", ""),
            ("archive.tar.gz", ".gz"),
        ],
    )
    def test_uuid_upload_to_various_extensions(self, filename, expected_ext):
        result = uuid_upload_to(None, filename)

        assert result.endswith(expected_ext)

    def test_uuid_upload_to_generates_unique_paths(self):
        results = {uuid_upload_to(None, "file.pdf") for _ in range(100)}

        assert len(results) == 100

    def test_uuid_upload_to_contains_uuid(self):
        result = uuid_upload_to(None, "file.pdf")
        parts = result.removeprefix("bod/claim/evidence/").removesuffix(".pdf")

        assert len(parts) in (32, 36)

    def _evidence_with_file(self, **mock_kwargs):
        """Build evidence with a mock file, ready for full_clean."""
        evidence = BoardCandidateClaimEvidence(
            title="Test Evidence", description="Test description."
        )
        evidence.claim_id = 1
        mock_file = MagicMock()
        mock_file.name = "document.pdf"
        mock_file.content_type = "application/pdf"
        mock_file.size = 1000
        for key, value in mock_kwargs.items():
            setattr(mock_file, key, value)
        evidence.file = mock_file
        return evidence

    def test_full_clean_passes_with_valid_file(self):
        """Test that full_clean passes for a valid file."""
        evidence = self._evidence_with_file()

        with _mock_evidence_full_clean():
            evidence.full_clean()

    @pytest.mark.parametrize("name", ["evidence.pdf", "evidence.png", "evidence.docx"])
    def test_full_clean_allowed_extension_passes(self, name):
        """Test that full_clean passes for representative allowed extensions."""
        evidence = self._evidence_with_file(name=name)

        with _mock_evidence_full_clean():
            evidence.full_clean()

    @pytest.mark.parametrize("name", ["evidence.exe", "evidence.gif", "evidence"])
    def test_full_clean_disallowed_extension_raises_error(self, name):
        """Test that full_clean rejects disallowed extensions."""
        evidence = self._evidence_with_file(name=name)

        with _mock_evidence_full_clean(), pytest.raises(ValidationError):
            evidence.full_clean()

    def test_full_clean_file_within_size_limit_passes(self):
        """Test that full_clean passes for a file at the size limit."""
        evidence = self._evidence_with_file(size=10 * 1024 * 1024)

        with _mock_evidence_full_clean():
            evidence.full_clean()

    def test_full_clean_file_exceeds_size_limit_raises_error(self):
        """Test that full_clean rejects a file exceeding the maximum size."""
        evidence = self._evidence_with_file(size=999999999)

        with _mock_evidence_full_clean(), pytest.raises(ValidationError):
            evidence.full_clean()

    @pytest.mark.parametrize(
        "status",
        [
            BoardCandidateClaim.Status.APPROVED,
            BoardCandidateClaim.Status.DISCARDED,
            BoardCandidateClaim.Status.REJECTED,
            BoardCandidateClaim.Status.SUBMITTED,
            BoardCandidateClaim.Status.WITHDRAWN,
        ],
    )
    def test_clean_non_draft_statuses_raise_validation_error(self, status):
        """Test that clean raises ValidationError for all non-draft statuses."""
        evidence = BoardCandidateClaimEvidence(
            title="Test Evidence", source_url="https://example.com"
        )
        evidence.claim_id = 1

        with patch(
            "apps.owasp.models.board_candidate_claim_evidence.BoardCandidateClaim.objects"
        ) as mock_objects:
            mock_objects.filter.return_value.exists.return_value = False

            with pytest.raises(
                ValidationError, match=r"Cannot add or modify evidence on a non-draft claim."
            ):
                evidence.clean()

            assert status != BoardCandidateClaim.Status.DRAFT
            mock_objects.filter.assert_called_with(
                pk=1,
                status=BoardCandidateClaim.Status.DRAFT,
            )

    def test_clean_draft_status_passes(self):
        """Test that clean passes for draft status."""
        evidence = BoardCandidateClaimEvidence(
            title="Test Evidence", source_url="https://example.com"
        )
        evidence.claim_id = 1

        with patch(
            "apps.owasp.models.board_candidate_claim_evidence.BoardCandidateClaim.objects"
        ) as mock_objects:
            mock_objects.filter.return_value.exists.return_value = True

            evidence.clean()

            mock_objects.filter.assert_called_with(
                pk=1,
                status=BoardCandidateClaim.Status.DRAFT,
            )

    def test_clean_non_draft_claim_raises_validation_error(self):
        """Test that clean raises ValidationError when claim is non-draft."""
        evidence = BoardCandidateClaimEvidence(
            title="Test Evidence", source_url="https://example.com"
        )
        evidence.claim_id = 1

        with patch(
            "apps.owasp.models.board_candidate_claim_evidence.BoardCandidateClaim.objects"
        ) as mock_objects:
            mock_objects.filter.return_value.exists.return_value = False

            with pytest.raises(
                ValidationError, match=r"Cannot add or modify evidence on a non-draft claim."
            ):
                evidence.clean()

    def test_clean_draft_claim_with_source_url_passes(self):
        """Test that clean passes for draft claim with source_url."""
        evidence = BoardCandidateClaimEvidence(
            title="Test Evidence", source_url="https://example.com"
        )
        evidence.claim_id = 1

        with patch(
            "apps.owasp.models.board_candidate_claim_evidence.BoardCandidateClaim.objects"
        ) as mock_objects:
            mock_objects.filter.return_value.exists.return_value = True
            evidence.clean()

    def test_clean_no_file_and_no_source_url_raises_validation_error(self):
        """Test that clean raises ValidationError when neither file nor source_url."""
        evidence = BoardCandidateClaimEvidence(title="Test Evidence", source_url="")
        evidence.claim_id = 1
        evidence.file = None

        with patch(
            "apps.owasp.models.board_candidate_claim_evidence.BoardCandidateClaim.objects"
        ) as mock_objects:
            mock_objects.filter.return_value.exists.return_value = True

            with pytest.raises(ValidationError, match=r"Either file or source_url is required."):
                evidence.clean()

    def test_clean_with_file_sets_file_name(self):
        """Test that clean auto-sets file_name from file when not provided."""
        mock_file = MagicMock()
        mock_file.name = "document.pdf"
        mock_file.size = 12345
        mock_file.__bool__ = Mock(return_value=True)

        evidence = BoardCandidateClaimEvidence(title="Test Evidence")
        evidence.claim_id = 1
        evidence.file = mock_file
        evidence.file_name = ""
        evidence.file_size = None

        with patch(
            "apps.owasp.models.board_candidate_claim_evidence.BoardCandidateClaim.objects"
        ) as mock_objects:
            mock_objects.filter.return_value.exists.return_value = True
            evidence.clean()

        assert evidence.file_name == "document.pdf"
        assert evidence.file_size == 12345

    def test_clean_with_file_overwrites_existing_file_name(self):
        """Test that clean overwrites file_name when already set."""
        mock_file = MagicMock()
        mock_file.name = "document.pdf"
        mock_file.size = 12345
        mock_file.__bool__ = Mock(return_value=True)

        evidence = BoardCandidateClaimEvidence(title="Test Evidence")
        evidence.claim_id = 1
        evidence.file = mock_file
        evidence.file_name = "custom_name.pdf"
        evidence.file_size = 99999

        with patch(
            "apps.owasp.models.board_candidate_claim_evidence.BoardCandidateClaim.objects"
        ) as mock_objects:
            mock_objects.filter.return_value.exists.return_value = True
            evidence.clean()

        assert evidence.file_name == "document.pdf"
        assert evidence.file_size == 12345

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
