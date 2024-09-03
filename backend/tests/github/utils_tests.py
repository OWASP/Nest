import pytest

from apps.github.utils import check_funding_policy_compliance


@pytest.mark.parametrize(
    ("platform", "target", "as_expected"),
    [
        # Compliant
        ("github", "owasp", True),
        ("github", "OWASP", True),
        ("custom", "https://owasp.org/donate", True),
        # Non-compliant
        ("custom", "https://my-site.com/donate", False),
        ("custom", "https://my-site.com/owasp/donate", False),
    ],
)
def test_check_funding_policy_compliance(platform, target, as_expected):
    assert check_funding_policy_compliance(platform, target) is as_expected
