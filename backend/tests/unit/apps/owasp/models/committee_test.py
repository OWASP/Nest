from unittest.mock import Mock, patch

import pytest

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
        with patch.object(Committee.objects, "filter") as mock_filter:
            mock_filter.return_value.count.return_value = value
            count = Committee.active_committees_count()
            assert count == value
            mock_filter.assert_called_once_with(has_active_repositories=True)

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

        with patch(
            "apps.owasp.models.committee.RepositoryBasedEntityModel.from_github"
        ) as mock_from_github:
            mock_from_github.side_effect = lambda instance, _: setattr(
                instance, "name", owasp_repository.title
            )
            committee.from_github(owasp_repository)

        mock_from_github.assert_called_once_with(
            committee,
            {
                "description": "pitch",
                "name": "title",
                "tags": "tags",
            },
        )

        assert committee.created_at == owasp_repository.created_at
        assert committee.name == owasp_repository.title
        assert committee.updated_at == owasp_repository.updated_at

    def test_nest_key(self):
        """Test nest_key property strips www-committee- prefix."""
        committee = Committee(key="www-committee-chapter")
        assert committee.nest_key == "chapter"

    def test_nest_key_complex(self):
        """Test nest_key with multi-word key."""
        committee = Committee(key="www-committee-web-security")
        assert committee.nest_key == "web-security"

    def test_update_data_creates_new(self):
        """Test update_data creates new committee when not found."""
        mock_gh_repository = Mock()
        mock_gh_repository.name = "www-committee-test"

        mock_repository = Mock()

        with patch.object(Committee, "objects") as mock_manager:
            mock_manager.get.side_effect = Committee.DoesNotExist

            with (
                patch.object(Committee, "from_github") as mock_from_github,
                patch.object(Committee, "save") as mock_save,
            ):
                result = Committee.update_data(mock_gh_repository, mock_repository, save=True)

                mock_manager.get.assert_called_once_with(key="www-committee-test")
                mock_from_github.assert_called_once_with(mock_repository)
                mock_save.assert_called_once()
                assert isinstance(result, Committee)

    def test_update_data_updates_existing(self):
        """Test update_data updates existing committee."""
        mock_gh_repository = Mock()
        mock_gh_repository.name = "www-committee-existing"

        mock_repository = Mock()
        existing_committee = Mock(spec=Committee)

        with patch.object(Committee, "objects") as mock_manager:
            mock_manager.get.return_value = existing_committee

            result = Committee.update_data(mock_gh_repository, mock_repository, save=False)

            mock_manager.get.assert_called_once_with(key="www-committee-existing")
            existing_committee.from_github.assert_called_once_with(mock_repository)
            existing_committee.save.assert_not_called()
            assert result == existing_committee

    def test_update_data_with_save_false(self):
        """Test update_data does not save when save=False."""
        mock_gh_repository = Mock()
        mock_gh_repository.name = "www-committee-nosave"

        mock_repository = Mock()

        with patch.object(Committee, "objects") as mock_manager:
            mock_manager.get.side_effect = Committee.DoesNotExist

            with (
                patch.object(Committee, "from_github"),
                patch.object(Committee, "save") as mock_save,
            ):
                Committee.update_data(mock_gh_repository, mock_repository, save=False)

                mock_save.assert_not_called()
