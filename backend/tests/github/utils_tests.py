import pytest

from apps.github.utils import check_funding_policy_compliance


class TestUtils:
    @pytest.mark.parametrize(
        ("platform", "target", "as_expected"),
        [
            # Compliant
            ("custom", "https://domain.owasp.org/sponsorship/", True),
            ("custom", "https://owasp.org/donate", True),
            ("github", "owasp", True),
            ("github", "OWASP", True),
            ("patreon", "", True),
            ("patreon", None, True),
            # Non-compliant
            ("custom", "https://my-site.com/donate", False),
            ("custom", "https://my-site.com/owasp/donate", False),
            ("patreon", "username", False),
        ],
    )
    def test_check_funding_policy_compliance(self, platform, target, as_expected):
        assert check_funding_policy_compliance(platform, target) is as_expected
