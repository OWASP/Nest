"""Fuzz target for apps.common.search.query_parser."""

import contextlib
import sys

import atheris

with atheris.instrument_imports():
    from apps.common.search.query_parser import QueryParser, QueryParserError

FIELD_SCHEMA = {
    "query": "string",
    "language": "string",
    "stars": "number",
    "created": "date",
    "archived": "boolean",
}
FIELDS = list(FIELD_SCHEMA.keys())


def test_one_input(data: bytes) -> None:
    """Fuzz QueryParser with arbitrary and structured input."""
    parser = QueryParser(field_schema=FIELD_SCHEMA, case_sensitive=False, strict=False)
    with contextlib.suppress(QueryParserError):
        parser.parse(data.decode("utf-8", errors="surrogateescape"))

    fdp = atheris.FuzzedDataProvider(data)
    parser = QueryParser(
        field_schema=FIELD_SCHEMA,
        case_sensitive=fdp.ConsumeBool(),
        strict=fdp.ConsumeBool(),
    )
    if fdp.ConsumeBool():
        query = fdp.ConsumeUnicodeNoSurrogates(512)
    else:
        field = fdp.PickValueInList(FIELDS)
        value = fdp.ConsumeUnicodeNoSurrogates(128)
        query = f"{field}:{value}"

    with contextlib.suppress(QueryParserError):
        parser.parse(query)


def main() -> None:
    """Run the Atheris fuzz target."""
    atheris.Setup(sys.argv, atheris.instrument_func(test_one_input))
    atheris.Fuzz()


if __name__ == "__main__":
    main()
