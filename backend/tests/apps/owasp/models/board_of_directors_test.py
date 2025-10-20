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
