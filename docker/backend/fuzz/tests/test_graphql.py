"""OWASP Nest GraphQL API fuzz tests."""

import logging
import os

import schemathesis

CSRF_TOKEN = os.getenv("CSRF_TOKEN")

logger = logging.getLogger(__name__)
schema = schemathesis.graphql.from_url(
    f"{os.getenv('BASE_URL')}/graphql/",
    headers={"X-CSRFToken": CSRF_TOKEN, "Cookie": f"csrftoken={CSRF_TOKEN}"},
    timeout=30,
    wait_for_schema=10.0,
)


@schema.parametrize()
def test_graphql_api(case: schemathesis.Case) -> None:
    """Test GraphQL API endpoints."""
    logger.info(case.as_curl_command())
    case.call_and_validate(
        headers={"X-CSRFToken": CSRF_TOKEN, "Cookie": f"csrftoken={CSRF_TOKEN}"}
    )
