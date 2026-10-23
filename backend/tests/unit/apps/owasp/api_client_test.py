"""Tests for the public OWASP website API client."""

from http import HTTPStatus
from unittest import mock

import pytest
import requests

from apps.owasp.api_client import CHAPTERS_URL, PROJECTS_URL, OwaspApiClient


def page(projects, *, status_code=HTTPStatus.OK, headers=None):
    """Build a mocked catalog response."""
    payload = mock.Mock()
    payload.status_code = status_code
    payload.headers = headers or {}
    payload.json.return_value = {"projects": projects}
    return payload


class TestOwaspApiClient:
    @mock.patch("apps.owasp.api_client.requests.get")
    def test_list_projects_returns_one_short_page(self, mock_get):
        """Test a short page is the whole catalog."""
        mock_get.return_value = page([{"slug": "nest"}])

        records = OwaspApiClient(page_limit=2).list_projects()

        assert records == [{"slug": "nest"}]
        mock_get.assert_called_once_with(
            PROJECTS_URL,
            params={"limit": 2, "offset": 0},
            timeout=(5, 30),
        )

    @mock.patch("apps.owasp.api_client.requests.get")
    def test_list_projects_follows_pages(self, mock_get):
        """Test a full page is followed by the next offset."""
        mock_get.side_effect = [
            page([{"slug": "one"}, {"slug": "two"}]),
            page([{"slug": "three"}]),
        ]

        records = OwaspApiClient(page_limit=2).list_projects()

        assert records == [{"slug": "one"}, {"slug": "two"}, {"slug": "three"}]
        assert mock_get.call_args_list[1].kwargs["params"] == {"limit": 2, "offset": 2}

    @mock.patch("apps.owasp.api_client.requests.get")
    def test_list_projects_returns_none_when_a_page_repeats(self, mock_get):
        """Test a repeated full page is a failed read."""
        repeated = page([{"slug": "one"}, {"slug": "two"}])
        mock_get.side_effect = [repeated, repeated]

        assert OwaspApiClient(page_limit=2).list_projects() is None
        assert mock_get.call_count == 2

    @mock.patch("apps.owasp.api_client.requests.get")
    def test_list_projects_returns_none_when_the_page_limit_is_exceeded(self, mock_get):
        """Test a catalog that never ends is a failed read."""
        mock_get.side_effect = [
            page([{"slug": "one"}]),
            page([{"slug": "two"}]),
        ]

        assert OwaspApiClient(max_pages=2, page_limit=1).list_projects() is None

    @mock.patch("apps.owasp.api_client.requests.get")
    def test_list_chapters_reads_the_chapters_collection(self, mock_get):
        """Test the chapter catalog uses the chapters endpoint and field."""
        response = page([{"slug": "london"}])
        response.json.return_value = {"chapters": [{"slug": "london"}]}
        mock_get.return_value = response

        records = OwaspApiClient().list_chapters()

        assert records == [{"slug": "london"}]
        assert mock_get.call_args.args[0] == CHAPTERS_URL

    @mock.patch("apps.owasp.api_client.time.sleep")
    @mock.patch("apps.owasp.api_client.requests.get")
    def test_list_projects_retries_rate_limit(self, mock_get, mock_sleep):
        """Test a 429 is retried once using Retry-After."""
        mock_get.side_effect = [
            page([], status_code=HTTPStatus.TOO_MANY_REQUESTS, headers={"Retry-After": "2"}),
            page([{"slug": "nest"}]),
        ]

        records = OwaspApiClient().list_projects()

        assert records == [{"slug": "nest"}]
        mock_sleep.assert_called_once_with(2)

    @pytest.mark.parametrize(
        "payload",
        [
            requests.exceptions.RequestException("offline"),
            page([], status_code=HTTPStatus.INTERNAL_SERVER_ERROR),
        ],
    )
    @mock.patch("apps.owasp.api_client.requests.get")
    def test_list_projects_returns_none_when_a_page_fails(self, mock_get, payload):
        """Test a failed page is not an empty catalog."""
        mock_get.side_effect = [
            page([{"slug": "nest"}]),
            payload,
        ]

        assert OwaspApiClient(page_limit=1).list_projects() is None

    @mock.patch("apps.owasp.api_client.requests.get")
    def test_list_projects_returns_none_for_invalid_json(self, mock_get):
        """Test a non-JSON body is a failed read."""
        response = page([])
        response.json.side_effect = ValueError("not json")
        mock_get.return_value = response

        assert OwaspApiClient().list_projects() is None

    @mock.patch("apps.owasp.api_client.requests.get")
    def test_list_projects_returns_none_when_collection_is_not_a_list(self, mock_get):
        """Test a collection that is not a list is a failed read."""
        response = page([])
        response.json.return_value = {"projects": {"slug": "nest"}}
        mock_get.return_value = response

        assert OwaspApiClient().list_projects() is None

    @mock.patch("apps.owasp.api_client.requests.get")
    def test_list_projects_returns_an_empty_catalog(self, mock_get):
        """Test an empty collection is an empty catalog."""
        mock_get.return_value = page([])

        assert OwaspApiClient().list_projects() == []

    @pytest.mark.parametrize("item", ["london", None])
    @mock.patch("apps.owasp.api_client.requests.get")
    def test_list_projects_returns_none_when_an_item_is_not_a_dict(self, mock_get, item):
        """Test a page item that is not an object is a failed read."""
        response = page([])
        response.json.return_value = {"projects": [{"slug": "nest"}, item]}
        mock_get.return_value = response

        assert OwaspApiClient().list_projects() is None

    @mock.patch("apps.owasp.api_client.requests.get")
    def test_list_projects_returns_none_when_the_collection_is_missing(self, mock_get):
        """Test a body without the collection field is a failed read."""
        response = page([])
        response.json.return_value = {}
        mock_get.return_value = response

        assert OwaspApiClient().list_projects() is None
