"""Tests for BoardVote model."""

from apps.owasp.models.board_vote import BoardVote


class TestBoardVoteModel:
    """Test cases for BoardVote model."""

    def test_str_representation_with_tally(self):
        """Test string representation includes result display and tally."""
        vote = BoardVote(result=BoardVote.Result.PASSED, tally="7-0")

        assert str(vote) == "Vote (Passed): 7-0"

    def test_str_representation_without_tally(self):
        """Test string representation when tally is empty falls back to 'n/a'."""
        vote = BoardVote(result=BoardVote.Result.FAILED)

        assert str(vote) == "Vote (Failed): n/a"

    def test_meta_options(self):
        """Test Meta options for BoardVote."""
        assert BoardVote._meta.db_table == "owasp_board_votes"
        assert BoardVote._meta.verbose_name_plural == "Board Votes"

    def test_result_choices(self):
        """Test Result choices are correctly defined."""
        assert BoardVote.Result.DEFERRED == "deferred"
        assert BoardVote.Result.FAILED == "failed"
        assert BoardVote.Result.PASSED == "passed"
        assert BoardVote.Result.TABLED == "tabled"
        assert BoardVote.Result.WITHDRAWN == "withdrawn"

    def test_type_choices(self):
        """Test Type choices are correctly defined."""
        assert BoardVote.Type.E_VOTE == "e_vote"
        assert BoardVote.Type.VOTE == "vote"

    def test_type_default_is_vote(self):
        """Test type default is VOTE."""
        assert BoardVote._meta.get_field("type").default == BoardVote.Type.VOTE

    def test_field_defaults(self):
        """Test default values on optional fields."""
        assert BoardVote._meta.get_field("metadata").default is dict
        assert BoardVote._meta.get_field("tally").default == ""

    def test_vote_cast_m2m_fields_target_entity_member(self):
        """Test in_favor, against, abstain, and recused M2M fields target EntityMember."""
        for name in ("in_favor", "against", "abstain", "recused"):
            field = BoardVote._meta.get_field(name)
            assert field.many_to_many
            assert field.related_model.__name__ == "EntityMember"

    def test_motion_fk_required_cascade(self):
        """Test motion FK is required and uses CASCADE on delete."""
        field = BoardVote._meta.get_field("motion")

        assert field.null is False
        assert field.related_model.__name__ == "BoardMotion"
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_has_timestamp_fields(self):
        """Test presence of TimestampedModel fields."""
        assert hasattr(BoardVote, "nest_created_at")
        assert hasattr(BoardVote, "nest_updated_at")
