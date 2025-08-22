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
        self.boolean_values = self.parser._BOOLEAN_TRUE_VALUES | self.parser._BOOLEAN_FALSE_VALUES
        self.true_boolean_values = self.parser._BOOLEAN_TRUE_VALUES
        self.comparison_operators = self.parser._COMPARISON_OPERATORS

    def test_invalid_parser_field_validation(self):
        with pytest.raises(QueryParserError) as ei:
            QueryParser(allowed_fields={"field": "invalid_type"})
        assert ei.value.error_type == "FIELD_TYPE_ERROR"

        with pytest.raises(QueryParserError) as ei:
            QueryParser(allowed_fields={"field-with-dash": "string"})
        assert ei.value.error_type == "FIELD_NAME_ERROR"

    @pytest.mark.parametrize(
        ("parser_type", "expected_string"),
        [
            ("parser", '"john doe"'),
            ("case_sensitive_parser", '"John Doe"'),
            ("strict_parser", '"john doe"'),
            ("case_sensitive_strict_parser", '"John Doe"'),
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

    def test_comparison_operators(self):
        for op in self.comparison_operators:
            result = self.parser.parse(f"stars:{op}100")
            assert len(result) == 1
            assert result[0]["field"] == "stars"
            assert result[0]["type"] == "number"
            assert result[0]["op"] == op
            assert result[0]["number"] == "100"

    def test_boolean_variations(self):
        for bool_val in self.boolean_values:
            result = self.parser.parse(f"archived:{bool_val}")
            assert len(result) == 1
            assert result[0]["field"] == "archived"
            assert result[0]["type"] == "boolean"
            expected = "True" if bool_val in self.true_boolean_values else "False"
            assert result[0]["boolean"] == expected

    @pytest.mark.parametrize(
        ("query", "expected"),
        [
            (
                'author:"John Doe" stars:>100 archived:false some "free text"',
                [
                    {"type": "string", "field": "author", "string": '"john doe"'},
                    {"type": "number", "field": "stars", "op": ">", "number": "100"},
                    {"type": "boolean", "field": "archived", "boolean": "False"},
                    {"type": "string", "field": "query", "string": "some"},
                    {"type": "string", "field": "query", "string": '"free text"'},
                ],
            ),
            (
                'project:"my-awesome-project" language:"C++"',
                [
                    {"type": "string", "field": "project", "string": '"my-awesome-project"'},
                    {"type": "string", "field": "language", "string": '"c++"'},
                ],
            ),
        ],
    )
    def test_complex_queries_and_mixed_content(self, query, expected):
        result = self.parser.parse(query)
        assert result == expected

    malformed_queries = ['not_field:"operation"', "not_field:operation"]

    @pytest.mark.parametrize("query", malformed_queries)
    def test_malformed_queries(self, query):
        result = self.parser.parse(query)
        assert not result

    @pytest.mark.parametrize("query", malformed_queries)
    def test_invalid_queries(self, query):
        with pytest.raises(QueryParserError):
            self.strict_parser.parse(query)

    def test_date_format_validation(self):
        valid_dates = ["2023-01-01", "2023-12-31"]
        for date_str in valid_dates:
            result = self.parser.parse(f"created:{date_str}")
            assert len(result) == 1
            assert result[0]["date"] == date_str

        invalid_dates = ["invalid-date", "2023-163-01", "2023-01-362"]
        for inv_date_str in invalid_dates:
            with pytest.raises(QueryParserError, match="Invalid date value"):
                self.strict_parser.parse(f"created:{inv_date_str}")

        for inv_date_str in invalid_dates:
            result = self.parser.parse(f"created:{inv_date_str}")
            assert not result

    def test_invalid_initialization(self):
        with pytest.raises(QueryParserError):
            QueryParser(allowed_fields={"field": "invalid_type"})

    def test_custom_default_field(self):
        parser_with_default = QueryParser(
            allowed_fields={"test": "string"}, default_field="default"
        )
        result = parser_with_default.parse("query:test free_text")
        expected = [
            {"type": "string", "field": "default", "string": "free_text"},
        ]
        assert result == expected

    @pytest.mark.parametrize(
        ("query"),
        ["author:", ":123", '"field: true"', "2341"],
    )
    def test_boundary_conditions(self, query):
        result = self.parser.parse(query)
        assert len(result) == 1
        assert result[0]["field"] == "query"
        assert result[0]["type"] == "string"
        assert result[0]["string"] == query

    def test_long_field_names_and_values(self):
        long_field_parser = QueryParser(allowed_fields={"verylongfieldname": "string"})
        long_value = "a" * 1000
        result = long_field_parser.parse(f'verylongfieldname:"{long_value}"')
        assert isinstance(result, list)
        assert result[0]["string"] == '"' + long_value + '"'

    @pytest.mark.parametrize("val", ["0", "-1", "999999", "3.14159"])
    def test_numeric_values(self, val):
        result = self.parser.parse(f"stars:{val}")
        assert len(result) == 1
        assert result[0]["type"] == "number"
        assert result[0]["field"] == "stars"
        assert result[0]["number"] == str(int(float(val)))
        assert result[0]["op"] == "="
