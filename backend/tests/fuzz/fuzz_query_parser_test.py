"""OWASP Nest QueryParser fuzz target for ClusterFuzzLite."""

import sys

import atheris

with atheris.instrument_imports():
    from apps.common.search.query_parser import QueryParser, QueryParserError

# Representative production-like schema exercising multiple field types.
FIELD_SCHEMA = {
    "query": "string",
    "language": "string",
    "stars": "number",
    "created": "date",
    "archived": "boolean",
}

FIELDS = list(FIELD_SCHEMA.keys())


def TestOneInput(data: bytes) -> None:
    """Fuzz QueryParser with arbitrary and structured Unicode input."""
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

    try:
        parser.parse(query)
    except QueryParserError:
        # Invalid queries are expected during fuzzing.
        pass


def main() -> None:
    """Run the Atheris fuzz target."""
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
