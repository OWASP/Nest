import pytest

from apps.owasp.models.common import OwaspEntity


class TestOwaspEntity:
    @pytest.mark.parametrize(
        ("url", "expected_url"),
        [
            ("https://github.com/owasp/repository", None),
            ("https://owasp.org/owasp/repository", None),
            ("https://github.com/owasp/code-repo", "https://github.com/owasp/code-repo"),
            ("https://github.com/username", "https://github.com/username"),
            ("https://github.com/OWASP/repo/tree/v1.0.0/1.0", "https://github.com/owasp/repo"),
        ],
    )
    def test_get_related_repository_url(self, url, expected_url):
        entity = OwaspEntity()
        entity.key = "repository"
        assert entity.get_related_url(url) == expected_url
