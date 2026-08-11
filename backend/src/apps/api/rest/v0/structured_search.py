"""Structured query utilities for REST API endpoints."""

from typing import TypedDict

from django.db.models import Q

from apps.common.search.query_parser import (
    QueryParser,
    QueryParserError,
)


class FieldConfig(TypedDict, total=False):
    """Configuration for a searchable field in structured queries."""

    type: str
    field: str
    lookup: str


OPERATOR_MAPPING = {
    "=": "",
    ">": "__gt",
    "<": "__lt",
    ">=": "__gte",
    "<=": "__lte",
}

STRING_LOOKUP_MAPPING = {
    "icontains": "__icontains",
    "exact": "",
}


def apply_structured_search(
    queryset,
    query: str | None,
    field_schema: dict[str, FieldConfig],
    *,
    string_lookup: str = "icontains",
):
    """Apply structured search filtering to a Django queryset.

    Args:
        queryset: Base queryset.
        query: Structured query string (e.g. "name:nest stars>100").
        field_schema: Allowed fields with their types.
        string_lookup: String matching strategy ("icontains", "exact").

    Returns:
        Filtered queryset.

    """
    if not query:
        return queryset

    parser_schema: dict[str, str] = {
        name: config.get("type", "") for name, config in field_schema.items()
    }

    try:
        parser = QueryParser(case_sensitive=True, field_schema=parser_schema, strict=False)
        conditions = parser.parse(query)
    except QueryParserError:
        # Fail safely
        return queryset

    q_object = Q()

    for condition in conditions:
        field = condition["field"]
        field_config: FieldConfig = field_schema.get(field, {})

        if field not in field_schema:
            continue

        db_field = field_config.get("field", field)
        field_type = field_config.get("type")
        value = condition["value"]
        operator = condition.get("op", "=")

        if field_type == "string":
            lookup_suffix = STRING_LOOKUP_MAPPING.get(
                field_config.get("lookup", string_lookup),
                "",
            )
        elif field_type == "number":
            lookup_suffix = OPERATOR_MAPPING.get(operator, "")
            try:
                value = int(value)
            except (ValueError, TypeError):
                continue
        else:
            lookup_suffix = ""

        lookup = f"{db_field}{lookup_suffix}"
        q_object &= Q(**{lookup: value})

    return queryset.filter(q_object)
