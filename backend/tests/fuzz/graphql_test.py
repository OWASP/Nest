"""OWASP Nest GraphQL API fuzz tests."""

import logging
import os

import schemathesis

CSRF_TOKEN = os.getenv("CSRF_TOKEN")
BASE_URL = os.getenv("BASE_URL")
if not CSRF_TOKEN or not BASE_URL:
    message = "CSRF_TOKEN and BASE_URL must be set in the environment."
    raise OSError(message)

HEADERS = {
    "X-CSRFToken": CSRF_TOKEN,
    "Cookie": f"csrftoken={CSRF_TOKEN}",
}

logger = logging.getLogger(__name__)
schema = schemathesis.graphql.from_url(
    f"{BASE_URL}/graphql/",
    headers=HEADERS,
    timeout=30,
    wait_for_schema=10.0,
)


@schema.parametrize()
def test_graphql_api(case: schemathesis.Case) -> None:
    """Test GraphQL API endpoints."""
    logger.info(case.as_curl_command())
    case.call_and_validate(headers=HEADERS)
