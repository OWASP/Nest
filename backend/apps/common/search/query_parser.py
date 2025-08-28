"""Query parser module for parsing search queries into structured conditions."""

from enum import Enum

from pyparsing import (
    Group,
    Optional,
    ParseException,
    QuotedString,
    Regex,
    Word,
    ZeroOrMore,
    alphanums,
    alphas,
    oneOf,
)


class FieldType(str, Enum):
    """Supported field types for query parsing."""

    STRING = "string"
    NUMBER = "number"
    DATE = "date"
    BOOLEAN = "boolean"


def has_enum_value(enum_class, value):
    """Check if a value exists in the given enum class.

    Args:
        enum_class: The enum class to check against.
        value: The value to check for existence in the enum.

    Returns:
        bool: True if the value exists in the enum, False otherwise.

    Raises:
        None: This function catches ValueError internally and returns False.

    """
    try:
        enum_class(value)
    except ValueError:
        return False
    else:
        return True


class QueryParserError(Exception):
    """Exception for query parsing errors with context."""

    def __init__(
        self,
        message: str,
        error_type: str = "PARSE_ERROR",
        query: str = "",
        field: str = "",
    ):
        """Initialize QueryParserError.

        Args:
            message: Human-readable error message by the parser
            error_type: Category of error (PARSE_ERROR, FIELD_ERROR, VALUE_ERROR, etc.)
            query: The original query string that caused the error (if applicable)
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

    def to_response(self) -> dict:
        """Return error information as dictionary for API responses."""
        return {
            "error": True,
            "error_type": self.error_type,
            "message": self.message,
            "query": self.query or "",
            "field": self.field or "",
        }


class QueryParser:
    """QueryParser class for parsing search queries into structured conditions.

    Features:
    - Equality checks (field:value)
    - Numeric and date comparisons (>, <, >=, <=, =)
    - Quoted strings for multi-word values
    - Boolean field support
    - Date field parsing with comparisons
    - Handle case sensitivity/insensitivity values
    - Only supports implicit AND logic between conditions
    """

    # Grammar definitions (class-level constants)
    _FIELD_NAME = Word(alphas, alphanums + "_")
    _QUOTED_VALUE = QuotedString(quoteChar='"', escChar="\\", unquoteResults=False)
    _UNQUOTED_VALUE = Word(alphanums + '+-.<>=/_"')
    _FIELD_VALUE = _QUOTED_VALUE | _UNQUOTED_VALUE
    _COMPARISON_OPERATORS = {">", "<", ">=", "<=", "="}
    _COMPARISON_OPERATOR = Optional(oneOf(_COMPARISON_OPERATORS), default="=")
    _COMPARISON_PATTERN = Group(_COMPARISON_OPERATOR + _UNQUOTED_VALUE)
    _DATE_PATTERN = Regex(r"\d{4}-\d{2}-\d{2}") | Regex(r"\d{8}")  # YYYY-MM-DD or YYYYMMDD format
    _BOOLEAN_TRUE_VALUES = {"true", "1", "yes", "on"}
    _BOOLEAN_FALSE_VALUES = {"false", "0", "no", "off"}

    def __init__(
        self,
        field_schema: dict[str, str],
        default_field: str = "query",
        *,
        case_sensitive: bool = False,
        strict: bool = False,
    ):
        """Initialize the query parser.

        Args:
            field_schema: Dictionary mapping field names to their types
                         (e.g., {"stars": "number", "language": "string"}).
                         Field names must be lowercase.
            default_field: Default field name for free text search
            case_sensitive: If True, field names are case-sensitive
            strict: If True, raises exception for unknown fields; if False, issues warnings

        Raises:
            QueryParserError: If field_schema contains invalid field names or types

        """
        try:
            self.field_schema = self._validate_field_schema(field_schema, default_field)
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
        query = query.strip()
        if not self.case_sensitive:
            query = query.lower()
        tokens = self._split_tokens(query)
        try:
            for token in tokens:
                if QueryParser._is_empty_string(token):
                    continue
                field, raw_value = self._parse_token(token)

                if field is None:
                    conditions.append(self._create_text_search_condition(raw_value))
                    continue

                if field not in self.field_schema:
                    self._handle_unknown_field(field)
                    continue

                field_type = self.field_schema[field]
                condition = self.create_condition(field, field_type, raw_value)
                if condition:
                    conditions.append(condition)
        except QueryParserError as e:
            e.query = query
            raise
        else:
            return conditions

    def create_condition(
        self, field: str, field_type: FieldType, raw_value: str
    ) -> dict[str, str] | None:
        """Create a structured condition dictionary from field and raw value.

        Args:
            field: Field name
            field_type: FieldType of the condition
            raw_value: Raw string value to parse

        Returns:
            Dictionary representation of the condition

        Raises:
            QueryParserError: If parsing fails

        """
        condition = {
            "type": field_type.value,
            "field": field,
        }
        try:
            match field_type:
                case FieldType.BOOLEAN:
                    condition["boolean"] = self._parse_boolean_value(
                        raw_value
                    )  # "True" or "False"
                case FieldType.NUMBER:
                    operator, numeric_value = self._parse_number_value(raw_value)
                    condition["op"] = operator
                    condition["number"] = numeric_value
                case FieldType.DATE:
                    operator, date_value = self._parse_date_value(raw_value)
                    condition["op"] = operator
                    condition["date"] = date_value
                case FieldType.STRING:
                    condition["string"] = self._parse_string_value(raw_value)
        except QueryParserError as e:
            if self.strict:
                e.field = field
                raise
            return None
        else:
            return condition

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
                message="Unknown field",
                error_type="UNKNOWN_FIELD_ERROR",
                field=field,
            )

    @staticmethod
    def _is_field_name(field_name: str) -> bool:
        """Check if a field name is valid."""
        try:
            QueryParser._FIELD_NAME.parseString(field_name, parseAll=True)
        except ParseException:
            return False
        return field_name.islower()

    @staticmethod
    def _is_empty_string(token: str) -> bool:
        """Check if a token is empty or contains only whitespace/quotes."""
        return token.strip().strip('"').strip() == ""

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
                message=f"Failed to tokenize query: {e!s}",
                error_type="TOKENIZATION_ERROR",
                query=query,
            ) from e

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
        if QueryParser._is_empty_string(field) or QueryParser._is_empty_string(value):
            return None, token
        return field, value

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
    def _normalize_date(date: str) -> str:
        """Normalize the date string to YYYY-MM-DD format.

        Args:
            date: Raw date string

        Returns:
            Normalized date string

        """
        if "-" not in date:
            return f"{date[:4]}-{date[4:6]}-{date[6:]}"
        return date

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
            value = QueryParser._remove_quotes(value)
            match = QueryParser._COMPARISON_PATTERN.parseString(value, parseAll=True)
            return match[0][0], match[0][1]
        except (ValueError, ParseException) as e:
            raise QueryParserError(
                message=f"Invalid comparison pattern in value: {e!s}",
                error_type="COMPARISON_ERROR",
            ) from e

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
            result = QueryParser._FIELD_VALUE.parseString(value, parseAll=True)
            return result[0]
        except (ValueError, ParseException) as e:
            raise QueryParserError(
                message=f"Invalid string value: {e!s}", error_type="STRING_VALUE_ERROR"
            ) from e

    @staticmethod
    def _parse_boolean_value(value: str) -> str:
        """Parse boolean value from string and return its string representation.

        Args:
            value: String value to parse

        Returns:
            String ("True" or "False") based on the boolean input value.

        Raises:
            QueryParserError: If value is not a valid boolean

        """
        value = QueryParser._remove_quotes(value).lower()
        if value in QueryParser._BOOLEAN_TRUE_VALUES:
            return "True"
        if value in QueryParser._BOOLEAN_FALSE_VALUES:
            return "False"
        raise QueryParserError(
            message=f"Invalid boolean value: {value}", error_type="BOOLEAN_VALUE_ERROR"
        )

    @staticmethod
    def _parse_number_value(value: str) -> tuple[str, str]:
        """Parse numeric value with optional comparison operator.

        Args:
            value: String value to parse

        Returns:
            Tuple of (operator, numeric_value) where numeric_value is string
            of integer representation and "=" is the default operator.

        Raises:
            QueryParserError: If value is not a valid number

        """
        try:
            value = QueryParser._remove_quotes(value)
            operator, clean_value = QueryParser._parse_comparison_pattern(value)
            numeric_value = int(float(clean_value))
            return operator, str(numeric_value)
        except QueryParserError:
            raise
        except (ValueError, ParseException) as e:
            raise QueryParserError(
                message=f"Invalid numeric value: {e!s}", error_type="NUMBER_VALUE_ERROR"
            ) from e

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
            value = QueryParser._remove_quotes(value)
            operator, clean_value = QueryParser._parse_comparison_pattern(value)
            result = QueryParser._DATE_PATTERN.parseString(clean_value, parseAll=True)
            result[0] = QueryParser._normalize_date(result[0])
            return operator, result[0]
        except QueryParserError:
            raise
        except (ValueError, ParseException) as e:
            raise QueryParserError(
                message=f"Invalid date value: {e!s}", error_type="DATE_VALUE_ERROR"
            ) from e
