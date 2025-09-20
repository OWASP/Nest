from unittest.mock import Mock, patch

import pytest

from apps.common.index import IndexBase
from apps.github.models.repository import Repository
from apps.github.models.user import User
from apps.owasp.models.committee import Committee


class TestCommitteeModel:
    @pytest.mark.parametrize(
        ("name", "expected_str"),
        [
            ("Test Committee", "Test Committee"),
            ("", ""),
        ],
    )
    def test_str_representation(self, name, expected_str):
        committee = Committee(name=name)
        assert str(committee) == expected_str

    @pytest.mark.parametrize(
        ("value"),
        [
            23,
        ],
    )
    def test_active_committees_count(self, value):
        with patch.object(IndexBase, "get_total_count", return_value=value) as mock_count:
            count = Committee.active_committees_count()
            assert count == value
            mock_count.assert_called_once_with("committees")

    @pytest.mark.parametrize(
        ("summary"),
        [
            "A summary",
            "",
            None,
        ],
    )
    def test_save_method(self, summary):
        committee = Committee()
        committee.generate_summary = Mock()
        committee.summary = summary

        with (
            patch(
                "apps.core.models.prompt.Prompt.get_owasp_committee_summary",
                return_value="Test Prompt",
            ) as mock_prompt,
            patch("apps.owasp.models.committee.BulkSaveModel.save"),
        ):
            committee.save()

        if summary:
            committee.generate_summary.assert_not_called()
        else:
            committee.generate_summary.assert_called_once_with(prompt="Test Prompt")
            mock_prompt.assert_called_once()

    def test_bulk_save(self):
        mock_committees = [Mock(id=None), Mock(id=1)]
        with patch("apps.owasp.models.committee.BulkSaveModel.bulk_save") as mock_bulk_save:
            Committee.bulk_save(mock_committees, fields=["name"])
            mock_bulk_save.assert_called_once_with(Committee, mock_committees, fields=["name"])

    def test_from_github(self):
        owasp_repository = Repository()
        owasp_repository.name = "Test Repo"
        owasp_repository.created_at = "2024-01-01"
        owasp_repository.updated_at = "2024-12-24"
        owasp_repository.title = "Project Committee"
        owasp_repository.pitch = "Nest Pitch"
        owasp_repository.tags = ["react", "python"]
        owasp_repository.owner = User(name="OWASP")

        committee = Committee()
        committee.owasp_repository = owasp_repository

        with (
            patch(
                "apps.owasp.models.committee.RepositoryBasedEntityModel.from_github"
            ) as mock_from_github,
            patch("apps.github.auth.Github") as mock_github,
        ):
            mock_from_github.side_effect = lambda instance, _, __: setattr(
                instance, "name", owasp_repository.title
            )
            committee.from_github(owasp_repository, mock_github)

        mock_from_github.assert_called_once_with(
            committee,
            {
                "description": "pitch",
                "name": "title",
                "tags": "tags",
            },
            mock_github,
        )

        assert committee.created_at == owasp_repository.created_at
        assert committee.name == owasp_repository.title
        assert committee.updated_at == owasp_repository.updated_at
