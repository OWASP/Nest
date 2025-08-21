import pytest

from apps.common.search.query_parser import QueryParser, QueryParserError


class TestQueryParser:
    def setup_method(self):
        self.allowed_fields = {
            "author": "string",
            "stars": "number",
            "issues": "number",
            "project": "string",
            "archived": "boolean",
            "language": "string",
            "created": "date",
        }

        self.parser = QueryParser(allowed_fields=self.allowed_fields)
        self.case_sensitive_parser = QueryParser(
            allowed_fields=self.allowed_fields, default_field="test", case_sensitive=True
        )
        self.strict_parser = QueryParser(allowed_fields=self.allowed_fields, strict=True)
        self.case_sensitive_strict_parser = QueryParser(
            allowed_fields=self.allowed_fields, strict=True, case_sensitive=True
        )

    def test_invalid_parser_field_validation(self):
        with pytest.raises(QueryParserError, match="Invalid field type"):
            QueryParser(allowed_fields={"field": "invalid_type"})

        with pytest.raises(Exception, match="Expected end of text"):
            QueryParser(allowed_fields={"field-with-dash": "string"})

    @pytest.mark.parametrize(
        ("parser_type", "expected_string"),
        [
            ("parser", "john doe"),
            ("case_sensitive_parser", "John Doe"),
            ("strict_parser", "john doe"),
            ("case_sensitive_strict_parser", "John Doe"),
        ],
    )
    def test_basic_field_parsing_all_types(self, parser_type, expected_string):
        parser = getattr(self, parser_type)
        result = parser.parse('Author:"John Doe"')
        assert len(result) == 1
        assert result[0]["field"] == "author"
        assert result[0]["type"] == "string"
        assert result[0]["string"] == expected_string

    def test_parser_configuration_differences(self):
        query = "AUTHOR:test"
        result = self.case_sensitive_parser.parse(query)
        assert len(result) == 1
        assert result[0]["field"] == "author"

    def test_comparison_operators_and_boolean_variations(self):
        @pytest.mark.parametrize("op", ["<", "<=", ">", ">=", "="])
        def test_operator_variations(self, op):
            result = self.parser.parse(f"stars:{op}100")
            assert len(result) == 1
            assert result[0]["field"] == "stars"
            assert result[0]["type"] == "number"
            assert result[0]["op"] == op
            assert result[0]["number"] == "100"

        boolean_values = ["true", "false", "True", "False", "TRUE", "FALSE"]

        @pytest.mark.parametrize("bool_val", boolean_values)
        def test_boolean_variations(self, bool_val):
            result = self.parser.parse(f"archived:{bool_val}")
            assert len(result) == 1
            assert result[0]["field"] == "archived"
            assert result[0]["type"] == "boolean"
            assert result[0]["boolean"] == bool_val

    @pytest.mark.parametrize(
        ("query", "expected"),
        [
            (
                'author:"John Doe" stars:>100 archived:false some "free text"',
                [
                    {"type": "string", "field": "author", "string": "john doe"},
                    {"type": "number", "field": "stars", "op": ">", "number": "100"},
                    {"type": "boolean", "field": "archived", "boolean": "False"},
                    {"type": "string", "field": "query", "string": "some"},
                    {"type": "string", "field": "query", "string": "free text"},
                ],
            ),
            (
                'project:"my-awesome-project" language:"C++"',
                [
                    {"type": "string", "field": "project", "string": "my-awesome-project"},
                    {"type": "string", "field": "language", "string": "c++"},
                ],
            ),
        ],
    )
    def test_complex_queries_and_mixed_content(self, query, expected):
        result = self.parser.parse(query)
        assert result == expected

    def test_error_handling_and_malformed_queries(self):
        malformed_queries = ["field_without_colon", ":value_without_field", "field:", ""]

        @pytest.mark.parametrize("query", malformed_queries)
        def test_malformed_queries(self, query):
            result = self.parser.parse(query)
            if query == "":
                assert not result
            else:
                assert result[0]["field"] == "query"
                assert result[0]["type"] == "string"
                assert result[0]["string"] == query

        @pytest.mark.parametrize("query", malformed_queries)
        def test_invalid_queries(self, query):
            with pytest.raises(QueryParserError):
                self.strict_parser.parse(query)

    def test_date_format_validation(self):
        @pytest.mark.parametrize("date_str", ["2023-01-01", "2023-12-31"])
        def test_valid_dates(self, date_str):
            result = self.parser.parse(f"created:{date_str}")
            assert len(result) == 1
            assert result[0]["date"] == date_str

        @pytest.mark.parametrize("inv_date_str", ["invalid-date", "2023-2213-01", "2023-01-322"])
        def test_invalid_dates(self, inv_date_str):
            result = self.parser.parse(f"created:{inv_date_str}")
            assert not result

    def test_initialization(self):
        def test_invalid_initialization():
            with pytest.raises(QueryParserError):
                QueryParser(allowed_fields=None)

        @pytest.mark.parametrize(
            ("allowed_fields", "default_field", "query", "expected"),
            [
                (
                    {"query": "string"},
                    "query",
                    "query:test free_text",
                    [
                        {"type": "string", "field": "query", "string": "test"},
                        {"type": "string", "field": "query", "string": "free_text"},
                    ],
                )
            ],
        )
        def test_valid_initialization(allowed_fields, default_field, query, expected):
            parser_with_default = QueryParser(
                allowed_fields=allowed_fields, default_field=default_field
            )
            result = parser_with_default.parse(query)
            assert result == expected

    def test_boundary_conditions_and_edge_cases(self):
        @pytest.mark.parametrize(
            ("query", "expected"),
            [
                ("author:", {"field": "query", "type": "string", "string": "author:"}),
                (":123", {"field": "query", "type": "string", "string": ":123"}),
                ('"field: true"', {"field": "query", "type": "string", "boolean": True}),
                ("2341", {"field": "query", "type": "string", "string": "2341"}),
            ],
        )
        def test_boundary_conditions_and_edge_cases(self, query, expected):
            result = self.parser.parse(query)
            assert result == [expected]

        def test_long_field_names():
            long_field_parser = QueryParser(allowed_fields={"verylongfieldname": "string"})
            long_value = "a" * 1000
            result = long_field_parser.parse(f'verylongfieldname:"{long_value}"')
            assert isinstance(result, list)
            assert result[0]["string"] == long_value

        @pytest.mark.parametrize("val", ["0", "-1", "999999", "3.14159"])
        def test_numeric_values(self, val):
            result = self.parser.parse(f"stars:{val}")
            assert len(result) == 1
            assert result[0]["type"] == "number"
            assert result[0]["field"] == "stars"
            assert result[0]["number"] == str(int(float(val)))
            assert result[0]["op"] == "="
