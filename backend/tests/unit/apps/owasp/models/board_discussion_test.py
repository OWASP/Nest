"""Tests for BoardDiscussion model."""

from apps.owasp.models.board_discussion import BoardDiscussion


class TestBoardDiscussionModel:
    """Test cases for BoardDiscussion model."""

    def test_str_representation(self):
        """Test string representation."""
        discussion = BoardDiscussion(topic="Marketing strategy for 2026")

        assert str(discussion) == "Discussion: Marketing strategy for 2026"

    def test_meta_options(self):
        """Test Meta options for BoardDiscussion."""
        assert BoardDiscussion._meta.db_table == "owasp_board_discussions"
        assert BoardDiscussion._meta.verbose_name_plural == "Board Discussions"

    def test_field_defaults(self):
        """Test default values on optional fields."""
        assert BoardDiscussion._meta.get_field("metadata").default is dict

    def test_topic_max_length(self):
        """Test topic max_length is 500."""
        assert BoardDiscussion._meta.get_field("topic").max_length == 500

    def test_participants_m2m_targets_entity_member(self):
        """Test participants is M2M to EntityMember."""
        field = BoardDiscussion._meta.get_field("participants")

        assert field.many_to_many
        assert field.related_model.__name__ == "EntityMember"

    def test_has_timestamp_fields(self):
        """Test presence of TimestampedModel fields."""
        assert hasattr(BoardDiscussion, "nest_created_at")
        assert hasattr(BoardDiscussion, "nest_updated_at")
