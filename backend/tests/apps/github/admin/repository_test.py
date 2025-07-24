from unittest.mock import MagicMock

import pytest
from django.contrib.admin.sites import AdminSite

from apps.github.admin.repository import RepositoryAdmin
from apps.github.models.repository import Repository


@pytest.fixture
def repository_admin_instance():
    return RepositoryAdmin(model=Repository, admin_site=AdminSite())


def test_custom_field_title_unit(repository_admin_instance):
    mock_repository = MagicMock()
    mock_repository.owner.login = "mock-owner"
    mock_repository.name = "mock-repo"

    result = repository_admin_instance.custom_field_title(mock_repository)

    assert result == "mock-owner/mock-repo"


def test_custom_field_github_url_unit(repository_admin_instance):
    mock_repository = MagicMock()
    mock_repository.owner.login = "mock-owner"
    mock_repository.name = "mock-repo"

    result = repository_admin_instance.custom_field_github_url(mock_repository)

    expected_html = "<a href='https://github.com/mock-owner/mock-repo' target='_blank'>↗️</a>"
    assert result == expected_html


def test_list_display_contains_custom_fields(repository_admin_instance):
    admin_list_display = repository_admin_instance.list_display
    assert "custom_field_title" in admin_list_display
    assert "custom_field_github_url" in admin_list_display
