"""Tests for BoardMeetingAction model."""

from django.db import models

from apps.owasp.models.board_meeting_action import BoardMeetingAction


class TestBoardMeetingActionModel:
    """Test cases for BoardMeetingAction model."""

    def test_str_representation(self):
        """Test string representation includes order and meeting id."""
        action = BoardMeetingAction(order=3, meeting_id=42)

        assert str(action) == "Meeting Action #3 in meeting 42"

    def test_meta_options(self):
        """Test Meta options for BoardMeetingAction."""
        assert BoardMeetingAction._meta.db_table == "owasp_board_meeting_actions"
        assert BoardMeetingAction._meta.verbose_name_plural == "Board Meeting Actions"

    def test_unique_meeting_order_constraint(self):
        """Test unique constraint on (meeting, order) is declared with the right fields."""
        constraint = next(
            c
            for c in BoardMeetingAction._meta.constraints
            if c.name == "board_meeting_action_unique_meeting_order"
        )

        assert isinstance(constraint, models.UniqueConstraint)
        assert list(constraint.fields) == ["meeting", "order"]

    def test_exactly_one_target_check_constraint(self):
        """Test check constraint enforces exactly one of discussion/motion/outcome."""
        constraint = next(
            c
            for c in BoardMeetingAction._meta.constraints
            if c.name == "board_meeting_action_exactly_one_target"
        )

        assert isinstance(constraint, models.CheckConstraint)
        assert constraint.condition is not None
        condition = str(constraint.condition)
        assert "discussion__isnull" in condition
        assert "motion__isnull" in condition
        assert "outcome__isnull" in condition

    def test_target_fields_are_nullable_one_to_one(self):
        """Test target links are nullable OneToOneFields."""
        for name in ("discussion", "motion", "outcome"):
            field = BoardMeetingAction._meta.get_field(name)
            assert isinstance(field, models.OneToOneField)
            assert field.null is True

    def test_meeting_fk_is_required(self):
        """Test meeting foreign key is required."""
        field = BoardMeetingAction._meta.get_field("meeting")

        assert field.null is False
        assert field.related_model.__name__ == "BoardMeeting"

    def test_target_foreign_keys_point_at_expected_models(self):
        """Test target foreign keys point at the expected models."""
        expected = {
            "discussion": "BoardDiscussion",
            "motion": "BoardMotion",
            "outcome": "BoardOutcome",
        }
        for name, model_name in expected.items():
            field = BoardMeetingAction._meta.get_field(name)
            assert field.related_model.__name__ == model_name

    def test_has_timestamp_fields(self):
        """Test presence of TimestampedModel fields."""
        assert hasattr(BoardMeetingAction, "nest_created_at")
        assert hasattr(BoardMeetingAction, "nest_updated_at")
