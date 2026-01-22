"""Structured query utilities for REST API endpoints."""

from django.db.models import Q

from apps.common.search.query_parser import (
    FieldType,
    QueryParser,
    QueryParserError,
)

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
    field_schema: dict[str, str],
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

    try:
        parser = QueryParser(field_schema=field_schema, strict=False)
        conditions = parser.parse(query)
    except QueryParserError:
        # Fail safely
        return queryset

    q_object = Q()

    for condition in conditions:
        field = condition["field"]
        value = condition["value"]
        field_type = condition["type"]
        operator = condition.get("op", "=")

        if field not in field_schema:
            continue

        if field_type == FieldType.STRING.value:
            lookup_suffix = STRING_LOOKUP_MAPPING.get(string_lookup, "")
        elif field_type in (FieldType.NUMBER.value, FieldType.DATE.value):
            lookup_suffix = OPERATOR_MAPPING.get(operator, "")
        else:
            lookup_suffix = ""

        lookup = f"{field}{lookup_suffix}"
        q_object &= Q(**{lookup: value})

    return queryset.filter(q_object)
