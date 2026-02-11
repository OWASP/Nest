from unittest.mock import MagicMock

import pytest
from requests.exceptions import RequestException

from apps.github.utils import (
    check_funding_policy_compliance,
    check_owasp_site_repository,
    get_repository_file_content,
    get_repository_path,
    normalize_url,
)


class TestUtils:
    @pytest.mark.parametrize(
        ("key", "as_expected"),
        [
            ("www-chapter-abc", True),
            ("www-committee-xyz", True),
            ("www-event-123", True),
            ("www-project-abc123", True),
            ("www-random-site", False),
            ("random-prefix", False),
        ],
    )
    def test_check_owasp_site_repository(self, key, as_expected):
        assert check_owasp_site_repository(key) is as_expected

    @pytest.mark.parametrize(
        ("platform", "target", "as_expected"),
        [
            ("custom", "https://domain.owasp.org/sponsorship/", True),
            ("custom", "https://owasp.org/donate", True),
            ("github", "owasp", True),
            ("github", "OWASP", True),
            ("patreon", "", True),
            ("patreon", None, True),
            ("custom", "https://my-site.com/donate", False),
            ("custom", "https://my-site.com/owasp/donate", False),
            ("patreon", "username", False),
        ],
    )
    def test_check_funding_policy_compliance(self, platform, target, as_expected):
        assert check_funding_policy_compliance(platform, target) is as_expected

    @pytest.mark.parametrize(
        ("url", "expected"),
        [
            ("github.com/user/repo", None),
        ],
    )
    def test_get_repository_path(self, url, expected):
        result = get_repository_path(url)
        assert result == expected

    def test_get_repository_file_content(self, mocker):
        url = "https://example.com/file.txt"
        content = "Hello, World!"
        response = MagicMock()
        response.text = content
        mocker.patch("requests.get", return_value=response)
        result = get_repository_file_content(url)
        assert result == content

    def test_get_repository_file_content_exception(self, mocker):
        url = "https://example.com/file.txt"
        mocker.patch("requests.get", side_effect=RequestException("Test exception"))
        result = get_repository_file_content(url)
        assert result == ""

    @pytest.mark.parametrize(
        ("url", "expected"),
        [
            ("example.com", None),
            ("invalid-url", None),
            ("https://example.com", "https://example.com"),
            ("https://example.com/path/", "https://example.com/path"),
            ("https://example.com/path#fragment", "https://example.com/path"),
            ("http://example.com", "https://example.com"),
            ("http://example.com/path", "https://example.com/path"),
        ],
    )
    def test_normalize_url(self, url, expected):
        result = normalize_url(url)
        assert result == expected
