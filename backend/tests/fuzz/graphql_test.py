"""OWASP Nest GraphQL API fuzz tests."""

import logging
import os
from contextlib import suppress

import schemathesis
from schemathesis.graphql.checks import GraphQLClientError

if not (BASE_URL := os.getenv("BASE_URL")) or not (CSRF_TOKEN := os.getenv("CSRF_TOKEN")):
    message = "BASE_URL and CSRF_TOKEN must be set in the environment."
    raise ValueError(message)

HEADERS = {
    "Cookie": f"csrftoken={CSRF_TOKEN}",
    "X-CSRFToken": CSRF_TOKEN,
}

logger = logging.getLogger(__name__)
schema = schemathesis.graphql.from_url(
    f"{BASE_URL}/graphql/",
    headers=HEADERS,
    timeout=30,
    wait_for_schema=10,
)


@schema.parametrize()
def test_graphql_api(case: schemathesis.Case) -> None:
    """Test GraphQL API endpoints."""
    logger.info(case.as_curl_command())
    with suppress(GraphQLClientError):
        case.call_and_validate(headers=HEADERS)
