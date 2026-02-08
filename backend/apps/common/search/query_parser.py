"""Query parser module for parsing search queries into structured conditions."""

import enum
from dataclasses import asdict, dataclass

from pyparsing import (
    Group,
    ParseException,
    QuotedString,
    Regex,
    Word,
    ZeroOrMore,
    alphanums,
    one_of,
)
from pyparsing import (
    Optional as PyparsingOptional,
)


class FieldType(enum.StrEnum):
    """Supported field types for query parsing."""

    BOOLEAN = "boolean"
    DATE = "date"
    NUMBER = "number"
    STRING = "string"


def has_enum_value(enum_class, value):
    """Check if a value exists in the given enum class."""
    try:
        enum_class(value)
    except ValueError:
        return False

    return True


@dataclass
class QueryCondition:
    """Dataclass representing a parsed query condition."""

    field: str
    type: str
    value: bool | int | str

    op: str | None = None

    def to_dict(self) -> dict:
        """Convert the QueryCondition to a dictionary representation."""
        data = asdict(self)
        if data.get("op") is None:
            data.pop("op")

        return data


class QueryParserError(Exception):
    """Exception for query parsing errors with context."""

    def __init__(
        self,
        message: str,
        error_type: str = "PARSE_ERROR",
        field: str = "",
        query: str = "",
    ):
        """Initialize QueryParserError.

        Args:
            message: Human-readable error message by the parser
            error_type: Category of error (PARSE_ERROR, FIELD_ERROR, VALUE_ERROR, etc.)
            field: Field name related to the error (if applicable)
            query: The original query string that caused the error (if applicable)

        """
        super().__init__(message)
        self.message = message

        self.error_type = error_type
        self.field = field
        self.query = query

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
            "error_type": self.error_type,
            "error": True,
            "field": self.field or "",
            "message": self.message,
            "query": self.query or "",
        }


class QueryParser:
    """QueryParser class for parsing search queries into structured conditions.

    Features:
        - Equality checks (field:value)
        - Numeric and date comparisons (>, <, >=, <=, =)
        - Quoted strings for multi-word values
        - Boolean field support
        - Date field parsing with comparisons
        - Case sensitivity: normalize field names only, preserve original value casing when
          case sensitive is True
        - Only supports implicit AND logic between conditions
    """

    # Grammar definitions (class-level constants).
    FIELD_NAME = Regex(r"[a-z0-9_]+")
    QUOTED_VALUE = QuotedString(quote_char='"', esc_char="\\", unquote_results=False)
    UNQUOTED_VALUE = Word(alphanums + '+-.<>=/_"')
    FIELD_VALUE = QUOTED_VALUE | UNQUOTED_VALUE
    COMPARISON_OPERATOR = PyparsingOptional(one_of(">= <= > < ="), default="=")
    COMPARISON_PATTERN = Group(COMPARISON_OPERATOR + UNQUOTED_VALUE)
    DATE_PATTERN = Regex(r"\d{4}-\d{2}-\d{2}") | Regex(r"\d{8}")  # YYYY-MM-DD or YYYYMMDD format.
    BOOLEAN_TRUE_VALUES = {"true", "1", "yes", "on"}
    BOOLEAN_FALSE_VALUES = {"false", "0", "no", "off"}

    def __init__(
        self,
        field_schema: dict[str, str],
        *,
        case_sensitive: bool = False,
        default_field: str = "query",
        strict: bool = False,
    ):
        """Initialize the query parser.

        Args:
            field_schema: Dictionary mapping field names to their types
                (e.g., {"stars": "number", "language": "string"}).
                Field names must be lowercase.
            default_field: Default field name for free text search
            case_sensitive: Controls value-case behavior for downstream search,
                field names are always normalized to lowercase.
            strict: If True, raises exception for unknown fields; if False, issues warnings

        """
        self.case_sensitive = case_sensitive
        self.default_field = default_field
        self.field_schema = self._validate_field_schema(field_schema, default_field)
        self.strict = strict

    def parse(self, query: str) -> list[dict]:
        """Parse query string into structured conditions.

        Args:
            query: Query string to parse

        Returns:
            List of dictionaries representing parsed conditions

        Raises:
            QueryParserError: If parsing fails

        """
        conditions: list[dict] = []
        query = query.strip()

        tokens = self._split_tokens(query)
        try:
            for token in tokens:
                if QueryParser._is_empty_string(token):
                    continue

                field, raw_value = self._parse_token(token)

                if not self.case_sensitive and raw_value:
                    raw_value = raw_value.lower()

                if field is None:
                    conditions.append(self._create_text_search_condition(raw_value))
                    continue

                normalized_field = field.lower()

                if normalized_field not in self.field_schema:
                    self._handle_unknown_field(normalized_field)
                    continue

                field_type = self.field_schema[normalized_field]
                condition = self.to_dict(normalized_field, field_type, raw_value)
                if condition:
                    conditions.append(condition)
        except QueryParserError as e:
            e.query = query
            raise

        return conditions

    def to_dict(self, field: str, field_type: FieldType, raw_value: str) -> dict | None:
        """Create a structured condition dictionary from field and raw value.

        Args:
            field: Field name
            field_type: FieldType of the condition
            raw_value: Raw string value to parse

        Returns:
            Dictionary representation of the condition or None if invalid

        Raises:
            QueryParserError: If parsing fails and strict mode is enabled

        """
        op_field = None
        value_field: str | int | bool = ""

        try:
            match field_type:
                case FieldType.BOOLEAN:
                    value_field = self._parse_boolean_value(raw_value)
                case FieldType.NUMBER:
                    operator, numeric_value = self._parse_number_value(raw_value)
                    op_field = operator
                    value_field = numeric_value
                case FieldType.DATE:
                    operator, date_value = self._parse_date_value(raw_value)
                    op_field = operator
                    value_field = date_value
                case FieldType.STRING:
                    value_field = self._parse_string_value(raw_value)
        except QueryParserError as e:
            if self.strict:
                e.field = field
                raise
            return None

        return QueryCondition(
            field=field,
            op=op_field,
            type=field_type.value,
            value=value_field,
        ).to_dict()

    def _create_text_search_condition(self, token: str) -> dict:
        """Create a text search condition for tokens that aren't field:value pairs.

        Args:
            token: Raw token string

        Returns:
            QueryCondition dictionary for text search

        """
        return QueryCondition(
            field=self.default_field,
            type=FieldType.STRING.value,
            value=QueryParser._remove_quotes(token),
        ).to_dict()

    def _handle_unknown_field(self, field: str) -> None:
        """Handle unknown field based on strict mode setting.

        Args:
            field: Unknown field name

        Raises:
            QueryParserError: If in strict mode

        """
        if self.strict:
            raise QueryParserError(
                message="Unknown field",
                error_type="UNKNOWN_FIELD_ERROR",
                field=field,
            )

    @staticmethod
    def _is_field_name(field_name: str) -> bool:
        """Check if a field name is valid."""
        try:
            QueryParser.FIELD_NAME.parse_string(field_name, parse_all=True)
        except ParseException:
            return False

        return True

    @staticmethod
    def _is_empty_string(token: str) -> bool:
        """Check if a token is empty or contains only whitespace/quotes."""
        return not token.strip().strip('"').strip()

    @staticmethod
    def _raise_invalid_field_name(field: str) -> None:
        """Raise an error for invalid field names."""
        msg = "Field name must be lowercase alphanumeric (letters, numbers, underscores only)"
        raise QueryParserError(message=msg, error_type="FIELD_NAME_ERROR", field=field)

    @staticmethod
    def _raise_invalid_field_type(field: str, field_type: str) -> None:
        """Raise an error for invalid field types."""
        msg = f"Invalid field type: '{field_type}'"
        raise QueryParserError(message=msg, error_type="FIELD_TYPE_ERROR", field=field)

    @staticmethod
    def _validate_field_schema(
        field_schema: dict[str, str], default_field: str
    ) -> dict[str, FieldType]:
        """Validate field schema and convert string field types to FieldType enums.

        Args:
            field_schema: Raw field type mapping with string values
            default_field: Default field name for free text search

        Returns:
            Validated field type mapping with string types converted to FieldType enum values

        Raises:
            QueryParserError: If field names are invalid or field types are not supported

        """
        if not QueryParser._is_field_name(default_field):
            QueryParser._raise_invalid_field_name(default_field)

        validated_fields = {}
        for field, field_type in field_schema.items():
            if not has_enum_value(FieldType, field_type):
                QueryParser._raise_invalid_field_type(field, field_type)
            if not QueryParser._is_field_name(field):
                QueryParser._raise_invalid_field_name(field)
            validated_fields[field] = FieldType(field_type)

        # Ensure default_field is a string.
        if (
            default_field in validated_fields
            and validated_fields[default_field] is not FieldType.STRING
        ):
            raise QueryParserError(
                error_type="CONFIGURATION_ERROR",
                field=default_field,
                message="default_field must be of type 'string'",
            )
        validated_fields[default_field] = FieldType.STRING

        return validated_fields

    @staticmethod
    def _split_tokens(query: str) -> list[str]:
        """Split query string into individual tokens, respecting quoted strings.

        Args:
            query: Raw query string

        Returns:
            List of individual tokens

        Raises:
            QueryParserError: If tokenization fails

        """
        regex_components = {
            # Key-value pairs with quoted values: name:"OWASP"
            "key_value_quoted": r'[a-zA-Z0-9_]+:"([^"\\]|\\.)*"',
            # Standard key-value pairs: stars:>10
            "key_value_plain": r"[a-zA-Z0-9_]+:\S+",
            # Standalone quoted strings: "OWASP Foundation"
            "quoted_string": r'"([^"\\]|\\.)*"',
            # Single words
            "unquoted_word": r"\S+",
        }

        parser = ZeroOrMore(Regex("|".join(regex_components.values())))
        try:
            result = parser.parse_string(query, parse_all=True)
        except ParseException as e:
            raise QueryParserError(
                message=f"Failed to tokenize query: {e!s}",
                error_type="TOKENIZATION_ERROR",
                query=query,
            ) from e

        return result.asList()

    @staticmethod
    def _parse_token(token: str) -> tuple[str | None, str]:
        """Parse a single token into field name and value.

        Args:
            token: Individual token string (e.g., "field:value").

        Returns:
            Tuple of (field_name, raw_value) or returns (None, token)
            if token is not a field:value pattern.

        """
        token = token.strip()
        if token[0] == '"':
            return None, token
        if token.count(":") == 0:
            return None, token

        field, value = token.split(":", 1)
        field = field.strip().lower()
        value = value.strip()

        return (
            (None, token)
            if QueryParser._is_empty_string(field) or QueryParser._is_empty_string(value)
            else (field, value)
        )

    @staticmethod
    def _remove_quotes(value: str) -> str:
        """Remove surrounding quotes from a string.

        Args:
            value: Input string

        Returns:
            String without surrounding quotes

        """
        return value.strip().strip('"')

    @staticmethod
    def _normalize_date(value: str) -> str:
        """Normalize the date string to YYYY-MM-DD format.

        Args:
            value: Raw date string

        Returns:
            Normalized date string

        """
        return value if "-" in value else f"{value[:4]}-{value[4:6]}-{value[6:]}"

    @staticmethod
    def _parse_comparison_pattern(value: str) -> tuple[str, str]:
        """Parse comparison operator and value from a string.

        Args:
            value: Value string potentially containing comparison operator

        Returns:
            Tuple of (operator, clean_value), "=" is the default operator when none is specified

        Raises:
            QueryParserError: If the comparison pattern is invalid

        """
        try:
            match = QueryParser.COMPARISON_PATTERN.parse_string(
                QueryParser._remove_quotes(value), parse_all=True
            )
        except ParseException as e:
            raise QueryParserError(
                message=f"Invalid comparison pattern in value: {e!s}",
                error_type="COMPARISON_ERROR",
            ) from e

        return match[0][0], match[0][1]

    @staticmethod
    def _parse_string_value(value: str) -> str:
        """Process string values by validating their format.

        Args:
            value: Raw string value

        Returns:
            Cleaned and validated string value

        Raises:
            QueryParserError: If string parsing fails

        """
        try:
            return QueryParser.FIELD_VALUE.parse_string(value, parse_all=True)[0]
        except ParseException as e:
            raise QueryParserError(
                message=f"Invalid string value: {e!s}", error_type="STRING_VALUE_ERROR"
            ) from e

    @staticmethod
    def _parse_boolean_value(value: str) -> bool:
        """Parse boolean string to actual boolean.

        Args:
            value: Boolean string to parse

        Returns:
            Actual boolean value (True/False)

        Raises:
            QueryParserError: If value is not a valid boolean

        """
        value = QueryParser._remove_quotes(value).lower()

        if value in QueryParser.BOOLEAN_TRUE_VALUES:
            return True
        if value in QueryParser.BOOLEAN_FALSE_VALUES:
            return False

        raise QueryParserError(
            message=f"Invalid boolean value: {value}", error_type="BOOLEAN_VALUE_ERROR"
        )

    @staticmethod
    def _parse_number_value(value: str) -> tuple[str, int]:
        """Parse numeric value with optional comparison operator.

        Args:
            value: String value to parse

        Returns:
            Tuple of (operator, numeric_value) where numeric_value is integer,
            clamped to [0, 2^32] range and "=" is the default operator.

        Raises:
            QueryParserError: If value is not a valid number or int overflow occurs

        """
        try:
            operator, clean_value = QueryParser._parse_comparison_pattern(
                QueryParser._remove_quotes(value)
            )

            numeric_value = int(float(clean_value))
            if numeric_value > 2**32 or numeric_value < 0:
                operator = ">" if numeric_value < 0 else operator
                numeric_value = max(0, min(numeric_value, 2**32))
        except ValueError as e:
            raise QueryParserError(
                message=f"Invalid numeric value: {e!s}", error_type="NUMBER_VALUE_ERROR"
            ) from e
        except OverflowError as e:
            raise QueryParserError(
                message=f"Numeric value overflow: {e!s}", error_type="NUMBER_VALUE_ERROR"
            ) from e

        return operator, numeric_value

    @staticmethod
    def _parse_date_value(value: str) -> tuple[str, str]:
        """Parse date value with optional comparison operator.

        Args:
            value: String value to parse

        Returns:
            Tuple of (operator, date_string) where date_string
            format is "YYYY-MM-DD" and "=" is the default operator.

        Raises:
            QueryParserError: If value is not a valid date format

        """
        try:
            operator, clean_value = QueryParser._parse_comparison_pattern(
                QueryParser._remove_quotes(value)
            )
            result = QueryParser.DATE_PATTERN.parse_string(clean_value, parse_all=True)
        except ParseException as e:
            raise QueryParserError(
                message=f"Invalid date value: {e!s}", error_type="DATE_VALUE_ERROR"
            ) from e

        return operator, QueryParser._normalize_date(result[0])
