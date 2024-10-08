import pytest

from apps.owasp.models.project import Project


class TestProjectModel:
    @pytest.mark.parametrize(
        ("url", "expected_url"),
        [
            ("https://github.com/owasp/repository", None),
            ("https://owasp.org/repository", None),
            ("https://github.com/owasp/code-repo", "https://github.com/owasp/code-repo"),
            ("https://github.com/username", "https://github.com/username"),
            ("https://github.com/OWASP/repo/tree/v1.0.0/1.0", "https://github.com/owasp/repo"),
        ],
    )
    def test_get_related_url(self, url, expected_url):
        project = Project()
        project.key = "repository"
        assert project.get_related_url(url) == expected_url
