"""Tests for BoardMeeting model."""

from datetime import UTC, datetime

from apps.owasp.models.board_meeting import BoardMeeting


class TestBoardMeetingModel:
    """Test cases for BoardMeeting model."""

    def test_str_representation_with_title(self):
        """Test string representation prefers title."""
        meeting = BoardMeeting(
            title="August 2025",
            date=datetime(2025, 8, 26, 13, 0, tzinfo=UTC),
        )

        assert str(meeting) == "Board Meeting: August 2025"

    def test_str_representation_without_title(self):
        """Test string representation falls back to ISO datetime when title is empty."""
        meeting = BoardMeeting(
            title="",
            date=datetime(2025, 8, 26, 13, 0, tzinfo=UTC),
        )

        assert str(meeting) == "Board Meeting: 2025-08-26T13:00:00+00:00"

    def test_meta_options(self):
        """Test Meta options for BoardMeeting."""
        assert BoardMeeting._meta.db_table == "owasp_board_meetings"
        assert BoardMeeting._meta.verbose_name_plural == "Board Meetings"

    def test_source_path_unique(self):
        """Test source_path is unique."""
        assert BoardMeeting._meta.get_field("source_path").unique is True

    def test_type_choices(self):
        """Test Type choices are correctly defined."""
        assert BoardMeeting.Type.PRIVATE == "private"
        assert BoardMeeting.Type.PUBLIC == "public"
        assert BoardMeeting.Type.SPECIAL == "special"
        assert BoardMeeting.Type.SUMMIT == "summit"

    def test_type_default_is_public(self):
        """Test type default is PUBLIC."""
        assert BoardMeeting._meta.get_field("type").default == BoardMeeting.Type.PUBLIC

    def test_field_defaults(self):
        """Test default values on optional fields."""
        assert BoardMeeting._meta.get_field("metadata").default is dict
        assert BoardMeeting._meta.get_field("attachments").default is list
        assert BoardMeeting._meta.get_field("call_in_url").default == ""
        assert BoardMeeting._meta.get_field("recording_url").default == ""
        assert BoardMeeting._meta.get_field("location").default == ""
        assert BoardMeeting._meta.get_field("title").default == ""
        assert BoardMeeting._meta.get_field("source_checksum").default == ""

    def test_quorum_present_nullable(self):
        """Test quorum_present is nullable."""
        assert BoardMeeting._meta.get_field("quorum_present").null is True

    def test_date_is_datetime_field(self):
        """Test date field is a DateTimeField."""
        field = BoardMeeting._meta.get_field("date")

        assert field.get_internal_type() == "DateTimeField"

    def test_board_fk_targets_board_of_directors_cascade(self):
        """Test board FK targets BoardOfDirectors and cascades."""
        field = BoardMeeting._meta.get_field("board")

        assert field.related_model.__name__ == "BoardOfDirectors"
        assert field.null is False
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_source_path_max_length(self):
        """Test source_path max_length is 500."""
        assert BoardMeeting._meta.get_field("source_path").max_length == 500

    def test_attendance_m2m_fields_target_entity_member(self):
        """Test attendees and absentees M2M fields target EntityMember."""
        for name in ("attendees", "absentees"):
            field = BoardMeeting._meta.get_field(name)
            assert field.many_to_many
            assert field.related_model.__name__ == "EntityMember"

    def test_guests_is_json_list(self):
        """Test guests is a JSON field defaulting to an empty list."""
        field = BoardMeeting._meta.get_field("guests")

        assert field.get_internal_type() == "JSONField"
        assert field.default is list

    def test_source_checksum_max_length(self):
        """Test source_checksum max_length is 64 (SHA-256 hex)."""
        assert BoardMeeting._meta.get_field("source_checksum").max_length == 64

    def test_has_timestamp_fields(self):
        """Test presence of TimestampedModel fields."""
        assert hasattr(BoardMeeting, "nest_created_at")
        assert hasattr(BoardMeeting, "nest_updated_at")
