"""Tests for BoardCandidateClaim model."""

from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ValidationError

from apps.owasp.models.board_candidate_claim import BoardCandidateClaim


class TestBoardCandidateClaimModel:
    """Tests for BoardCandidateClaim model."""

    def test_str_representation(self):
        """Test __str__ returns the claim name."""
        claim = BoardCandidateClaim(name="Test Claim Name")

        assert str(claim) == "Test Claim Name"

    def test_meta_options(self):
        """Test model meta options."""
        assert BoardCandidateClaim._meta.db_table == "owasp_board_candidate_claim"
        assert BoardCandidateClaim._meta.verbose_name_plural == "Board Candidate Claims"

    def test_meta_constraints(self):
        """Test model constraints are defined."""
        constraint_names = {c.name for c in BoardCandidateClaim._meta.constraints}

        assert "owasp_claim_candidate_key_unique" in constraint_names
        assert "owasp_claim_candidate_name_unique" in constraint_names

    def test_meta_indexes(self):
        """Test model indexes are defined."""
        index_names = {index.name for index in BoardCandidateClaim._meta.indexes}

        assert "owasp_claim_candidate_status" in index_names
        assert "owasp_claim_board_status" in index_names

    def test_has_timestamp_fields(self):
        """Test model has timestamp fields from TimestampedModel."""
        assert hasattr(BoardCandidateClaim, "nest_created_at")
        assert hasattr(BoardCandidateClaim, "nest_updated_at")

    def test_status_choices(self):
        """Test status choices are correctly defined."""
        assert BoardCandidateClaim.Status.APPROVED == "APPROVED"
        assert BoardCandidateClaim.Status.DISCARDED == "DISCARDED"
        assert BoardCandidateClaim.Status.DRAFT == "DRAFT"
        assert BoardCandidateClaim.Status.REJECTED == "REJECTED"
        assert BoardCandidateClaim.Status.SUBMITTED == "SUBMITTED"
        assert BoardCandidateClaim.Status.WITHDRAWN == "WITHDRAWN"

    def test_finalized_statuses(self):
        """Test FINALIZED_STATUSES contains the correct statuses."""
        expected = {
            BoardCandidateClaim.Status.APPROVED,
            BoardCandidateClaim.Status.DISCARDED,
            BoardCandidateClaim.Status.REJECTED,
            BoardCandidateClaim.Status.WITHDRAWN,
        }

        assert expected == BoardCandidateClaim.FINALIZED_STATUSES

    def test_default_status_is_draft(self):
        """Test default status is DRAFT."""
        field = BoardCandidateClaim._meta.get_field("status")

        assert field.default == BoardCandidateClaim.Status.DRAFT

    def test_default_is_locked_false(self):
        """Test default is_locked is False."""
        field = BoardCandidateClaim._meta.get_field("is_locked")

        assert field.default is False

    def test_default_order_zero(self):
        """Test default order is 0."""
        field = BoardCandidateClaim._meta.get_field("order")

        assert field.default == 0

    def test_board_field_nullable(self):
        """Test board field is nullable."""
        field = BoardCandidateClaim._meta.get_field("board")

        assert field.null
        assert field.blank

    def test_withdrawn_at_field_nullable(self):
        """Test withdrawn_at field is nullable."""
        field = BoardCandidateClaim._meta.get_field("withdrawn_at")

        assert field.null
        assert field.blank

    def test_withdrawn_reason_field_blank(self):
        """Test withdrawn_reason field allows blank."""
        field = BoardCandidateClaim._meta.get_field("withdrawn_reason")

        assert field.blank

    def test_name_max_length(self):
        """Test name field max_length."""
        field = BoardCandidateClaim._meta.get_field("name")

        assert field.max_length == 200

    def test_description_default_empty(self):
        """Test description field defaults to empty string."""
        field = BoardCandidateClaim._meta.get_field("description")

        assert field.default == ""

    def test_clean_new_claim_passes(self):
        """Test that clean passes for new draft claims without pk."""
        claim = BoardCandidateClaim(name="New Claim", status=BoardCandidateClaim.Status.DRAFT)
        claim.pk = None

        claim.clean()

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
    def test_clean_new_claim_non_draft_raises(self, status):
        """Test that clean raises ValidationError when creating a non-draft claim."""
        claim = BoardCandidateClaim(name="New Claim", status=status)
        claim.pk = None

        with pytest.raises(ValidationError) as exc_info:
            claim.clean()

        assert str(exc_info.value.messages[0]) == "New claims must be created as draft."

    @patch("apps.owasp.models.board_candidate_claim.BoardCandidateClaim.objects")
    def test_clean_nonexistent_pk_raises(self, mock_objects):
        """Test that clean raises ValidationError when claim with pk does not exist in DB."""
        mock_objects.filter.return_value.first.return_value = None

        claim = BoardCandidateClaim(name="Ghost Claim", status=BoardCandidateClaim.Status.DRAFT)
        claim.pk = 999

        with pytest.raises(ValidationError) as exc_info:
            claim.clean()

        assert str(exc_info.value.messages[0]) == "Claim does not exist."

    @pytest.mark.parametrize(
        ("from_status", "to_status"),
        [
            (BoardCandidateClaim.Status.DRAFT, BoardCandidateClaim.Status.SUBMITTED),
            (BoardCandidateClaim.Status.DRAFT, BoardCandidateClaim.Status.DISCARDED),
            (BoardCandidateClaim.Status.SUBMITTED, BoardCandidateClaim.Status.APPROVED),
            (BoardCandidateClaim.Status.SUBMITTED, BoardCandidateClaim.Status.REJECTED),
            (BoardCandidateClaim.Status.SUBMITTED, BoardCandidateClaim.Status.WITHDRAWN),
            (BoardCandidateClaim.Status.APPROVED, BoardCandidateClaim.Status.WITHDRAWN),
        ],
    )
    @patch("apps.owasp.models.board_candidate_claim.BoardCandidateClaim.objects")
    def test_clean_valid_transition_passes(self, mock_objects, from_status, to_status):
        """Test that clean passes for valid status transitions."""
        existing = BoardCandidateClaim(
            name="Original Name",
            description="Original Description",
            status=from_status,
            is_locked=from_status in BoardCandidateClaim.FINALIZED_STATUSES,
        )
        existing.pk = 1
        mock_objects.filter.return_value.first.return_value = existing

        claim = BoardCandidateClaim(
            name=existing.name,
            description=existing.description,
            status=to_status,
        )
        claim.is_locked = existing.is_locked
        claim.pk = 1

        if to_status == BoardCandidateClaim.Status.WITHDRAWN:
            for field in claim._meta.fields:
                if field.attname not in BoardCandidateClaim.WITHDRAWAL_ALLOWED_FIELDS:
                    setattr(claim, field.attname, getattr(existing, field.attname))

        claim.clean()

    @pytest.mark.parametrize(
        ("from_status", "to_status"),
        [
            (BoardCandidateClaim.Status.DRAFT, BoardCandidateClaim.Status.APPROVED),
            (BoardCandidateClaim.Status.DRAFT, BoardCandidateClaim.Status.REJECTED),
            (BoardCandidateClaim.Status.DRAFT, BoardCandidateClaim.Status.WITHDRAWN),
            (BoardCandidateClaim.Status.SUBMITTED, BoardCandidateClaim.Status.DRAFT),
            (BoardCandidateClaim.Status.SUBMITTED, BoardCandidateClaim.Status.DISCARDED),
            (BoardCandidateClaim.Status.APPROVED, BoardCandidateClaim.Status.DRAFT),
            (BoardCandidateClaim.Status.APPROVED, BoardCandidateClaim.Status.SUBMITTED),
            (BoardCandidateClaim.Status.APPROVED, BoardCandidateClaim.Status.REJECTED),
            (BoardCandidateClaim.Status.APPROVED, BoardCandidateClaim.Status.DISCARDED),
            (BoardCandidateClaim.Status.REJECTED, BoardCandidateClaim.Status.DRAFT),
            (BoardCandidateClaim.Status.REJECTED, BoardCandidateClaim.Status.SUBMITTED),
            (BoardCandidateClaim.Status.REJECTED, BoardCandidateClaim.Status.APPROVED),
            (BoardCandidateClaim.Status.REJECTED, BoardCandidateClaim.Status.DISCARDED),
            (BoardCandidateClaim.Status.REJECTED, BoardCandidateClaim.Status.WITHDRAWN),
            (BoardCandidateClaim.Status.DISCARDED, BoardCandidateClaim.Status.DRAFT),
            (BoardCandidateClaim.Status.DISCARDED, BoardCandidateClaim.Status.SUBMITTED),
            (BoardCandidateClaim.Status.DISCARDED, BoardCandidateClaim.Status.APPROVED),
            (BoardCandidateClaim.Status.DISCARDED, BoardCandidateClaim.Status.REJECTED),
            (BoardCandidateClaim.Status.DISCARDED, BoardCandidateClaim.Status.WITHDRAWN),
            (BoardCandidateClaim.Status.WITHDRAWN, BoardCandidateClaim.Status.DRAFT),
            (BoardCandidateClaim.Status.WITHDRAWN, BoardCandidateClaim.Status.SUBMITTED),
            (BoardCandidateClaim.Status.WITHDRAWN, BoardCandidateClaim.Status.APPROVED),
            (BoardCandidateClaim.Status.WITHDRAWN, BoardCandidateClaim.Status.REJECTED),
            (BoardCandidateClaim.Status.WITHDRAWN, BoardCandidateClaim.Status.DISCARDED),
        ],
    )
    @patch("apps.owasp.models.board_candidate_claim.BoardCandidateClaim.objects")
    def test_clean_invalid_transition_raises(self, mock_objects, from_status, to_status):
        """Test that clean raises for invalid status transitions."""
        existing = BoardCandidateClaim(
            name="Original Name",
            description="Original Description",
            status=from_status,
            is_locked=from_status in BoardCandidateClaim.FINALIZED_STATUSES,
        )
        existing.pk = 1
        mock_objects.filter.return_value.first.return_value = existing

        claim = BoardCandidateClaim(
            name=existing.name,
            description=existing.description,
            status=to_status,
        )
        claim.is_locked = existing.is_locked
        claim.pk = 1

        with pytest.raises(ValidationError) as exc_info:
            claim.clean()

        assert (
            str(exc_info.value.messages[0])
            == f"Invalid status transition from {from_status} to {to_status}."
        )

    @patch("apps.owasp.models.board_candidate_claim.BoardCandidateClaim.objects")
    def test_clean_withdrawal_from_submitted_with_disallowed_field_change_raises(
        self, mock_objects
    ):
        """Test that clean raises when changing disallowed fields during withdrawal."""
        existing = BoardCandidateClaim(
            name="Original Name",
            description="Original Description",
            status=BoardCandidateClaim.Status.SUBMITTED,
            is_locked=False,
        )
        existing.pk = 1
        mock_objects.filter.return_value.first.return_value = existing

        claim = BoardCandidateClaim(
            name="Updated Name",
            description=existing.description,
            status=BoardCandidateClaim.Status.WITHDRAWN,
        )
        claim.is_locked = existing.is_locked
        claim.pk = 1

        with pytest.raises(ValidationError) as exc_info:
            claim.clean()

        assert str(exc_info.value.messages[0]) == "Cannot update fields while withdrawing a claim."

    @patch("apps.owasp.models.board_candidate_claim.BoardCandidateClaim.objects")
    def test_clean_non_draft_claim_disallows_field_updates(self, mock_objects):
        """Test that non-draft claims cannot update non-status fields."""
        existing = BoardCandidateClaim(
            name="Original Name",
            description="Original Description",
            status=BoardCandidateClaim.Status.SUBMITTED,
            is_locked=False,
        )
        existing.pk = 1
        mock_objects.filter.return_value.first.return_value = existing

        claim = BoardCandidateClaim(
            name="Updated Name",
            description=existing.description,
            status=BoardCandidateClaim.Status.SUBMITTED,
        )
        claim.is_locked = existing.is_locked
        claim.pk = 1

        with pytest.raises(ValidationError) as exc_info:
            claim.clean()

        assert str(exc_info.value.messages[0]) == "Can only update status on a non-draft claim"

    @patch("apps.owasp.models.board_candidate_claim.BoardCandidateClaim.objects")
    def test_clean_non_draft_claim_allows_status_update_only(self, mock_objects):
        """Test that non-draft claims can change status when fields are unchanged."""
        existing = BoardCandidateClaim(
            name="Original Name",
            description="Original Description",
            status=BoardCandidateClaim.Status.SUBMITTED,
            is_locked=False,
        )
        existing.pk = 1
        mock_objects.filter.return_value.first.return_value = existing

        claim = BoardCandidateClaim(
            name=existing.name,
            description=existing.description,
            status=BoardCandidateClaim.Status.APPROVED,
        )
        claim.is_locked = existing.is_locked
        claim.pk = 1

        claim.clean()

    @patch.object(BoardCandidateClaim, "full_clean")
    @patch("apps.owasp.models.board_candidate_claim.TimestampedModel.save")
    def test_save_calls_full_clean(self, mock_super_save, mock_full_clean):
        """Test that save calls full_clean before saving."""
        claim = BoardCandidateClaim(name="Test Claim", status=BoardCandidateClaim.Status.DRAFT)

        claim.save()

        mock_full_clean.assert_called_once()
        mock_super_save.assert_called_once()

    @pytest.mark.parametrize(
        "status",
        [
            BoardCandidateClaim.Status.APPROVED,
            BoardCandidateClaim.Status.DISCARDED,
            BoardCandidateClaim.Status.REJECTED,
            BoardCandidateClaim.Status.WITHDRAWN,
        ],
    )
    @patch.object(BoardCandidateClaim, "full_clean")
    @patch("apps.owasp.models.board_candidate_claim.TimestampedModel.save")
    def test_save_locks_claim_on_finalized_status(self, mock_super_save, mock_full_clean, status):
        """Test that save sets is_locked=True for finalized statuses."""
        claim = BoardCandidateClaim(name="Test Claim", status=status)
        claim.is_locked = False

        claim.save()

        assert claim.is_locked is True

    @pytest.mark.parametrize(
        "status",
        [
            BoardCandidateClaim.Status.DRAFT,
            BoardCandidateClaim.Status.SUBMITTED,
        ],
    )
    @patch.object(BoardCandidateClaim, "full_clean")
    @patch("apps.owasp.models.board_candidate_claim.TimestampedModel.save")
    def test_save_does_not_lock_claim_on_non_finalized_status(
        self, mock_super_save, mock_full_clean, status
    ):
        """Test that save does not set is_locked=True for non-finalized statuses."""
        claim = BoardCandidateClaim(name="Test Claim", status=status)
        claim.is_locked = False

        claim.save()

        assert claim.is_locked is False

    @patch("apps.owasp.models.board_candidate_claim.BulkSaveModel.bulk_save")
    def test_bulk_save_delegates(self, mock_bulk_save):
        """Test bulk_save delegates to BulkSaveModel.bulk_save."""
        claims = [MagicMock()]

        BoardCandidateClaim.bulk_save(claims, fields=["order"])

        mock_bulk_save.assert_called_once_with(BoardCandidateClaim, claims, fields=["order"])

    @patch.object(BoardCandidateClaim, "full_clean")
    @patch("apps.owasp.models.board_candidate_claim.TimestampedModel.save")
    @patch("apps.owasp.models.board_candidate_claim.BoardCandidateClaim.objects")
    def test_save_sets_order_on_create(self, mock_objects, mock_super_save, mock_full_clean):
        """Test save auto-assigns order on create."""
        mock_queryset = MagicMock()
        mock_queryset.aggregate.return_value = {"max_order": 4}
        mock_objects.filter.return_value = mock_queryset

        claim = BoardCandidateClaim(name="Test Claim", status=BoardCandidateClaim.Status.DRAFT)
        claim.candidate_id = 10
        claim.board_id = 20
        claim.pk = None

        claim.save()

        assert claim.order == 5
