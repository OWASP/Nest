"""OWASP Nest REST API fuzz tests."""

import os

import schemathesis

CSRF_TOKEN = os.getenv("CSRF_TOKEN")
schema = schemathesis.openapi.from_url(
    f"{os.getenv('REST_URL')}/openapi.json",
    headers={"X-CSRFToken": CSRF_TOKEN, "Cookie": f"csrftoken={CSRF_TOKEN}"},
    timeout=30,
    wait_for_schema=10.0,
)


@schema.parametrize()
def test_rest_api(case):
    """Test REST API endpoints."""
    case.call_and_validate(
        headers={"X-CSRFToken": CSRF_TOKEN, "Cookie": f"csrftoken={CSRF_TOKEN}"}
    )
