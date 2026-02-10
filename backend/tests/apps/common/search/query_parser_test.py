import pytest

from apps.common.search.query_parser import QueryParser, QueryParserError


class TestQueryParser:
    unknown_field_queries = ['not_field:"operation"', "not_field:operation"]

    def setup_method(self):
        self.field_schema = {
            "archived": "boolean",
            "author": "string",
            "created": "date",
            "issues": "number",
            "language": "string",
            "project": "string",
            "stars": "number",
        }

        self.parser = QueryParser(field_schema=self.field_schema)
        self.case_sensitive_parser = QueryParser(
            field_schema=self.field_schema, default_field="test", case_sensitive=True
        )
        self.strict_parser = QueryParser(field_schema=self.field_schema, strict=True)
        self.case_sensitive_strict_parser = QueryParser(
            field_schema=self.field_schema, strict=True, case_sensitive=True
        )
        self.boolean_values = {"true", "1", "yes", "on", "false", "0", "no", "off"}
        self.true_boolean_values = {"true", "1", "yes", "on"}
        self.comparison_operators = ["<", "<=", ">", ">=", "="]

    def test_invalid_parser_field_validation(self):
        with pytest.raises(QueryParserError) as e:
            QueryParser(field_schema={"field": "invalid_type"})
        assert e.value.error_type == "FIELD_TYPE_ERROR"

        with pytest.raises(QueryParserError) as e:
            QueryParser(field_schema={"field-with-dash": "string"})
        assert e.value.error_type == "FIELD_NAME_ERROR"

    @pytest.mark.parametrize(
        ("parser_type", "expected_string"),
        [
            ("case_sensitive_parser", '"John Doe"'),
            ("case_sensitive_strict_parser", '"John Doe"'),
            ("parser", '"john doe"'),
            ("strict_parser", '"john doe"'),
        ],
    )
    def test_basic_field_parsing_all_types(self, parser_type, expected_string):
        parser = getattr(self, parser_type)

        assert parser.parse('Author:"John Doe"') == [
            {
                "field": "author",
                "type": "string",
                "value": expected_string,
            }
        ]

    def test_parser_configuration_differences(self):
        query = "AUTHOR:test"
        assert self.case_sensitive_parser.parse(query) == [
            {
                "field": "author",
                "type": "string",
                "value": "test",
            }
        ]

    def test_comparison_operators(self):
        for op in self.comparison_operators:
            assert self.parser.parse(f"stars:{op}100") == [
                {
                    "field": "stars",
                    "op": op,
                    "type": "number",
                    "value": 100,
                },
            ]

    def test_boolean_variations(self):
        for boolean_value in self.boolean_values:
            assert self.parser.parse(f"archived:{boolean_value}") == [
                {
                    "field": "archived",
                    "type": "boolean",
                    "value": boolean_value in self.true_boolean_values,
                }
            ]

    @pytest.mark.parametrize(
        ("query", "expected"),
        [
            (
                'author:"John Doe" stars:>100 archived:false some "free text"',
                [
                    {"type": "string", "field": "author", "value": '"john doe"'},
                    {"type": "number", "field": "stars", "op": ">", "value": 100},
                    {"type": "boolean", "field": "archived", "value": False},
                    {"type": "string", "field": "query", "value": "some"},
                    {"type": "string", "field": "query", "value": "free text"},
                ],
            ),
            (
                'project:"my-awesome-project" language:"C++"',
                [
                    {"type": "string", "field": "project", "value": '"my-awesome-project"'},
                    {"type": "string", "field": "language", "value": '"c++"'},
                ],
            ),
        ],
    )
    def test_complex_queries_and_mixed_content(self, query, expected):
        assert self.parser.parse(query) == expected

    @pytest.mark.parametrize("query", unknown_field_queries)
    def test_unknown_field_non_strict_drops_token(self, query):
        assert not self.parser.parse(query)

    @pytest.mark.parametrize("query", unknown_field_queries)
    def test_unknown_field_strict_raises(self, query):
        with pytest.raises(QueryParserError) as e:
            self.strict_parser.parse(query)

        assert e.value.error_type == "UNKNOWN_FIELD_ERROR"

    def test_date_format_validation(self):
        valid_dates = ["2023-12-31", '"2023-12-31"', '"2023-12-31', "20231231"]
        for date_str in valid_dates:
            assert self.parser.parse(f"created:{date_str}") == [
                {
                    "field": "created",
                    "op": "=",
                    "type": "date",
                    "value": "2023-12-31",
                }
            ]

        invalid_dates = ["invalid-date", "2023-163-01", "2023-01-362"]
        for inv_date_str in invalid_dates:
            with pytest.raises(QueryParserError) as e:
                self.strict_parser.parse(f"created:{inv_date_str}")

            assert e.value.error_type == "DATE_VALUE_ERROR"

        for inv_date_str in invalid_dates:
            assert not self.parser.parse(f"created:{inv_date_str}")

    def test_invalid_default_field_name(self):
        with pytest.raises(QueryParserError) as e:
            QueryParser(field_schema={"test": "string"}, default_field="Default")

        assert e.value.error_type == "FIELD_NAME_ERROR"

    def test_custom_default_field(self):
        parser_with_default = QueryParser(field_schema={"test": "string"}, default_field="default")
        result = parser_with_default.parse("query:test free_text")

        assert result == [
            {
                "field": "default",
                "type": "string",
                "value": "free_text",
            },
        ]

    @pytest.mark.parametrize(
        ("query"),
        ["author:", ":123", '"field: true"', "2341"],
    )
    def test_boundary_conditions(self, query):
        result = self.parser.parse(query)
        assert result == [
            {
                "field": "query",
                "type": "string",
                "value": query.strip('"'),
            }
        ]

    def test_long_field_names_and_values(self):
        long_field_parser = QueryParser(field_schema={"verylongfieldname": "string"})
        long_value = "a" * 1000

        assert long_field_parser.parse(f'verylongfieldname:"{long_value}"') == [
            {
                "field": "verylongfieldname",
                "type": "string",
                "value": f'"{long_value}"',
            }
        ]

    @pytest.mark.parametrize("val", ["0", "-1", "999999", "3.14159"])
    def test_numeric_values(self, val):
        assert self.parser.parse(f"stars:{val}") == [
            {
                "field": "stars",
                "op": ">" if float(val) < 0 else "=",
                "type": "number",
                "value": max(0, int(float(val))),
            }
        ]

    def test_overflow_numerical_value(self):
        overflow_number = "1e3000"
        with pytest.raises(QueryParserError) as e:
            self.strict_parser.parse(f"stars:{overflow_number}")

        assert e.value.error_type == "NUMBER_VALUE_ERROR"

    def test_quoted_multi_word_values(self):
        query = 'project:"OWASP Nest" author:"John Doe"'
        results = self.parser.parse(query)

        assert len(results) == 2
        assert results[0]["value"] == '"owasp nest"'
        assert results[1]["value"] == '"john doe"'

    def test_case_sensitivity_toggle(self):
        query = "Author:OWASP"
        cs_result = self.case_sensitive_parser.parse(query)
        assert cs_result[0]["value"] == "OWASP"
