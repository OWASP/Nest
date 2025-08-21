"""Query parser module for parsing search queries into structured conditions."""

from enum import Enum

from pyparsing import (
    Combine,
    Group,
    ParseException,
    QuotedString,
    Regex,
    Suppress,
    Word,
    ZeroOrMore,
    alphanums,
    alphas,
)


class FieldType(Enum):
    """Supported field types for query parsing."""

    STRING = "string"
    NUMBER = "number"
    DATE = "date"
    BOOLEAN = "boolean"


class QueryParserError(Exception):
    """Exception for query parsing errors with context."""

    def __init__(
        self,
        message: str,
        error_type: str = "PARSE_ERROR",
        query: str = "<query>",
        field: str = "<field>",
    ):
        """Initialize QueryParserError.

        Args:
            message: Human-readable error message
            error_type: Category of error (PARSE_ERROR, FIELD_ERROR, VALUE_ERROR, etc.)
            query: The original query string that caused the error
            field: Field name related to the error (if applicable)

        """
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.query = query
        self.field = field

    def __str__(self) -> str:
        """Return formatted error message with context."""
        parts = [f"[{self.error_type}] {self.message}"]

        if self.query:
            parts.append(f"Query: '{self.query}'")

        if self.field:
            parts.append(f"Field: '{self.field}'")

        return "\n".join(parts)

    def to_dict(self) -> dict:
        """Return error information as dictionary for API responses."""
        return {
            "error": True,
            "error_type": self.error_type,
            "message": self.message,
            "query": self.query,
            "field": self.field,
        }


class QueryParser:
    """QueryParser class for parsing search queries into structured conditions.

    Features:
    - Equality checks (field:value)
    - Numeric comparisons (>, <, >=, <=, =)
    - Quoted strings for multi-word values
    - Boolean field support
    - Date field parsing with comparisons
    - Only support implicit AND logic between conditions
    - Handle case sensitivity/insensitivity values
    """

    # Grammar definitions (class-level constants)
    _FIELD_NAME = Word(alphas, alphanums + "_")
    _QUOTED_VALUE = QuotedString('"', escChar="\\")
    _UNQUOTED_VALUE = Word(alphanums + "+-.<>=/_")
    _FIELD_VALUE = _QUOTED_VALUE | _UNQUOTED_VALUE
    _TOKEN_PATTERN = Group(_FIELD_NAME + Suppress(":") + _FIELD_VALUE)
    _COMP_OPERATOR = Combine(
        Regex(r"^(>=|<=|>|<|=)?")
    )  # valid operator {"=", ">", "<", ">=", "<="}
    _COMP_PATTERN = Group(_COMP_OPERATOR + _UNQUOTED_VALUE)
    _UNQUOTED_STRING = Word(alphanums + "+-.<>=/ ")
    _DATE_PATTERN = Regex(r"\d{4}-\d{2}-\d{2}")  # YYYY-MM-DD format

    _BOOLEAN_TRUE_VALUES = {"true", "1", "yes", "on"}
    _BOOLEAN_FALSE_VALUES = {"false", "0", "no", "off"}

    def __init__(
        self,
        allowed_fields: dict[str, str],
        default_field: str = "query",
        *,
        case_sensitive: bool = False,
        strict: bool = False,
    ):
        """Initialize the query parser.

        Args:
            allowed_fields: Dictionary mapping field names to their types
                           (e.g., {"stars": "number", "language": "string"})
            default_field: Default field name for free text search
            case_sensitive: If True, field names are case-sensitive
            strict: If True, raises exception for unknown fields; if False, issues warnings

        Raises:
            QueryParserError: If allowed_fields contains invalid field types

        """
        try:
            self.allowed_fields = self._validate_allowed_fields(allowed_fields, default_field)
            self.default_field = default_field
            self.case_sensitive = case_sensitive
            self.strict = strict
        except QueryParserError:
            raise
        except Exception as e:
            raise QueryParserError(
                message=f"Invalid query parser configuration: {e!s}",
                error_type="CONFIGURATION_ERROR",
            ) from e

    @staticmethod
    def _raise_invalid_field_name(field: str) -> None:
        msg = f"Field name '{field}' must be alphanumeric (letters, numbers, underscores only)"
        raise QueryParserError(message=msg, error_type="FIELD_NAME_ERROR", field=field)

    @staticmethod
    def _raise_invalid_field_type(field: str, field_type: str) -> None:
        msg = f"Invalid field type '{field_type}' for field '{field}'"
        raise QueryParserError(message=msg, error_type="FIELD_TYPE_ERROR", field=field)

    @staticmethod
    def _validate_allowed_fields(
        allowed_fields: dict[str, str], default_field: str
    ) -> dict[str, FieldType]:
        """Validate and convert allowed_fields to use FieldType enum.

        Args:
            allowed_fields: Raw field type mapping
            default_field: Default field name for free text search

        Returns:
            Validated field type mapping using FieldType enum

        Raises:
            QueryParserError: If field type is not supported

        """
        if not QueryParser._FIELD_NAME.parseString(default_field, parseAll=True):
            QueryParser._raise_invalid_field_name(default_field)
        validated_fields = {}

        for field, field_type in allowed_fields.items():
            if not QueryParser._FIELD_NAME.parseString(field, parseAll=True):
                QueryParser._raise_invalid_field_name(field)
            if field_type not in FieldType._value2member_map_:
                QueryParser._raise_invalid_field_type(field, field_type)
            validated_fields[field] = FieldType(field_type)

        validated_fields[default_field] = FieldType.STRING
        return validated_fields

    @staticmethod
    def _split_tokens(query: str) -> list[str]:
        """Split query string into individual tokens, respecting quoted strings.

        Args:
            query: Raw query string

        Returns:
            List of individual tokens

        """
        reg_components = {
            "key_value": r'\S+:"[^"]*"',
            "quoted_string": r'"[^"]*"',
            "unquoted_word": r"\S+",
        }

        reg = [
            reg_components["key_value"],
            reg_components["quoted_string"],
            reg_components["unquoted_word"],
        ]

        token_regex = "|".join(reg)
        parser = ZeroOrMore(Regex(token_regex))

        try:
            result = parser.parseString(query, parseAll=True)
            return result.asList()
        except ParseException as e:
            raise QueryParserError(
                message="Failed to tokenize query", error_type="TOKENIZATION_ERROR", query=query
            ) from e

    @staticmethod
    def _parse_token(token: str) -> tuple[str | None, str]:
        """Parse a single token into field name and value.

        Args:
            token: Individual token string (e.g., "field:value") raise exception if null

        Returns:
            Tuple of (field_name, raw_value) or (None, token) if parsing fails

        """
        try:
            result = QueryParser._TOKEN_PATTERN.parseString(token, parseAll=True)
            return result[0][0], result[0][1]
        except ParseException:
            if token.startswith('"') and token.endswith('"'):
                token = token[1:-1]
            return None, token

    @staticmethod
    def _parse_comparison_pattern(value: str) -> tuple[str, str]:
        """Parse comparison operator and value from a string.

        Args:
            value: Value string potentially containing comparison operator

        Returns:
            Tuple of (operator, clean_value), if operator is none then (None, clean_value)

        Raises:
            QueryParserError: If the comparison pattern is invalid

        """
        try:
            match = QueryParser._COMP_PATTERN.parseString(value, parseAll=True)
            if match[0][0] is None:
                return "=", match[0][1]
            return match[0][0], match[0][1]
        except ParseException as e:
            raise QueryParserError(
                message="Invalid comparison pattern in value", error_type="COMPARISON_ERROR"
            ) from e

    @staticmethod
    def _parse_string_value(field: str, value: str) -> str:
        """Parse and validate string value.

        Args:
            field: Field name
            value: Raw string value

        Returns:
            Cleaned string value

        Raises:
            QueryParserError: If string parsing fails

        """
        try:
            result = QueryParser._UNQUOTED_STRING.parseString(value)
            return result[0]
        except ParseException as e:
            raise QueryParserError(
                message="Invalid string value", error_type="STRING_VALUE_ERROR", field=field
            ) from e

    @staticmethod
    def _parse_boolean_value(field: str, value: str) -> str:
        """Parse boolean value from string.

        Args:
            field: Field name
            value: String value to parse

        Returns:
            Boolean value

        Raises:
            QueryParserError: If value is not a valid boolean

        """
        if value.lower() in QueryParser._BOOLEAN_TRUE_VALUES:
            return "True"
        if value.lower() in QueryParser._BOOLEAN_FALSE_VALUES:
            return "False"

        raise QueryParserError(
            message=f"Invalid boolean value '{value}'",
            error_type="BOOLEAN_VALUE_ERROR",
            field=field,
        )

    @staticmethod
    def _parse_number_value(field: str, value: str) -> tuple[str, int]:
        """Parse numeric value with optional comparison operator.

        Args:
            field: Field name (for error messages)
            value: String value to parse

        Returns:
            Tuple of (operator, numeric_value)

        Raises:
            QueryParserError: If value is not a valid number

        """
        try:
            operator, clean_value = QueryParser._parse_comparison_pattern(value)
            numeric_value = int(float(clean_value))

        except ValueError as e:
            raise QueryParserError(
                message=f"Invalid numeric value '{value}'",
                error_type="NUMBER_VALUE_ERROR",
                field=field,
            ) from e

        return operator, numeric_value

    @staticmethod
    def _parse_date_value(field: str, value: str) -> tuple[str, str]:
        """Parse date value with optional comparison operator.

        Args:
            field: Field name
            value: String value to parse

        Returns:
            Tuple of (operator, date_string)

        Raises:
            QueryParserError: If value is not a valid date format

        """
        try:
            operator, clean_value = QueryParser._parse_comparison_pattern(value)
            result = QueryParser._DATE_PATTERN.parseString(clean_value, parseAll=True)
            return operator, result[0]

        except (ValueError, ParseException, QueryParserError) as e:
            raise QueryParserError(
                message=f"Invalid date value '{value}'", error_type="DATE_VALUE_ERROR", field=field
            ) from e

    def to_dict(self, field: str, field_type: FieldType, raw_value: str) -> dict[str, str]:
        """Convert condition to dictionary format.

        Args:
            field: Field name
            field_type: FieldType of the condition
            raw_value: Raw string value to parse

        Returns:
            Dictionary representation of the condition

        Raises:
            QueryParserError: If parsing fails

        """
        condition_dict = {
            "type": field_type.value,
            "field": field,
        }
        if field_type == FieldType.BOOLEAN:
            condition_dict["boolean"] = self._parse_boolean_value(field, raw_value)
        elif field_type == FieldType.NUMBER:
            operator, numeric_value = self._parse_number_value(field, raw_value)
            condition_dict["op"] = operator
            condition_dict["number"] = str(numeric_value)
        elif field_type == FieldType.DATE:
            operator, date_value = self._parse_date_value(field, raw_value)
            condition_dict["op"] = operator
            condition_dict["date"] = date_value
        else:  # STRING
            condition_dict["string"] = self._parse_string_value(field, raw_value)

        return condition_dict

    def _create_text_search_condition(self, token: str) -> dict[str, str]:
        """Create a text search condition for tokens that aren't field:value pairs.

        Args:
            token: Raw token string

        Returns:
            QueryCondition for text search

        """
        return {"type": FieldType.STRING.value, "field": self.default_field, "string": token}

    def _handle_unknown_field(self, field: str) -> None:
        """Handle unknown field based on strict mode setting.

        Args:
            field: Unknown field name

        Raises:
            QueryParserError: If in strict mode

        """
        if self.strict:
            raise QueryParserError(
                message=f"Unknown field '{field}'",
                error_type="UNKNOWN_FIELD_ERROR",
                field=field,
            )

    def parse(self, query: str) -> list[dict[str, str]]:
        """Parse query string into structured conditions.

        Args:
            query: Query string to parse

        Returns:
            List of dictionaries representing parsed conditions

        Raises:
            QueryParserError: If parsing fails

        """
        conditions = []
        try:
            if not self.case_sensitive:
                query = query.lower().strip()
            tokens = self._split_tokens(query)
            for token in tokens:
                if not token or token.strip() == "":
                    continue
                field, raw_value = self._parse_token(token)
                if raw_value is None or raw_value.strip() == "":
                    continue

                if field is None:
                    conditions.append(self._create_text_search_condition(raw_value))
                    continue

                field = field.lower()  # field name normalization

                if field not in self.allowed_fields:
                    self._handle_unknown_field(field)
                    continue

                field_type = self.allowed_fields[field]
                condition_dict = self.to_dict(field, field_type, raw_value)
                conditions.append(condition_dict)
        except QueryParserError:
            raise
        except Exception as e:
            raise QueryParserError(
                message=f"Unexpected error during parsing: {e!s}",
                error_type="INTERNAL_ERROR",
                query=query,
            ) from e

        return conditions
