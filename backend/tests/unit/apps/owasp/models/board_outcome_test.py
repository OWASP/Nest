"""Tests for BoardOutcome model."""

from apps.owasp.models.board_outcome import BoardOutcome


class TestBoardOutcomeModel:
    """Test cases for BoardOutcome model."""

    def test_str_representation(self):
        """Test string representation includes status and truncated description."""
        outcome = BoardOutcome(
            description="Finalize the Q1 audit report and distribute to the board.",
            status=BoardOutcome.Status.PENDING,
        )

        assert str(outcome).startswith("Outcome (Pending):")
        assert "Finalize the Q1 audit report" in str(outcome)

    def test_meta_options(self):
        """Test Meta options for BoardOutcome."""
        assert BoardOutcome._meta.db_table == "owasp_board_outcomes"
        assert BoardOutcome._meta.verbose_name_plural == "Board Outcomes"

    def test_status_choices(self):
        """Test Status choices are correctly defined."""
        assert BoardOutcome.Status.CANCELLED == "cancelled"
        assert BoardOutcome.Status.COMPLETED == "completed"
        assert BoardOutcome.Status.IN_PROGRESS == "in_progress"
        assert BoardOutcome.Status.PENDING == "pending"

    def test_status_default_is_pending(self):
        """Test status default is PENDING."""
        assert BoardOutcome._meta.get_field("status").default == BoardOutcome.Status.PENDING

    def test_field_defaults(self):
        """Test default values on optional fields."""
        assert BoardOutcome._meta.get_field("metadata").default is dict

    def test_due_date_nullable(self):
        """Test due_date is nullable."""
        assert BoardOutcome._meta.get_field("due_date").null is True

    def test_assignees_m2m_targets_entity_member(self):
        """Test assignees is M2M to EntityMember."""
        field = BoardOutcome._meta.get_field("assignees")

        assert field.many_to_many
        assert field.related_model.__name__ == "EntityMember"

    def test_has_timestamp_fields(self):
        """Test presence of TimestampedModel fields."""
        assert hasattr(BoardOutcome, "nest_created_at")
        assert hasattr(BoardOutcome, "nest_updated_at")
