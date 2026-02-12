from unittest.mock import Mock, patch

from apps.owasp.models.board_of_directors import BoardOfDirectors


class TestBoardOfDirectorsModel:
    def test_str_representation(self):
        board = BoardOfDirectors(year=2025)

        assert str(board) == "OWASP 2025 Board of Directors"

    def test_meta_options(self):
        assert BoardOfDirectors._meta.db_table == "owasp_board_of_directors"
        assert BoardOfDirectors._meta.verbose_name_plural == "Board of Directors"

    def test_year_field_unique(self):
        field = BoardOfDirectors._meta.get_field("year")

        assert field.unique is True

    def test_has_timestamp_fields(self):
        assert hasattr(BoardOfDirectors, "created_at")
        assert hasattr(BoardOfDirectors, "updated_at")

    def test_has_candidates_method(self):
        board = BoardOfDirectors(year=2025)

        assert hasattr(board, "get_candidates")
        assert callable(board.get_candidates)

    def test_has_members_method(self):
        board = BoardOfDirectors(year=2025)

        assert hasattr(board, "get_members")
        assert callable(board.get_members)

    def test_owasp_url_property(self):
        board = BoardOfDirectors(year=2025)

        assert board.owasp_url == "https://board.owasp.org/elections/2025_elections"

    @patch("apps.owasp.models.board_of_directors.ContentType")
    @patch("apps.owasp.models.board_of_directors.EntityMember")
    def test_get_candidates_returns_filtered_queryset(self, mock_entity_member, mock_content_type):
        """Test get_candidates filters by CANDIDATE role and returns ordered queryset."""
        board = BoardOfDirectors(year=2025)
        board.id = 1
        mock_ct = Mock()
        mock_content_type.objects.get_for_model.return_value = mock_ct

        mock_qs = Mock()
        mock_entity_member.objects.filter.return_value.order_by.return_value = mock_qs

        result = board.get_candidates()

        assert result == mock_qs
        mock_entity_member.objects.filter.assert_called_once()
        call_kwargs = mock_entity_member.objects.filter.call_args[1]
        assert call_kwargs["entity_type"] == mock_ct
        assert call_kwargs["entity_id"] == 1
        assert call_kwargs["role"] == mock_entity_member.Role.CANDIDATE
        assert call_kwargs["is_active"] is True
        assert call_kwargs["is_reviewed"] is True
        mock_entity_member.objects.filter.return_value.order_by.assert_called_once_with(
            "member_name"
        )

    @patch("apps.owasp.models.board_of_directors.ContentType")
    @patch("apps.owasp.models.board_of_directors.EntityMember")
    def test_get_members_returns_filtered_queryset(self, mock_entity_member, mock_content_type):
        """Test get_members filters by MEMBER role and returns ordered queryset."""
        board = BoardOfDirectors(year=2025)
        board.id = 1
        mock_ct = Mock()
        mock_content_type.objects.get_for_model.return_value = mock_ct

        mock_qs = Mock()
        mock_entity_member.objects.filter.return_value.order_by.return_value = mock_qs

        result = board.get_members()

        assert result == mock_qs
        mock_entity_member.objects.filter.assert_called_once()
        call_kwargs = mock_entity_member.objects.filter.call_args[1]
        assert call_kwargs["entity_type"] == mock_ct
        assert call_kwargs["entity_id"] == 1
        assert call_kwargs["role"] == mock_entity_member.Role.MEMBER
        assert call_kwargs["is_active"] is True
        assert call_kwargs["is_reviewed"] is True
        mock_entity_member.objects.filter.return_value.order_by.assert_called_once_with(
            "member_name"
        )
