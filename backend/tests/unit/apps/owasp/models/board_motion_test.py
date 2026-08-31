"""Tests for BoardMotion model."""

from apps.owasp.models.board_motion import BoardMotion


class TestBoardMotionModel:
    """Test cases for BoardMotion model."""

    def test_str_representation(self):
        """Test string representation."""
        motion = BoardMotion(title="Approve 2026 Budget")

        assert str(motion) == "Motion: Approve 2026 Budget"

    def test_meta_options(self):
        """Test Meta options for BoardMotion."""
        assert BoardMotion._meta.db_table == "owasp_board_motions"
        assert BoardMotion._meta.verbose_name_plural == "Board Motions"

    def test_amends_motion_is_self_fk_nullable_cascade(self):
        """Test amends_motion is a nullable self-FK with CASCADE."""
        field = BoardMotion._meta.get_field("amends_motion")

        assert field.related_model is BoardMotion
        assert field.null is True
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_sponsor_and_second_fks_target_entity_member(self):
        """Test sponsor and second FKs target EntityMember and CASCADE."""
        for name in ("sponsor", "second"):
            field = BoardMotion._meta.get_field(name)
            assert field.related_model.__name__ == "EntityMember"
            assert field.null is True
            assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_field_defaults(self):
        """Test default values on optional fields."""
        assert BoardMotion._meta.get_field("metadata").default is dict
        assert BoardMotion._meta.get_field("references").default is list
        assert BoardMotion._meta.get_field("background").default == ""

    def test_has_timestamp_fields(self):
        """Test presence of TimestampedModel fields."""
        assert hasattr(BoardMotion, "nest_created_at")
        assert hasattr(BoardMotion, "nest_updated_at")
